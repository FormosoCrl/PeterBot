import os
import json
from dotenv import load_dotenv

# Cargamos las credenciales (cuando las tengas)
load_dotenv()


def load_video_metadata(json_path="output/current_script.json"):
    """ Lee el JSON del cerebro para poner títulos automáticos """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Estructura viral para el título
        title = f"¿Conocías {data['tema']}? 🤯 #tech #programming"
        description = f"Mira este repo: {data['url_objetivo']}\nHecho con #PeterBot"

        return title, description
    except:
        return "Increíble herramienta de IA 💻", "Suscríbete para más."


def upload_to_youtube(video_path, title, description):
    """ Lógica para YouTube Shorts """
    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    if not client_id:
        print("⏭️ Saltando YouTube: No hay credenciales en el .env")
        return

    print(f"▶️ Subiendo '{title}' a YouTube Shorts...")
    # Aquí irá la llamada a la API de Google con el archivo client_secrets.json


def upload_to_tiktok(video_path, title):
    """ Lógica para TikTok """
    session_id = os.getenv("TIKTOK_SESSION_ID")
    if not session_id:
        print("⏭️ Saltando TikTok: No hay Session ID en el .env")
        return

    print(f"🎵 Subiendo '{title}' a TikTok...")
    # Aquí usaremos un uploader basado en sesión o la API oficial


def distribute_video(video_path):
    """ Función que el main.py llamará al final """
    if not os.path.exists(video_path):
        print("❌ Error: El video no existe.")
        return

    title, description = load_video_metadata()

    # Ejecutamos las subidas
    upload_to_youtube(video_path, title, description)
    upload_to_tiktok(video_path, title)


if __name__ == "__main__":
    # Prueba rápida
    distribute_video("output/tiktok_final_1000eur.mp4")