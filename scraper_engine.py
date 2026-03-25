from playwright.sync_api import sync_playwright


def capture_scene(url, output_path, mode="repo"):
    print(f"🌐 Navegando a {url} en modo '{mode}'...")

    with sync_playwright() as p:
        # Lanzamos Chrome invisible con resolución de móvil/vertical
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1080, "height": 1080})

        try:
            page.goto(url, wait_until="networkidle")  # Espera a que cargue todo

            if mode == "repo":
                # Forzamos el modo oscuro en GitHub
                page.emulate_media(color_scheme="dark")

                # Inyectamos JavaScript para borrar la barra lateral y cabecera
                # Así nos queda solo el código y el README limpio
                page.evaluate("""
                    document.querySelectorAll('.js-header-wrapper, .Layout-sidebar, .pagehead').forEach(el => el.style.display = 'none');
                """)

                # Tomamos foto solo del contenedor principal
                page.locator("#repo-content-pjax-container").screenshot(path=output_path)

            elif mode == "news":
                # Para Dev-Peter: Capturamos artículos de noticias o documentación
                page.emulate_media(color_scheme="dark")
                # Intenta capturar la etiqueta <article> que suelen usar los blogs
                page.locator("article").screenshot(path=output_path)

            print(f"📸 ¡Captura perfecta guardada en {output_path}!")

        except Exception as e:
            print(f"❌ Error al capturar: {e}")
        finally:
            browser.close()


if __name__ == "__main__":
    # Prueba gratuita sin coste:
    # capture_scene("https://github.com/Significant-Gravitas/AutoGPT", "assets/github_repo.png", mode="repo")
    print("Módulo Scraper listo.")