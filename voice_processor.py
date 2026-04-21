import asyncio
import logging
import os
import re

import torch
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger("peterbot.voice")

RVC_CLI = os.environ.get("RVC_CLI_BIN", "rvc-cli")
MODELS_DIR = os.environ.get("MODELS_DIR", "models")

PITCH_MAP = {"PETER": -5, "STEWIE": 12}
SPEAKER_MAP = {"PETER": "en_1", "STEWIE": "en_2"}

os.makedirs("assets", exist_ok=True)

device = torch.device("cpu")
model_tts, _ = torch.hub.load(
    repo_or_dir="snakers4/silero-models",
    model="silero_tts",
    language="en",
    speaker="v3_en",
    trust_repo=True,
)
model_tts.to(device)


def _clean_text(text):
    return re.sub(r"[^a-zA-Z0-9\s!?]", "", text).strip()


async def generate_voice(text, character, index):
    """Genera el audio final para una línea: TTS Silero → RVC local."""
    char = character.upper()
    text_clean = _clean_text(text)
    if not text_clean:
        log.warning("Línea vacía tras limpieza, saltando %s", index)
        return None

    temp_wav = os.path.join("assets", f"temp_{index}.wav")
    final_mp3 = os.path.join("assets", f"audio_{index}.mp3")

    speaker_id = SPEAKER_MAP.get(char, "en_1")
    try:
        model_tts.save_wav(
            text=text_clean,
            speaker=speaker_id,
            sample_rate=48000,
            audio_path=temp_wav,
        )
    except Exception as e:
        log.exception("❌ Silero falló para %s: %s", index, e)
        return None

    pth = os.path.join(MODELS_DIR, f"{char}.pth")
    index_file = os.path.join(MODELS_DIR, f"{char}.index")

    if not os.path.exists(pth):
        log.error("❌ Modelo RVC no encontrado: %s", pth)
        return None

    pitch_shift = PITCH_MAP.get(char, 0)

    args = [
        RVC_CLI, "infer",
        "--input", temp_wav,
        "--model", pth,
        "--index", index_file,
        "--output", final_mp3,
        "--device", "cpu",
        "--pitch", str(pitch_shift),
    ]

    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            log.error(
                "❌ rvc-cli falló (código %s) en %s: %s",
                proc.returncode,
                index,
                stderr.decode(errors="ignore")[:500],
            )
            return None
    except FileNotFoundError:
        log.error("❌ rvc-cli no está instalado o no está en el PATH (variable RVC_CLI_BIN)")
        return None
    finally:
        if os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
            except OSError:
                pass

    if not os.path.exists(final_mp3):
        log.error("❌ rvc-cli no produjo salida en %s", final_mp3)
        return None

    return final_mp3
