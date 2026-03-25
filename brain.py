import json
import os


def generate_mock_script():
    """Simula la respuesta que nos daría la IA de texto gratis"""

    # Esta es la estructura exacta que la IA real nos devolverá en el futuro
    script_data = {
        "tema": "Auto-GPT (GitHub)",
        "cuenta_destino": "Repo-Peter",
        "url_objetivo": "https://github.com/Significant-Gravitas/AutoGPT",
        "duracion_estimada": 12.0,
        "timeline": [
            # Formato: (Inicio_seg, Fin_seg, Personaje, Texto para Subtítulo)
            (0.0, 4.0, "Peter", "¡Holy crap Brian! Tienes que ver este repositorio de GitHub."),
            (4.0, 8.5, "Brian", "¿Otra herramienta de IA que promete hacerte rico sin trabajar?"),
            (8.5, 12.0, "Peter", "¡Exacto! Esta escribe el código por ti. Adiós a teclear.")
        ]
    }

    # Guardamos esto como un archivo JSON que los otros scripts leerán
    os.makedirs("output", exist_ok=True)
    with open("output/current_script.json", "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=4, ensure_ascii=False)

    print("🧠 Guion generado y estructurado en JSON.")
    return script_data


if __name__ == "__main__":
    generate_mock_script()