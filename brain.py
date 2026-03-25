import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def generate_script(account_type="Repo-Peter", retries=0):
    """Genera un guion viral y lo valida contra las normas de seguridad."""

    if retries >= 3:
        print("❌ ERROR: Límite de reintentos con la IA alcanzado. Abortando misión.")
        return None

    model = genai.GenerativeModel('gemini-pro')

    # Contexto según la cuenta
    if account_type == "Repo-Peter":
        contexto = "un repositorio de GitHub increíble y útil para programadores"
    else:
        contexto = "una noticia de última hora sobre Inteligencia Artificial o desarrollo"

    prompt = f"""
    Actúa como un guionista viral. Genera un guion de 15-20 segundos entre Peter Griffin y Brian Griffin.
    Tema: {contexto}.
    Peter está muy emocionado y Brian es el perro intelectual y escéptico.

    Debes devolver estrictamente un objeto JSON con esta estructura:
    {{
        "tema": "Título corto y clickbait",
        "url_objetivo": "URL real del repositorio o noticia",
        "descripcion_viral": "Título para el post con hashtags virales",
        "timeline": [
            [0.0, 4.0, "Peter", "Texto de Peter"],
            [4.0, 8.5, "Brian", "Texto de Brian"]
        ]
    }}
    Responde SOLO el JSON, sin bloques de código Markdown.
    """

    try:
        print(f"🧠 [IA] Generando guion para {account_type} (Intento {retries + 1})...")
        response = model.generate_content(prompt)

        # Limpiamos posibles restos de Markdown de la IA
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        script_data = json.loads(clean_text)

        # --- VALIDACIÓN DE SEGURIDAD (Filtro de baneo) ---
        print("🛡️ [IA] Verificando seguridad del contenido...")
        safety_prompt = f"¿Es este texto apto para monetizar en TikTok, Instagram y YouTube? Responde SOLO 'SI' o 'NO': {clean_text}"
        safety_check = model.generate_content(safety_prompt)

        if "SI" in safety_check.text.upper():
            print("✅ Contenido validado y seguro.")
            return script_data
        else:
            print("⚠️ Contenido marcado como sensible. Reintentando generación...")
            return generate_script(account_type, retries + 1)

    except Exception as e:
        print(f"❌ Error en Brain Engine: {e}")
        return generate_script(account_type, retries + 1)