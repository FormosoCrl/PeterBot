import os, time, re, json, requests
from google import genai
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def get_trending_repo():
    """Obtiene el repositorio número 1 en tendencias de GitHub."""
    try:
        url = "https://github.com/trending"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        repo = soup.select_one('article.Box-row')

        # Extraemos nombre, descripción y estrellas
        title = repo.select_one('h2 a').text.replace('\n', '').replace(' ', '')
        desc = repo.select_one('p').text.strip() if repo.select_one('p') else "A mysterious coding project"
        stars = repo.select_one('a[href$="/stargazers"]').text.strip()

        return {"name": title, "desc": desc, "stars": stars}
    except Exception:
        # Fallback por si GitHub bloquea la petición
        return {"name": "AutoPeter-Bot", "desc": "The ultimate viral video creator", "stars": "99k"}


def generate_script(account_type="Repo-Peter", retries=5):
    repo_info = get_trending_repo()

    prompt = f"""
    Act as a Senior Family Guy Scriptwriter. 
    TOPIC: The real GitHub repository '{repo_info['name']}'.
    REPO CONTEXT: {repo_info['desc']} with {repo_info['stars']} stars.

    RULES:
    1. Characters: ONLY 'Peter' and 'Stewie'.
    2. Peter: He thinks '{repo_info['name']}' is something stupid like a new type of beer or a sandwich maker.
    3. Stewie: He is condescending, insults Peter's weight, and explains why the repo is actually genius.
    4. ENERGY: Extremely fast-paced.
    5. LENGTH: The dialogue MUST have at least 15 back-and-forth lines. Make it long and argumentative.
    5. PUNCTUATION: Use ONLY ONE (!) or (?) per dialogue. 
    6. PLACEMENT: These marks MUST be ONLY at the very end of each phrase.
    7. FORBIDDEN: No periods (.), no commas (,), no ellipses (...). No internal punctuation.

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
    """

    for attempt in range(retries):
        try:
            print(f"🧠 [IA] Contexto real: {repo_info['name']} (Intento {attempt + 1}/{retries})...")
            response = client.models.generate_content(model='gemini-3-flash-preview', contents=prompt)

            clean_json = re.sub(r'```json|```', '', response.text).strip()
            data = json.loads(clean_json)

            if data.get("seguridad") == "APTO":
                # Limpieza forzada por si la IA se salta las reglas
                for line in data["timeline"]:
                    line[3] = line[3].replace(".", "").replace(",", "").replace("...", "")
                return data

        except Exception as e:
            if "503" in str(e) or "429" in str(e):
                time.sleep(15)
            else:
                print(f"❌ Error en Brain: {e}")
                return None
    return None


if __name__ == "__main__":
    guion = generate_script()
    if guion:
        with open("guion_test.json", "w", encoding="utf-8") as f:
            json.dump(guion, f, indent=4, ensure_ascii=False)
        print(f"✅ Guion sobre {guion['tema']} guardado.")