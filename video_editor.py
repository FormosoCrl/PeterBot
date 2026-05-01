import logging
import os

import PIL.Image
from moviepy.editor import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    VideoFileClip,
)

# Parche MoviePy 1.0.3 ↔ Pillow moderno: ANTIALIAS fue eliminado en Pillow 10.
if not hasattr(PIL.Image, "ANTIALIAS"):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

log = logging.getLogger("peterbot.video")

# Altura en píxeles a la que se renderiza cada personaje en el vídeo (1080×1920).
# Todos los PNG se reescalan a esta altura para que ocupen el mismo espacio visual
# independientemente de la relación de aspecto original del asset.
CHAR_HEIGHT = {"PETER": 1100, "STEWIE": 1100}
DEFAULT_CHAR_HEIGHT = 1000


def create_minecraft_video(script_data, bg_path, output_path, audio_prefix=""):
    """Compone el video base (1080x1920) sin subtítulos.

    Usa preset ultrafast porque este render es intermedio: subtitle_engine
    lo re-encodea después. El fichero resultante pesa más pero renderiza
    mucho más rápido en CPU.
    """
    if not os.path.exists(bg_path):
        log.error("❌ Background no encontrado: %s", bg_path)
        return

    log.info("🎞️ Renderizando video: %s", output_path)
    bg = VideoFileClip(bg_path).without_audio()
    bg_resized = bg.resize(height=1920)
    bg_v = bg_resized.crop(x_center=bg_resized.size[0] / 2, width=1080)

    visuals = [bg_v]
    audios = []
    current_time = 0.5

    for i, line in enumerate(script_data["timeline"]):
        char = line[2]
        prefix_str = f"{audio_prefix}_" if audio_prefix else ""
        audio_p = f"assets/audio_{prefix_str}{i}.mp3"

        if not os.path.exists(audio_p):
            log.warning("⚠️ Audio %s no existe, saltando línea %d.", audio_p, i)
            continue

        a_clip = AudioFileClip(audio_p).set_start(current_time)
        actual_duration = a_clip.duration
        audios.append(a_clip)

        img_p = f"assets/{char.lower()}.png"
        if os.path.exists(img_p):
            target_h = CHAR_HEIGHT.get(char.upper(), DEFAULT_CHAR_HEIGHT)
            char_c = (
                ImageClip(img_p)
                .set_start(current_time)
                .set_duration(actual_duration)
                .set_position(("center", "bottom"))
                .resize(height=target_h)
            )
            visuals.append(char_c)
        else:
            log.warning("⚠️ Imagen de personaje %s no existe.", img_p)

        current_time += actual_duration + 0.3

    if not audios:
        log.error("❌ No se generó ningún audio, abortando render.")
        bg.close()
        return

    final_v = (
        CompositeVideoClip(visuals)
        .set_audio(CompositeAudioClip(audios))
        .set_duration(current_time + 0.5)
    )

    try:
        final_v.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            ffmpeg_params=["-pix_fmt", "yuv420p", "-crf", "28"],
            threads=4,
            logger=None,
        )
    finally:
        bg.close()
        final_v.close()
        for a in audios:
            a.close()
