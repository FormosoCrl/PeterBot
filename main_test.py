import asyncio, os, json, time, random
from datetime import datetime, timedelta
from brain import generate_script
from voice_processor import generate_voice
from video_editor import create_minecraft_video
from subtitle_engine import add_subtitles
from uploader import distribute_video

TASKS_FILE = "output/pending_tasks.json"


def save_tasks(tasks):
    """Guarda la lista de videos pendientes de publicar."""
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)


def load_tasks():
    """Carga los videos programados del disco."""
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    return []


async def produce_daily_batch():
    """Genera 4 vídeos (2 cuentas x 2 turnos) para el día siguiente."""
    print(f"🌙 {datetime.now()} - Iniciando producción masiva para mañana...")
    tasks = []

    # Configuramos 2 tipos de cuenta y 2 franjas horarias
    for acc in ["Repo-Peter", "Dev-Peter"]:
        for slot in ["AM", "PM"]:
            print(f"🎬 Fabricando contenido para: {acc} ({slot})")
            script = generate_script(acc)  #
            if not script: continue

            # 1. Doblaje RVC (Diferenciando archivos para no solapar)
            for i, line in enumerate(script["timeline"]):
                await generate_voice(line[3], line[2], f"{acc}_{slot}_{i}")  #

            # 2. Renderizado del Video Base
            video_base = f"output/base_{acc}_{slot}.mp4"
            video_final = f"output/FINAL_{acc}_{slot}.mp4"
            create_minecraft_video(script, "assets/minecraft_parkour.mp4", video_base, audio_prefix=f"{acc}_{slot}")

            # 3. Añadir Subtítulos
            try:
                add_subtitles(video_base, video_final)
                os.remove(video_base)  # Borramos el base para ahorrar espacio
            except Exception as e:
                print(f"⚠️ Error en subtítulos: {e}. Usando video base.")
                os.rename(video_base, video_final)

            # 4. Programación (Mañana a las 08:30 o 20:30 + margen aleatorio)
            hora = 8 if slot == "AM" else 20
            pub_time = (datetime.now() + timedelta(days=1)).replace(hour=hora, minute=30, second=0)
            pub_time += timedelta(minutes=random.randint(0, 45))

            tasks.append({
                "time": pub_time.isoformat(),
                "path": video_final,
                "title": script["tema"],
                "desc": script["descripcion_viral"]
            })

    save_tasks(tasks)
    print("✅ Producción nocturna finalizada. 4 videos listos en la recámara.")


async def main_loop():
    """Bucle infinito que vigila la hora para generar o publicar."""
    print("🤖 PeterBot Manager activado y vigilando la red...")

    while True:
        now = datetime.now()
        tasks = load_tasks()

        # FASE 1: Generar contenido nuevo a las 22:00
        if now.hour == 22 and now.minute == 0 and not tasks:
            await produce_daily_batch()

        # FASE 2: Revisar si toca publicar algo
        if tasks:
            tasks.sort(key=lambda x: x["time"])
            proxima_tarea = tasks[0]
            target_time = datetime.fromisoformat(proxima_tarea["time"])

            if now >= target_time:
                # 🛡️ PAUSA DE SEGURIDAD (Confirmación manual para el primer día)
                print(f"\n🔔 TAREA PENDIENTE: {proxima_tarea['path']}")
                input("Presiona ENTER para subir a Redes Sociales o CTRL+C para cancelar...")

                print(f"🚀 PUBLICANDO: {proxima_tarea['path']}")
                distribute_video(proxima_tarea["path"], proxima_tarea["title"], proxima_tarea["desc"])

                # Limpieza: Borrar video tras publicar y actualizar lista
                if os.path.exists(proxima_tarea["path"]):
                    os.remove(proxima_tarea["path"])

                tasks.pop(0)
                save_tasks(tasks)

        await asyncio.sleep(60)  # Esperar un minuto antes de la siguiente revisión


if __name__ == "__main__":
    # Aseguramos que existan las carpetas necesarias
    os.makedirs("output", exist_ok=True)
    os.makedirs("assets", exist_ok=True)
    # Bloqueado para test