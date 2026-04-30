import asyncio
import logging
import os
import re

import edge_tts
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger("peterbot.voice")

RVC_CLI = os.environ.get("RVC_CLI_BIN", "rvc-cli")
MODELS_DIR = os.environ.get("MODELS_DIR", "models")

# Microsoft Neural voices — base para RVC.
# Peter: voz masculina americana grave.
# Stewie: voz masculina británica con dicción clara.
VOICE_MAP = {
    "PETER": "en-US-ChristopherNeural",
    "STEWIE": "en-GB-RyanNeural",
}
PITCH_MAP = {"PETER": -5, "STEWIE": 12}

os.makedirs("assets", exist_ok=True)


def _clean_text(text):
    """Elimina caracteres no soportados por el TTS."""
    return re.sub(r"[^\w\s!?',\-]", "", text, flags=re.UNICODE).strip()


async def _edge_tts_to_wav(text: str, voice: str, out_wav: str) -> bool:
    """Genera WAV con edge-tts → convierte a WAV via ffmpeg."""
    tmp_mp3 = out_wav.replace(".wav", "_tts.mp3")
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(tmp_mp3)
    except Exception as e:
        log.exception("❌ edge-tts falló: %s", e)
        return False

    # Convertir MP3 → WAV 48kHz mono para que RVC lo ingiera bien
    try:
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-y", "-i", tmp_mp3,
            "-ar", "48000", "-ac", "1", out_wav,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.communicate()
        return proc.returncode == 0
    except FileNotFoundError:
        log.error("❌ ffmpeg no encontrado en PATH")
        return False
    finally:
        if os.path.exists(tmp_mp3):
            try:
                os.remove(tmp_mp3)
            except OSError:
                pass


async def generate_voice(text: str, character: str, index: str):
    """Genera el audio final para una línea: edge-tts → RVC local.

    Reemplaza Silero por Microsoft Neural TTS (edge-tts), que produce
    una prosodia mucho más natural como base para la conversión RVC.
    """
    char = character.upper()
    text_clean = _clean_text(text)
    if not text_clean:
        log.warning("Línea vacía tras limpieza, saltando %s", index)
        return None

    voice = VOICE_MAP.get(char, "en-US-ChristopherNeural")
    temp_wav = os.path.join("assets", f"temp_{index}.wav")
    final_mp3 = os.path.join("assets", f"audio_{index}.mp3")

    log.info("🗣️ edge-tts [%s / %s] → %s", char, voice, index)
    ok = await _edge_tts_to_wav(text_clean, voice, temp_wav)
    if not ok or not os.path.exists(temp_wav):
        log.error("❌ edge-tts no generó audio para %s", index)
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
        log.error("❌ rvc-cli no está instalado o no está en el PATH")
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

    log.info("✅ Audio generado: %s", final_mp3)
    return final_mp3
