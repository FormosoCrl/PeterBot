import os
from video_editor import create_minecraft_video

# 1. Simulamos un guion de 5 segundos
test_script = {
    "timeline": [
        [0.0, 5.0, "Peter", "Testing the rendering engine!"]
    ]
}

# 2. Verificamos que los archivos necesarios existen
assets_needed = ["assets/minecraft_parkour.mp4", "assets/peter.png", "assets/audio_0.mp3"]
missing = [f for f in assets_needed if not os.path.exists(f)]

if missing:
    print(f"❌ Faltan archivos en 'assets/': {missing}")
    print("Asegúrate de tener al menos el audio_0.mp3 que generaste antes.")
else:
    try:
        # Intentamos renderizar solo esos 5 segundos
        create_minecraft_video(
            test_script,
            "assets/minecraft_parkour.mp4",
            "output/test_quick.mp4"
        )
        print("\n✅ ¡BRUTAL! El renderizado ha funcionado perfectamente.")
        print("El error de 'ANTIALIAS' ha sido derrotado.")
    except Exception as e:
        print(f"\n❌ Error detectado durante el renderizado: {e}")