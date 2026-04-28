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

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def get_trending_repos(limit=10):
    """Devuelve una lista de repos trending (nombre, descripción, estrellas)."""
    try:
        response = requests.get(
            "https://github.com/trending",
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 PeterBot"},
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.select("article.Box-row")[:limit]
        repos = []
        for repo in articles:
            title_el = repo.select_one("h2 a")
            desc_el = repo.select_one("p")
            stars_el = repo.select_one('a[href$="/stargazers"]')
            if not title_el:
                continue
            title = title_el.text.replace("\n", "").replace(" ", "")
            desc = desc_el.text.strip() if desc_el else "A mysterious coding project"
            stars = stars_el.text.strip() if stars_el else "?"
            repos.append({"name": title, "desc": desc, "stars": stars})
        return repos
    except Exception as e:
        log.warning("Fallo scraping GitHub Trending: %s. Usando fallback.", e)
        return [{"name": "AutoPeter-Bot", "desc": "The ultimate viral video creator", "stars": "99k"}]


def _pick_repo(exclude):
    exclude = set(exclude or [])
    repos = get_trending_repos()
    for repo in repos:
        if repo["name"] not in exclude:
            return repo
    return repos[0]


def _build_prompt(repo_info):
    return f"""
Act as a Senior Family Guy Scriptwriter.
TOPIC: The real GitHub repository '{repo_info['name']}'.
REPO CONTEXT: {repo_info['desc']} with {repo_info['stars']} stars.

RULES:
1. Characters: ONLY 'Peter' and 'Stewie'.
2. Peter: He thinks '{repo_info['name']}' is something stupid like a new type of beer or a sandwich maker.
3. Stewie: He is condescending, insults Peter's weight, and explains why the repo is actually genius.
4. ENERGY: Extremely fast-paced.
5. LENGTH: The dialogue MUST have between 10 and 12 back-and-forth lines.
6. PUNCTUATION: Use ONLY ONE (!) or (?) per dialogue.
7. PLACEMENT: These marks MUST be ONLY at the very end of each phrase.
8. FORBIDDEN: No periods (.), no commas (,), no ellipses (...). No internal punctuation.

STRICT JSON OUTPUT ONLY:
{{
    "seguridad": "APTO",
    "tema": "{repo_info['name']} is crazy",
    "url_objetivo": "https://github.com/{repo_info['name']}",
    "descripcion_viral": "Peter finds {repo_info['name']}",
    "timeline": [
        [0.0, 5.0, "Peter", "Dialogue text!"],
        [5.0, 10.0, "Stewie", "Dialogue text?"]
    ]
}}
""".strip()


def generate_script(account_type="Repo-Peter", retries=10, exclude=None):
    repo_info = _pick_repo(exclude)
    prompt = _build_prompt(repo_info)

    for attempt in range(retries):
        try:
            log.info(
                "🧠 [IA] Contexto: %s (intento %d/%d, cuenta %s)",
                repo_info["name"],
                attempt + 1,
                retries,
                account_type,
            )
            response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)

            clean_json = re.sub(r"```json|```", "", response.text).strip()
            data = json.loads(clean_json)

            if data.get("seguridad") == "APTO":
                for line in data["timeline"]:
                    line[3] = line[3].replace(".", "").replace(",", "").replace("...", "")
                return data
            log.warning("Guion marcado como no apto por la IA. Reintentando.")

        except Exception as e:
            msg = str(e)
            if "503" in msg or "429" in msg:
                wait = min(15 * (attempt + 1), 90)  # backoff: 15s, 30s, 45s... max 90s
                log.warning("Rate limit o sobrecarga Gemini: %s. Esperando %ds.", e, wait)
                time.sleep(wait)
            else:
                log.exception("❌ Error en Brain: %s", e)
                return None
    return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    guion = generate_script()
    if guion:
        with open("guion_test.json", "w", encoding="utf-8") as f:
            json.dump(guion, f, indent=4, ensure_ascii=False)
        print(f"✅ Guion sobre {guion['tema']} guardado.")
