import os
import time
import random
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

# Carpeta donde se guardarán tus cookies y sesión para no tener que loguearte siempre
USER_DATA_DIR = "./browser_session"


def human_delay(min_s=2, max_s=5):
    """Simula una espera humana aleatoria"""
    time.sleep(random.uniform(min_s, max_s))


def upload_to_tiktok(video_path, title):
    print(f"🎵 [TikTok] Iniciando subida para: {title}")

    with sync_playwright() as p:
        # Abrimos el navegador con tu sesión guardada
        context = p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=False,  # En el server usaremos modo 'headless' con truco, pero aquí para probar pon False
            viewport={'width': 1280, 'height': 720}
        )
        page = context.new_page()

        try:
            # 1. Ir a la página de carga
            page.goto("https://www.tiktok.com/creator-center/upload", wait_until="networkidle")
            human_delay(5, 8)

            # Verificar si estamos logueados
            if "login" in page.url:
                print("❌ ERROR: No hay sesión activa en TikTok. Loguéate manualmente primero.")
                return

            # 2. Subir el archivo (buscamos el input de tipo file)
            print("📤 Subiendo archivo...")
            page.set_input_files('input[type="file"]', video_path)
            human_delay(10, 15)  # Esperamos a que cargue el video

            # 3. Poner el título (Caption)
            # TikTok suele usar un div editable para el caption
            print("✍️ Escribiendo descripción...")
            page.locator('div[contenteditable="true"]').fill(title)
            human_delay(2, 4)

            # 4. DARLE AL BOTÓN PUBLICAR
            # print("🚀 Publicando...")
            # page.get_by_text("Post").click() # DESCOMENTAR CUANDO ESTÉS LISTO

            print("✅ Simulación de subida a TikTok completada.")

        except Exception as e:
            print(f"❌ Error en TikTok: {e}")
        finally:
            context.close()


def upload_to_youtube(video_path, title, description):
    print(f"▶️ [YouTube] Iniciando subida para: {title}")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(USER_DATA_DIR)
        page = context.new_page()

        try:
            page.goto("https://studio.youtube.com/", wait_until="networkidle")
            human_delay(5, 7)

            if "login" in page.url:
                print("❌ ERROR: No hay sesión activa en YouTube.")
                return

            # Lógica de clics en YouTube Studio
            page.locator("#upload-icon").click()
            human_delay()

            page.set_input_files('input[type="file"]', video_path)
            print("📤 Video enviado a YouTube...")
            human_delay(10, 20)

            # (Aquí iría la lógica de rellenar título y marcar 'No es para niños')
            print("✅ Simulación de subida a YouTube completada.")

        except Exception as e:
            print(f"❌ Error en YouTube: {e}")
        finally:
            context.close()


def distribute_video(video_path):
    """Llamada principal desde main.py"""
    # Sacamos el título de algún sitio o generamos uno genérico
    title = f"Review increíble de un repo de GitHub! #IA #Dev"

    # IMPORTANTE: No subir todo a la vez. Esperar un tiempo entre redes.
    upload_to_tiktok(video_path, title)
    human_delay(60, 120)  # Esperamos 2 minutos antes de ir a YouTube
    upload_to_youtube(video_path, title, "Descripción generada")


if __name__ == "__main__":
    # Prueba manual
    distribute_video("output/FINAL_Repo-Peter.mp4")