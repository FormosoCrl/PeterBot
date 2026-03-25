import os
from brain import generate_mock_script
from scraper_engine import capture_scene
from tts_engine import generate_dialogue_audio
from video_engine import create_split_screen_video
from subtitle_engine import transcribe_audio, add_viral_subtitles


def main():
    print("🚀 INICIANDO LA FÁBRICA AUTOMÁTICA DE PETER-BOT...")

    # Nos aseguramos de que las carpetas existan
    os.makedirs("assets", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # ==========================================
    # FASE 1: EL CEREBRO (Guion y Datos)
    # ==========================================
    print("\n--- FASE 1: PENSANDO ---")
    script_data = generate_mock_script()

    # ==========================================
    # FASE 2: EL OJO (Captura del Fondo)
    # ==========================================
    print("\n--- FASE 2: CAPTURANDO ESCENARIO ---")
    bg_path = "assets/github_repo.png"
    # Llamamos al bot invisible para que tome la foto de GitHub
    capture_scene(url=script_data["url_objetivo"], output_path=bg_path, mode="repo")

    # ==========================================
    # FASE 3: LA VOZ (Audio y Tiempos)
    # ==========================================
    print("\n--- FASE 3: GRABANDO VOCES ---")
    audio_path = "assets/audio_final.mp3"

    # Intentamos generar las voces reales
    real_timeline = generate_dialogue_audio(script_data, output_filepath=audio_path)

    # MODO PRUEBA: Si falla (porque no hay API KEY), usamos los tiempos del guion falso
    if not real_timeline:
        print("⚠️ Modo de prueba activado (Sin API de voz). Usando mapa de tiempos del guion base...")
        # Extraemos solo (inicio, fin, personaje) para el motor de video
        real_timeline = [(item[0], item[1], item[2]) for item in script_data["timeline"]]

    # ==========================================
    # FASE 4: EL DIRECTOR DE CÁMARAS (Video Base)
    # ==========================================
    print("\n--- FASE 4: ENSAMBLANDO VIDEO (Pantalla Dividida) ---")
    base_video_path = "output/video_sin_letras.mp4"

    create_split_screen_video(
        audio_path=audio_path,
        speaker_timeline=real_timeline,
        peter_path="assets/peter.png",
        brian_path="assets/brian.png",
        repo_bg_path=bg_path,
        gameplay_path="assets/minecraft_parkour.mp4",
        output_path=base_video_path
    )

    # ==========================================
    # FASE 5: EL EDITOR (Subtítulos Virales)
    # ==========================================
    print("\n--- FASE 5: QUEMANDO SUBTÍTULOS (Retención) ---")
    final_video_path = "output/tiktok_final_1000eur.mp4"

    # Whisper escucha el audio para sacar el tiempo exacto de cada palabra
    words_data = transcribe_audio(audio_path)
    # Pegamos las letras en el video base
    add_viral_subtitles(base_video_path, words_data, final_video_path)

    print(f"\n🎉 ¡PROCESO COMPLETADO EXITOSAMENTE! 🎉")
    print(f"📁 Tu video viral listo para publicar está en: {final_video_path}")


if __name__ == "__main__":
    main()