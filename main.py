import asyncio
import json
import logging
import os
import random
from datetime import datetime, timedelta

from dotenv import load_dotenv

from brain import generate_script
from subtitle_engine import add_subtitles
from uploader import distribute_video
from video_editor import create_minecraft_video
from voice_processor import generate_voice

load_dotenv()

TASKS_FILE = "output/pending_tasks.json"
STATE_FILE = "output/state.json"
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() in ("1", "true", "yes")
PRODUCE_HOUR = int(os.environ.get("PRODUCE_HOUR", "22"))

ACCOUNTS = ["Repo-Peter", "Dev-Peter"]
SLOTS = {"AM": 8, "PM": 20}

os.makedirs("output", exist_ok=True)
os.makedirs("assets", exist_ok=True)
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/peterbot.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("peterbot")


def _read_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        log.warning("No se pudo leer %s: %s. Usando valor por defecto.", path, e)
        return default


def _write_json(path, data):
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    os.replace(tmp, path)


def load_tasks():
    return _read_json(TASKS_FILE, [])


def save_tasks(tasks):
    _write_json(TASKS_FILE, tasks)


def load_state():
    return _read_json(STATE_FILE, {"last_produced_date": None, "covered_repos": []})


def save_state(state):
    _write_json(STATE_FILE, state)


async def produce_daily_batch():
    log.info("🌙 Iniciando producción masiva para mañana...")
    tasks = []
    state = load_state()

    for acc in ACCOUNTS:
        for slot, hora in SLOTS.items():
            log.info("🎬 Fabricando contenido para: %s (%s)", acc, slot)
            script = generate_script(acc, exclude=state.get("covered_repos", []))
            if not script:
                log.warning("⚠️ Guion no disponible para %s %s. Saltando.", acc, slot)
                continue

            for i, line in enumerate(script["timeline"]):
                await generate_voice(line[3], line[2], f"{acc}_{slot}_{i}")

            video_base = f"output/base_{acc}_{slot}.mp4"
            video_final = f"output/FINAL_{acc}_{slot}.mp4"
            create_minecraft_video(
                script,
                "assets/minecraft_parkour.mp4",
                video_base,
                audio_prefix=f"{acc}_{slot}",
            )

            try:
                add_subtitles(video_base, video_final)
                if os.path.exists(video_base):
                    os.remove(video_base)
            except Exception as e:
                log.exception("⚠️ Error en subtítulos: %s. Usando video base.", e)
                if os.path.exists(video_base):
                    os.rename(video_base, video_final)

            pub_time = (datetime.now() + timedelta(days=1)).replace(
                hour=hora, minute=30, second=0, microsecond=0
            )
            pub_time += timedelta(minutes=random.randint(0, 45))

            tasks.append({
                "time": pub_time.isoformat(),
                "path": video_final,
                "title": script["tema"],
                "desc": script["descripcion_viral"],
                "account": acc,
            })

            repo_name = script.get("tema", "").split(" ")[0]
            if repo_name and repo_name not in state["covered_repos"]:
                state["covered_repos"].append(repo_name)
                state["covered_repos"] = state["covered_repos"][-50:]

    state["last_produced_date"] = datetime.now().date().isoformat()
    save_state(state)
    save_tasks(tasks)
    log.info("✅ Producción nocturna finalizada. %d videos listos.", len(tasks))


def _should_produce(now, state, tasks):
    if tasks:
        return False
    if now.hour < PRODUCE_HOUR:
        return False
    today = now.date().isoformat()
    return state.get("last_produced_date") != today


async def _publish_due_task(tasks):
    tasks.sort(key=lambda x: x["time"])
    proxima = tasks[0]
    target_time = datetime.fromisoformat(proxima["time"])

    if datetime.now() < target_time:
        return tasks

    account = proxima.get("account", ACCOUNTS[0])
    if DRY_RUN:
        log.info("🛡️ DRY_RUN activo — saltando publicación real de %s", proxima["path"])
    else:
        log.info("🚀 Publicando %s (cuenta %s)", proxima["path"], account)
        try:
            distribute_video(proxima["path"], proxima["title"], proxima["desc"], account)
        except Exception as e:
            log.exception("❌ Error publicando %s: %s", proxima["path"], e)
            return tasks

    if os.path.exists(proxima["path"]):
        os.remove(proxima["path"])
    tasks.pop(0)
    save_tasks(tasks)
    return tasks


async def main_loop():
    log.info("🤖 PeterBot Manager activado (DRY_RUN=%s, PRODUCE_HOUR=%d)", DRY_RUN, PRODUCE_HOUR)

    while True:
        try:
            now = datetime.now()
            tasks = load_tasks()
            state = load_state()

            if _should_produce(now, state, tasks):
                await produce_daily_batch()
                tasks = load_tasks()

            if tasks:
                await _publish_due_task(tasks)

        except Exception as e:
            log.exception("💥 Error en bucle principal: %s", e)

        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main_loop())
