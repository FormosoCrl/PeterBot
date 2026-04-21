import os
from playwright.sync_api import sync_playwright

def create_super_session():
    # Crear carpeta principal si no existe
    if not os.path.exists('./browser_session'):
        os.makedirs('./browser_session')

    print("\n--- 🤖 GENERADOR DE SUPER-SESIÓN ---")
    nombre = input("🏷️ Introduce el nombre de la identidad (ej: repo_total o dev_total): ").strip()
    ruta = os.path.abspath(f'./browser_session/{nombre}')

    with sync_playwright() as p:
        # Lanzamos el navegador con una carpeta persistente
        context = p.chromium.launch_persistent_context(
            ruta,
            headless=False,
            channel="chrome",
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
        )

        # Lista de redes a configurar para esta identidad
        redes = [
            ("INSTAGRAM", "https://www.instagram.com/accounts/login/"),
            ("YOUTUBE", "https://accounts.google.com/ServiceLogin?service=youtube")
        ]

        for nombre_red, url in redes:
            print(f"\n🚀 Abriendo {nombre_red} en pestaña nueva...")
            page = context.new_page()
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                print(f"⚠️  Aviso de navegación (puedes ignorarlo si la página cargó): {e}")
            print(f"⚠️  LOGUÉATE en {nombre_red} (pon usuario, pass y código si hace falta).")
            print(f"✅ Una vez veas tu feed/muro de {nombre_red}, vuelve aquí.")
            input(f"👉 Pulsa ENTER cuando hayas terminado con {nombre_red} para seguir...")

        print(f"\n✨ ¡Sesión '{nombre}' completada con éxito!")
        print("🔒 Cerrando navegador para guardar archivos...")
        context.close()

if __name__ == "__main__":
    while True:
        create_super_session()
        if input("\n¿Quieres configurar la otra identidad? (s/n): ").lower() != 's':
            print("👋 Proceso finalizado. Ahora sube la carpeta 'browser_session' al server.")
            break