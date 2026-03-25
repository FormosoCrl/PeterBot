import os
import time
import random
from playwright.sync_api import sync_playwright

USER_DATA_DIR = "./browser_session"


def wait_random(min_s=3, max_s=7):
    time.sleep(random.uniform(min_s, max_s))


def upload_to_tiktok(page, video_path, title):
    print("🎵 [TikTok] Iniciando subida...")
    try:
        page.goto("https://www.tiktok.com/creator-center/upload")
        wait_random(5, 10)

        # Subir archivo
        file_input = page.locator('input[type="file"]')
        file_input.set_input_files(video_path)
        print("📤 TikTok: Video cargando...")
        wait_random(15, 25)

        # Título
        page.locator('div[contenteditable="true"]').fill(title)
        wait_random(5)

        # page.get_by_text("Post").click() # Activar cuando estés listo
        print("✅ TikTok: Proceso de subida terminado.")
    except Exception as e:
        print(f"❌ Error TikTok: {e}")


def upload_to_instagram(page, video_path, title):
    print("📸 [Instagram] Iniciando subida de Reel...")
    try:
        page.goto("https://www.instagram.com/")
        wait_random(5)

        # Botón Crear
        page.get_by_role("link", name="New post").click()
        wait_random()

        page.locator('input[type="file"]').set_input_files(video_path)
        wait_random(10)

        # Siguiente, Siguiente...
        page.get_by_text("Next").click();
        wait_random()
        page.get_by_text("Next").click();
        wait_random()

        # Descripción
        page.locator('div[aria-label="Write a caption..."]').fill(title)
        wait_random()

        # page.get_by_text("Share").click() # Activar para real
        print("✅ Instagram: Reel subido.")
    except Exception as e:
        print(f"❌ Error Instagram: {e}")


def distribute_video(video_path, title, description):
    """Función maestra que abre el navegador una vez y sube a todo."""
    with sync_playwright() as p:
        # Abrimos el navegador con tu sesión guardada
        context = p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=True  # Headless para el server
        )
        page = context.new_page()

        full_caption = f"{title} 🤯 #coding #ia #peterbot #griffin"

        upload_to_tiktok(page, video_path, full_caption)
        wait_random(60, 120)  # Pausa humana entre redes
        upload_to_instagram(page, video_path, full_caption)

        # Aquí podrías añadir YouTube Shorts de la misma forma

        context.close()