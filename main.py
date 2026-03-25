import os
import time
import json
import random
from datetime import datetime, timedelta
from brain import generate_script
from scraper_engine import capture_scene
from tts_engine import generate_dialogue_audio
from video_engine import create_split_screen_video
from subtitle_engine import transcribe_audio, add_viral_subtitles
from uploader import distribute_video

# Archivo de persistencia por si el servidor se cae
TASKS_FILE = "output/pending_tasks.json"


def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)


def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    return []


def run_daily_cycle():
    os.makedirs("assets", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    tasks = load_tasks()

    # --- FASE DE PRODUCCIÓN (Si no hay tareas pendientes) ---
    if not tasks:
        print(f"🌅 {datetime.now()} - INICIANDO PRODUCCIÓN DIARIA (7:00 AM)")

        cuentas = [
            {"name": "Repo-Peter", "mode": "repo"},
            {"name": "Dev-Peter", "mode": "news"}
        ]

        for acc in cuentas:
            for slot in ["AM", "PM"]:
                video_id = f"{acc['name']}_{slot}"
                print(f"\n🎬 Creando contenido para: {video_id}")

                # 1. IA Guion
                script = generate_script(acc["name"])
                if not script: continue

                # 2. Scraper
                bg = f"assets/bg_{video_id}.png"
                capture_scene(script["url_objetivo"], bg, mode=acc["mode"])

                # 3. Audio y Timeline
                audio = f"assets/audio_{video_id}.mp3"
                timeline = generate_dialogue_audio(script, audio)

                # 4. Video Base
                base = f"output/base_{video_id}.mp4"
                create_split_screen_video(audio, timeline, "assets/peter.png", "assets/brian.png", bg,
                                          "assets/minecraft_parkour.mp4", base)

                # 5. Subtítulos
                final = f"output/FINAL_{video_id}.mp4"
                words = transcribe_audio(audio)
                add_viral_subtitles(base, words, final)

                # 6. Calcular Hora de Publicación Aleatoria
                hora_base = 8 if slot == "AM" else 20
                target_time = datetime.now().replace(hour=hora_base, minute=30, second=0) + timedelta(
                    minutes=random.randint(0, 60))

                tasks.append({
                    "time": target_time.isoformat(),
                    "video_path": final,
                    "title": script["tema"],
                    "description": script["descripcion_viral"],
                    "cleanup": [bg, audio, base, final]
                })

        save_tasks(tasks)
        print(f"✅ Producción terminada. {len(tasks)} videos en cola.")

    # --- FASE DE PUBLICACIÓN (Bucle de espera) ---
    while tasks:
        tasks = load_tasks()
        tasks.sort(key=lambda x: x["time"])

        proxima_tarea = tasks[0]
        target_dt = datetime.fromisoformat(proxima_tarea["time"])

        if datetime.now() >= target_dt:
            print(f"🚀 PUBLICANDO AHORA: {proxima_tarea['video_path']}")
            distribute_video(proxima_tarea["video_path"], proxima_tarea["title"], proxima_tarea["description"])

            # Limpiar archivos del video publicado
            for f in proxima_tarea["cleanup"]:
                if os.path.exists(f): os.remove(f)

            # Eliminar de la cola y guardar
            tasks.pop(0)
            save_tasks(tasks)
        else:
            # Dormir 1 minuto y volver a chequear
            print(f"⏳ Esperando... Próximo video a las {target_dt.strftime('%H:%M')}")
            time.sleep(60)


if __name__ == "__main__":
    run_daily_cycle()