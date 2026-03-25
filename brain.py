import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def generate_script(account_type="Repo-Peter"):
    """
    Usa Gemini para generar un guion basado en el tipo de cuenta.
    Incluye una segunda fase de revisión de seguridad.
    """
    model = genai.GenerativeModel('gemini-pro')

    # Definimos el contexto según la cuenta
    topic = "un repositorio de GitHub increible" if account_type == "Repo-Peter" else "una noticia de IA o dev de última hora"

    prompt = f"""
    Genera un guion de 15 segundos entre Peter Griffin y Brian Griffin hablando sobre {topic}.
    Peter está emocionado y Brian es escéptico.
    Devuelve SOLO un JSON con esta estructura:
    {{
        "tema": "Nombre",
        "url_objetivo": "URL",
        "timeline": [[inicio, fin, "Personaje", "Texto"]]
    }}
    """

    print(f"🧠 Generando guion para {account_type}...")
    response = model.generate_content(prompt)
    script_data = json.loads(response.text)

    # --- FASE DE SEGURIDAD (Compliance Check) ---
    print("🛡️ Verificando seguridad del contenido...")
    safety_prompt = f"¿Este texto es apto para TikTok y YouTube sin riesgo de baneo? Responde SOLO 'SI' o 'NO': {response.text}"
    safety_check = model.generate_content(safety_prompt)

    if "SI" in safety_check.text.upper():
        print("✅ Contenido seguro.")
        return script_data
    else:
        print("⚠️ Contenido sensible detectado. Reintentando...")
        return generate_script(account_type)  # Reintento automático