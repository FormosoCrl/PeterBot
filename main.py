import os
from brain import generate_script
from scraper_engine import capture_scene
from tts_engine import generate_dialogue_audio
from video_engine import create_split_screen_video
from subtitle_engine import transcribe_audio, add_viral_subtitles
from uploader import distribute_video

# Configuración de las cuentas que maneja la fábrica
ACCOUNTS = [
    {"name": "Repo-Peter", "mode": "repo"},
    {"name": "Dev-Peter", "mode": "news"}
]


def run_factory():
    print("🚀 INICIANDO LA FÁBRICA AUTOMÁTICA DE PETER-BOT (MODO SERVIDOR)...")

    # Asegurar directorios base
    os.makedirs("assets", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    for acc in ACCOUNTS:
        acc_name = acc["name"]
        print(f"\n" + "=" * 40)
        print(f"🎬 PROCESANDO: {acc_name}")
        print("=" * 40)

        # --- FASE 1: CEREBRO (IA Real + Seguridad) ---
        print("\n--- FASE 1: GENERANDO GUION SEGURO ---")
        script_data = generate_script(acc_name)

        # --- FASE 2: EL OJO (Captura dinámica) ---
        print("\n--- FASE 2: CAPTURANDO ESCENARIO ---")
        bg_path = f"assets/bg_{acc_name}.png"
        capture_scene(url=script_data["url_objetivo"], output_path=bg_path, mode=acc["mode"])

        # --- FASE 3: LA VOZ (TTS con ElevenLabs) ---
        print("\n--- FASE 3: GENERANDO AUDIO REAL ---")
        audio_path = f"assets/audio_{acc_name}.mp3"
        real_timeline = generate_dialogue_audio(script_data, output_filepath=audio_path)

        # Fallback si no hay API Key o falla el TTS
        if not real_timeline:
            print(f"⚠️ Fallo en TTS para {acc_name}. Usando timeline estimado del guion...")
            real_timeline = [(item[0], item[1], item[2]) for item in script_data["timeline"]]

        # --- FASE 4: ENSAMBLADO (Video Base) ---
        print("\n--- FASE 4: MONTANDO VIDEO BASE ---")
        base_video_path = f"output/base_{acc_name}.mp4"

        create_split_screen_video(
            audio_path=audio_path,
            speaker_timeline=real_timeline,
            peter_path="assets/peter.png",
            brian_path="assets/brian.png",
            repo_bg_path=bg_path,
            gameplay_path="assets/minecraft_parkour.mp4",
            output_path=base_video_path
        )

        # --- FASE 5: EDICIÓN (Subtítulos Virales) ---
        print("\n--- FASE 5: GENERANDO SUBTÍTULOS AUTOMÁTICOS ---")
        final_video_path = f"output/FINAL_{acc_name}.mp4"

        words_data = transcribe_audio(audio_path)
        add_viral_subtitles(base_video_path, words_data, final_video_path)

        # --- FASE 6: PUBLICACIÓN (Uploader) ---
        print(f"\n--- FASE 6: ENVIANDO A COLA DE PUBLICACIÓN ---")
        distribute_video(final_video_path)

        print(f"\n✅ PROCESO COMPLETADO PARA {acc_name}")
        print(f"📁 Video listo en: {final_video_path}")

    print("\n" + "=" * 40)
    print("🏁 RONDA DE PRODUCCIÓN FINALIZADA")
    print("=" * 40)


if __name__ == "__main__":
    run_factory()