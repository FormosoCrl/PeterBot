import asyncio, os, json, time, random
from datetime import datetime, timedelta
from brain import generate_script
from voice_processor import generate_voice
from video_editor import create_minecraft_video
from subtitle_engine import add_subtitles
from uploader import distribute_video

TASKS_FILE = "output/pending_tasks.json"


def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)


def load_tasks():
    return json.load(open(TASKS_FILE)) if os.path.exists(TASKS_FILE) else []


async def produce_daily_batch():
    """Genera 4 vídeos (2 cuentas x 2 turnos) para el día siguiente."""
    print(f"🌙 {datetime.now()} - Iniciando producción masiva...")
    tasks = []
    # Cuentas configuradas en brain.py
    for acc in ["Repo-Peter", "Dev-Peter"]:
        for slot in ["AM", "PM"]:
            print(f"🎬 Fabricando: {acc} ({slot})")
            script = generate_script(acc)
            if not script: continue

            # 1. Doblaje RVC
            for i, line in enumerate(script["timeline"]):
                await generate_voice(line[3], line[2], f"{acc}_{slot}_{i}")

            # 2. Renderizado
            video_out = f"output/FINAL_{acc}_{slot}.mp4"
            create_minecraft_video(script, "assets/minecraft_parkour.mp4", video_out)

            # 3. Programación (Mañana a las 08:30 o 20:30 + extra)
            hora = 8 if slot == "AM" else 20
            pub_time = (datetime.now() + timedelta(days=1)).replace(hour=hora, minute=30)
            pub_time += timedelta(minutes=random.randint(0, 45))

            tasks.append({
                "time": pub_time.isoformat(),
                "path": video_out,
                "title": script["tema"],
                "desc": script["descripcion_viral"]
            })
    save_tasks(tasks)


async def main_loop():
    print("🤖 PeterBot Manager activado y vigilando...")
    while True:
        now = datetime.now()
        tasks = load_tasks()

        # Generar contenido a las 22:00 si no hay tareas
        if now.hour == 22 and now.minute == 0 and not tasks:
            await produce_daily_batch()

        # Revisar si toca publicar algo
        if tasks:
            tasks.sort(key=lambda x: x["time"])
            if now >= datetime.fromisoformat(tasks[0]["time"]):
                item = tasks.pop(0)
                print(f"🚀 Publicando: {item['path']}")
                distribute_video(item["path"], item["title"], item["desc"])
                save_tasks(tasks)

        await asyncio.sleep(60)  # Revisar cada minuto


if __name__ == "__main__":
    asyncio.run(main_loop())