import asyncio, os, json, shutil
from brain import generate_script
from voice_processor import generate_voice
from video_editor import create_minecraft_video
from subtitle_engine import add_subtitles


def cleanup_old_assets():
    """Borra solo los audios del video anterior para evitar conflictos."""
    print("🧹 Limpiando audios antiguos de la carpeta assets...")
    if not os.path.exists("assets"):
        os.makedirs("assets")
        return

    for file in os.listdir("assets"):
        # Solo borramos los audios temporales
        if file.startswith("audio_") and file.endswith(".mp3"):
            try:
                os.remove(os.path.join("assets", file))
            except Exception as e:
                print(f"⚠️ No se pudo borrar {file}: {e}")


async def main():
    # 1. Preparación y Limpieza
    cleanup_old_assets()
    os.makedirs("output", exist_ok=True)

    # 2. IA Guionista (Ahora busca tendencias reales de GitHub)
    script = generate_script("Repo-Peter")
    if not script:
        print("❌ Error: No se pudo generar el guion.")
        return

    # Guardamos el guion para tener un registro de qué se ha creado
    with open("assets/ultimo_guion.json", "w", encoding="utf-8") as f:
        json.dump(script, f, indent=4, ensure_ascii=False)

    # 3. Generación de Voces (Doblaje)
    print(f"🎙️ Iniciando doblaje para el repo: {script['tema']}")
    tasks = []
    for i, line in enumerate(script["timeline"]):
        print(f"💬 [{line[2]}] grabando: {line[3]}")
        # Generamos los audios uno a uno
        await generate_voice(line[3], line[2], i)

    # 4. Edición de Video (Montaje con parche de compatibilidad)
    # Usamos el archivo de parkour que ya tienes en assets
    create_minecraft_video(script, "assets/minecraft_parkour.mp4", "output/base.mp4")

    # 5. Subtítulos (Opcional si tienes ImageMagick configurado)
    try:
        add_subtitles("output/base.mp4", "output/FINAL.mp4")
        print(f"✅ ¡PROCESO COMPLETADO! Video final en: output/FINAL.mp4")
    except Exception as e:
        print(f"⚠️ Error en subtítulos, pero el video base está en output/base.mp4: {e}")


if __name__ == "__main__":
    asyncio.run(main())