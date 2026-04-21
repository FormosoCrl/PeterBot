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
            args=["--start-maximized"]
        )
        page = context.new_page()

        # Lista de redes a configurar para esta identidad
        redes = [
            ("TIKTOK", "https://www.tiktok.com/login"),
            ("INSTAGRAM", "https://www.instagram.com/accounts/login/"),
            ("YOUTUBE", "https://accounts.google.com/ServiceLogin?service=youtube")
        ]

        for nombre_red, url in redes:
            print(f"\n🚀 Abriendo {nombre_red}...")
            page.goto(url)
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