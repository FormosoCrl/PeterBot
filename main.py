import os
import time
import random
from datetime import datetime, timedelta
from brain import generate_script
from scraper_engine import capture_scene
from tts_engine import generate_dialogue_audio
from video_engine import create_split_screen_video
from subtitle_engine import transcribe_audio, add_viral_subtitles
from uploader import distribute_video

ACCOUNTS = [
    {"name": "Repo-Peter", "mode": "repo"},
    {"name": "Dev-Peter", "mode": "news"}
]

SLOTS = ["AM", "PM"]


def run_daily_cycle():
    print(f"🌅 {datetime.now().strftime('%H:%M:%S')} - INICIANDO CICLO DIARIO DE PRODUCCIÓN")

    tasks = []  # Lista para guardar (hora_publicacion, ruta_video, cuenta)

    # --- FASE 1: PRODUCCIÓN EN BLOQUE (7:00 AM) ---
    for acc in ACCOUNTS:
        for slot in SLOTS:
            video_id = f"{acc['name']}_{slot}"
            print(f"\n🎬 Fabricando video: {video_id}")

            # 1. Generar Guion
            script_data = generate_script(acc['name'])

            # 2. Captura de escenario
            bg_path = f"assets/bg_{video_id}.png"
            capture_scene(script_data["url_objetivo"], bg_path, mode=acc['mode'])

            # 3. Audio y Video
            audio_path = f"assets/audio_{video_id}.mp3"
            real_timeline = generate_dialogue_audio(script_data, audio_path)

            base_path = f"output/base_{video_id}.mp4"
            create_split_screen_video(audio_path, real_timeline, "assets/peter.png",
                                      "assets/brian.png", bg_path,
                                      "assets/minecraft_parkour.mp4", base_path)

            # 4. Subtítulos Finales
            final_path = f"output/FINAL_{video_id}.mp4"
            words = transcribe_audio(audio_path)
            add_viral_subtitles(base_path, words, final_path)

            # --- FASE 2: CÁLCULO DE HORARIO ALEATORIO ---
            # Definimos la ventana (8:30 AM a 9:30 AM para el bloque AM)
            # Definimos otra ventana para el bloque PM (ej. 20:30 a 21:30 para máxima retención)
            if slot == "AM":
                start_h, start_m = 8, 30
            else:
                start_h, start_m = 20, 30  # Asumimos tarde real para el video PM

            random_minutes = random.randint(0, 60)
            target_time = datetime.now().replace(hour=start_h, minute=start_m, second=0) + timedelta(
                minutes=random_minutes)

            tasks.append({
                "time": target_time,
                "path": final_path,
                "account": acc['name'],
                "temp_files": [bg_path, audio_path, base_path, final_path]
            })
            print(f"📅 Programado: {video_id} para las {target_time.strftime('%H:%M')}")

    # --- FASE 3: EL RELOJ DE PUBLICACIÓN ---
    # Ordenamos las tareas por hora
    tasks.sort(key=lambda x: x["time"])

    for task in tasks:
        # Esperar hasta la hora señalada
        while datetime.now() < task["time"]:
            time.sleep(30)  # Revisa cada 30 segundos

        print(f"🚀 {datetime.now().strftime('%H:%M')} - DISPARANDO PUBLICACIÓN: {task['path']}")
        distribute_video(task['path'])

        # --- FASE 4: LIMPIEZA TOTAL ---
        print(f"🧹 Limpiando archivos de {task['account']}...")
        for f in task["temp_files"]:
            if os.path.exists(f):
                os.remove(f)

    print("\n🏁 CICLO COMPLETADO. Todos los videos publicados y local limpio.")


if __name__ == "__main__":
    run_daily_cycle()