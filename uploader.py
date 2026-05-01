import logging
import os
import random
import time

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()
log = logging.getLogger("peterbot.uploader")

DEFAULT_SESSION_BASE = "./sessions"


def _session_dir(account_name):
    """Resuelve el directorio de sesión persistente para una cuenta dada.

    Busca primero `{ACCOUNT}_SESSION_DIR` en el entorno (ej. REPO_PETER_SESSION_DIR),
    y si no existe usa `./sessions/{account_slug}`.
    """
    env_key = f"{account_name.upper().replace('-', '_')}_SESSION_DIR"
    path = os.environ.get(env_key)
    if not path:
        slug = account_name.lower().replace("-", "_")
        path = os.path.join(DEFAULT_SESSION_BASE, slug)
    return os.path.abspath(path)


def wait_random(min_s=3, max_s=7):
    time.sleep(random.uniform(min_s, max_s))


def upload_to_tiktok(page, video_path, title):
    log.info("🎵 [TikTok] Iniciando subida...")
    try:
        page.goto("https://www.tiktok.com/creator-center/upload")
        wait_random(5, 10)

        file_input = page.locator('input[type="file"]')
        file_input.set_input_files(video_path)
        log.info("📤 TikTok: Video cargando...")
        wait_random(15, 25)

        page.locator('div[contenteditable="true"]').first.fill(title)
        wait_random(5)

        # ⚠️ Safety guard: el click de Post está deshabilitado hasta validar manualmente.
        # Activar sólo tras una primera ronda de pruebas end-to-end.
        # page.get_by_text("Post").click()
        log.info("✅ TikTok: Proceso de subida terminado (Post desactivado).")
    except Exception as e:
        log.exception("❌ Error TikTok: %s", e)


def upload_to_instagram(page, video_path, title):
    log.info("📸 [Instagram] Iniciando subida de Reel...")
    try:
        page.goto("https://www.instagram.com/")
        wait_random(5)

        page.get_by_role("link", name="New post").click()
        wait_random()

        page.locator('input[type="file"]').set_input_files(video_path)
        wait_random(10)

        page.get_by_text("Next").click()
        wait_random()
        page.get_by_text("Next").click()
        wait_random()

        page.locator('div[aria-label="Write a caption..."]').fill(title)
        wait_random()

        page.get_by_text("Share").click()
        wait_random(5, 10)
        log.info("✅ Instagram: Reel publicado.")
    except Exception as e:
        log.exception("❌ Error Instagram: %s", e)


def distribute_video(video_path, title, description, account_name):
    """Sube un video a las redes asociadas a `account_name` usando su sesión persistente."""
    session_dir = _session_dir(account_name)
    if not os.path.isdir(session_dir):
        log.error(
            "❌ No existe sesión persistente para %s en %s. Ejecuta get_session.py primero.",
            account_name,
            session_dir,
        )
        return

    log.info("🌐 Usando sesión %s → %s", account_name, session_dir)
    full_caption = f"{title} 🤯 #coding #ia #peterbot #griffin"

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            session_dir,
            headless=True,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            ignore_default_args=["--enable-automation"],
        )
        try:
            page = context.new_page()
            # TikTok deshabilitado: detecta logins automatizados incluso con Chrome real.
            # Reactivar cuando tengamos estrategia alternativa (perfil Chrome real, API creadores).
            upload_to_instagram(page, video_path, full_caption)
        finally:
            context.close()
