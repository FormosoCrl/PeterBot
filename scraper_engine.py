from playwright.sync_api import sync_playwright


def capture_scene(url, output_path, mode="repo"):
    print(f"🌐 [Scraper] Navegando a: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Simulamos un navegador de escritorio para la captura
        page = browser.new_page(viewport={"width": 1080, "height": 1080})

        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            page.emulate_media(color_scheme="dark")

            if mode == "repo":
                # Limpiamos la interfaz de GitHub para que solo se vea el código/README
                page.evaluate("""
                    document.querySelectorAll('.js-header-wrapper, .Layout-sidebar, .pagehead').forEach(el => el.style.display = 'none');
                """)
                # Capturamos el contenedor principal
                page.locator("#repo-content-pjax-container").screenshot(path=output_path)
            else:
                # En modo noticia, intentamos capturar el cuerpo del artículo
                page.locator("article").screenshot(path=output_path)

            print(f"📸 Captura guardada en: {output_path}")

        except Exception as e:
            print(f"❌ Error en Scraper: {e}")
            # Si falla el selector, tomamos una captura de toda la página como fallback
            page.screenshot(path=output_path)
        finally:
            browser.close()