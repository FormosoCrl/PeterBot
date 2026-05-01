import json
import logging
import os
import re
import time

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google import genai

load_dotenv()
log = logging.getLogger("peterbot.brain")

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PeterBot/1.0"}

# ---------------------------------------------------------------------------
# Guion de referencia — muestra a Gemini la calidad y longitud esperadas
# ---------------------------------------------------------------------------
EXAMPLE_SCRIPT = """
EXAMPLE OF THE QUALITY AND LENGTH EXPECTED (do NOT copy this, use it only as a reference):
[
  [0, 5, "Peter", "Lois, I just found this thing called Codex CLI and I think it writes code by itself!"],
  [5, 10, "Stewie", "Oh for the love of God, it is a command-line AI coding tool, not a magic pizza dispenser!"],
  [10, 16, "Peter", "But Stewie, it has forty-five thousand stars, and you have zero, because nobody likes you!"],
  [16, 22, "Stewie", "Those are GitHub stars, you blithering idiot, it means forty-five thousand developers use it daily!"],
  [22, 28, "Peter", "Wait, so I just tell it what I want and it writes the whole thing? That is literally what I thought coding was!"],
  [28, 34, "Stewie", "You can build entire applications from plain English, which is genuinely revolutionary, you magnificent fool!"],
  [34, 40, "Peter", "OK but what if I asked it to write a program that just orders pizza every Friday, would that work?"],
  [40, 46, "Stewie", "That is actually a perfectly valid use case and I hate that you accidentally said something intelligent!"],
  [46, 52, "Peter", "See, I told you, Stewie, thinking about food is basically the same as thinking about world domination!"],
  [52, 57, "Stewie", "I genuinely cannot tell if you are the luckiest or most infuriating creature alive, but here we are!"]
]
"""


# ---------------------------------------------------------------------------
# Scrapers — Repo-Peter
# ---------------------------------------------------------------------------

def get_trending_repos(limit=10):
    """GitHub Trending: repos con más estrellas hoy."""
    try:
        r = requests.get("https://github.com/trending", timeout=10, headers=HEADERS)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        articles = soup.select("article.Box-row")[:limit]
        repos = []
        for repo in articles:
            title_el = repo.select_one("h2 a")
            desc_el = repo.select_one("p")
            stars_el = repo.select_one('a[href$="/stargazers"]')
            if not title_el:
                continue
            name = title_el.text.replace("\n", "").replace(" ", "")
            desc = desc_el.text.strip() if desc_el else "A mysterious coding project"
            stars = stars_el.text.strip() if stars_el else "?"
            repos.append({"name": name, "desc": desc, "stars": stars})
        return repos
    except Exception as e:
        log.warning("Fallo scraping GitHub Trending: %s", e)
        return []


def get_repo_readme(repo_name: str, max_chars: int = 1200) -> str:
    """Descarga el README.md del repo para dar más contexto a Gemini."""
    try:
        # repo_name viene como "owner/repo" desde GitHub Trending
        api_url = f"https://api.github.com/repos/{repo_name}/readme"
        r = requests.get(api_url, timeout=8, headers=HEADERS)
        if r.status_code != 200:
            return ""
        import base64
        content = base64.b64decode(r.json().get("content", "")).decode("utf-8", errors="ignore")
        # Quitar markdown pesado (imágenes, badges, HTML)
        content = re.sub(r"!\[.*?\]\(.*?\)", "", content)
        content = re.sub(r"<[^>]+>", "", content)
        content = re.sub(r"\[.*?\]\(.*?\)", lambda m: m.group(0).split("]")[0].lstrip("["), content)
        content = re.sub(r"\n{3,}", "\n\n", content).strip()
        return content[:max_chars]
    except Exception as e:
        log.debug("No se pudo obtener README de %s: %s", repo_name, e)
        return ""


# ---------------------------------------------------------------------------
# Scrapers — Dev-Peter (Noticias IA)
# ---------------------------------------------------------------------------

def get_huggingface_papers(limit=5):
    """HuggingFace Daily Papers — los papers de IA más destacados del día."""
    try:
        r = requests.get("https://huggingface.co/papers", timeout=10, headers=HEADERS)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        papers = []
        for article in soup.select("article")[:limit]:
            title_el = article.select_one("h3") or article.select_one("h2")
            if not title_el:
                continue
            title = title_el.text.strip()
            # Votos/upvotes como proxy de popularidad
            votes_el = article.select_one('[class*="vote"]') or article.select_one("button")
            votes = votes_el.text.strip() if votes_el else "?"
            papers.append({"name": title, "desc": "Latest AI research paper", "stars": f"{votes} upvotes"})
        return papers
    except Exception as e:
        log.warning("Fallo scraping HuggingFace Papers: %s", e)
        return []


def get_hackernews_ai(limit=5):
    """Hacker News API — top stories con 'AI' o 'LLM' en el título."""
    try:
        r = requests.get(
            "https://hn.algolia.com/api/v1/search?query=AI+LLM+model&tags=story&hitsPerPage=20",
            timeout=8, headers=HEADERS
        )
        r.raise_for_status()
        hits = r.json().get("hits", [])
        results = []
        for h in hits:
            title = h.get("title", "")
            if not title:
                continue
            points = h.get("points", 0)
            url = h.get("url", "")
            results.append({"name": title[:80], "desc": url, "stars": f"{points} points"})
            if len(results) >= limit:
                break
        return results
    except Exception as e:
        log.warning("Fallo scraping Hacker News: %s", e)
        return []


# ---------------------------------------------------------------------------
# Selección de fuente según cuenta
# ---------------------------------------------------------------------------

def _pick_content(account_type: str, exclude: list):
    """Elige el tema más relevante para la cuenta dada."""
    exclude = set(exclude or [])

    if account_type == "Dev-Peter":
        # Fuente 1: HuggingFace Papers
        items = get_huggingface_papers()
        # Fuente 2: Hacker News como fallback
        if not items:
            items = get_hackernews_ai()
        # Fallback absoluto
        if not items:
            items = [{"name": "GPT-5", "desc": "OpenAI releases GPT-5 with unprecedented reasoning", "stars": "500k upvotes"}]
        for item in items:
            if item["name"] not in exclude:
                return item, "ai_news"
        return items[0], "ai_news"

    else:  # Repo-Peter (default)
        repos = get_trending_repos()
        if not repos:
            repos = [{"name": "microsoft/vscode", "desc": "The most popular code editor", "stars": "160k"}]
        for repo in repos:
            if repo["name"] not in exclude:
                # Enriquecer con README si es posible
                readme = get_repo_readme(repo["name"])
                if readme:
                    repo["readme"] = readme
                return repo, "github_repo"
        repo = repos[0]
        return repo, "github_repo"


# ---------------------------------------------------------------------------
# Construcción del prompt
# ---------------------------------------------------------------------------

def _build_prompt(content: dict, content_type: str) -> str:
    name = content["name"]
    desc = content["desc"]
    stars = content["stars"]
    readme_section = ""
    if content.get("readme"):
        readme_section = f"\nREPO README EXCERPT (use this for technical details):\n{content['readme']}\n"

    if content_type == "ai_news":
        topic_line = f"TOPIC: The real AI news story: '{name}'"
        context_line = f"CONTEXT: {desc} — {stars}"
        peter_mistake = f"Peter thinks '{name}' is a new type of kitchen appliance or a sports team"
        stewie_role = "Stewie is outraged because this is actually groundbreaking AI research that will change humanity"
        url_field = f'"url_objetivo": "https://huggingface.co/papers"'
    else:
        topic_line = f"TOPIC: The real GitHub repository '{name}'"
        context_line = f"CONTEXT: {desc} — {stars} GitHub stars"
        peter_mistake = f"Peter thinks '{name}' is something completely mundane like a food delivery service or a TV show"
        stewie_role = "Stewie explains with condescending fury why this repo is actually genius engineering"
        url_field = f'"url_objetivo": "https://github.com/{name}"'

    return f"""You are a Senior Family Guy Scriptwriter creating a viral short video script.

{topic_line}
{context_line}{readme_section}

CHARACTER RULES:
- Peter Griffin: Lovable idiot. {peter_mistake}. He asks absurd questions, makes wrong assumptions, but accidentally says smart things. He references food, beer, or TV constantly.
- Stewie Griffin: Evil genius baby. {stewie_role}. He is condescending, uses big words, insults Peter's intelligence and weight, but secretly respects his accidental insights.

SCRIPT QUALITY RULES:
1. LENGTH: Write EXACTLY 10 to 14 dialogue lines — this must fill 60 to 90 seconds of video. Be punchy, not exhaustive.
2. FLOW: Each line must naturally follow from the previous. No random topic jumps.
3. AUTHENTICITY: Include 1-2 real technical details from the context above so viewers learn something.
4. COMEDY: Peter's misunderstanding must escalate fast and pay off hard — every line must be funnier than the last.
5. ENDING: The last 2 lines must be a satisfying comedic payoff — Peter accidentally makes a brilliant point, Stewie is grudgingly impressed.
6. PUNCTUATION: Each line ends with EXACTLY ONE ! or ?. No periods, no ellipses. Use commas only where you would naturally pause mid-sentence when speaking aloud.
7. LANGUAGE: English only. Write exactly how these characters would actually say it out loud — casual, fast, with natural rhythm.

{EXAMPLE_SCRIPT}

OUTPUT: Strict JSON only, no markdown, no explanation:
{{
    "seguridad": "APTO",
    "tema": "{name} explained by Peter and Stewie",
    "descripcion_viral": "Peter and Stewie argue about {name} and it gets out of hand",
    {url_field},
    "timeline": [
        [0.0, 4.0, "Peter", "First line here!"],
        [4.0, 8.0, "Stewie", "Response here?"]
    ]
}}
""".strip()


# ---------------------------------------------------------------------------
# Generación principal
# ---------------------------------------------------------------------------

def generate_script(account_type="Repo-Peter", retries=10, exclude=None):
    content, content_type = _pick_content(account_type, exclude)
    prompt = _build_prompt(content, content_type)

    for attempt in range(retries):
        try:
            log.info(
                "🧠 [IA] Tema: '%s' | tipo: %s | cuenta: %s | intento %d/%d",
                content["name"], content_type, account_type, attempt + 1, retries,
            )
            response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
            clean_json = re.sub(r"```json|```", "", response.text).strip()
            data = json.loads(clean_json)

            if data.get("seguridad") != "APTO":
                log.warning("Guion marcado como no apto. Reintentando.")
                continue

            timeline = data.get("timeline", [])
            if len(timeline) < 8:
                log.warning("Guion demasiado corto (%d líneas). Reintentando.", len(timeline))
                continue

            # Limpiar solo puntuación que rompe el TTS; conservar comas (pausas naturales)
            for line in timeline:
                line[3] = line[3].replace("...", "").replace(";", ",")

            log.info("✅ Guion generado: %d líneas sobre '%s'", len(timeline), content["name"])
            return data

        except Exception as e:
            msg = str(e)
            if "503" in msg or "429" in msg:
                wait = min(15 * (attempt + 1), 90)
                log.warning("Rate limit Gemini: %s. Esperando %ds.", e, wait)
                time.sleep(wait)
            else:
                log.exception("❌ Error en Brain: %s", e)
                return None
    return None


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    acc = sys.argv[1] if len(sys.argv) > 1 else "Repo-Peter"
    guion = generate_script(account_type=acc)
    if guion:
        with open("guion_test.json", "w", encoding="utf-8") as f:
            json.dump(guion, f, indent=4, ensure_ascii=False)
        print(f"✅ Guion ({len(guion['timeline'])} líneas) sobre '{guion['tema']}' guardado.")
    else:
        print("❌ No se generó guion.")
