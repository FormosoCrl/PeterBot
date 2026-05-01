import logging
import os

import whisper
from moviepy.editor import CompositeVideoClip, TextClip, VideoFileClip

log = logging.getLogger("peterbot.subs")

# Modelo Whisper configurable: "tiny" (rápido CPU), "base" (balance), "small" (mejor calidad, más lento).
WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "base")
SUBTITLE_FONT = os.environ.get("SUBTITLE_FONT", "Impact")

# Cacheamos el modelo a nivel de módulo — recargar Whisper en cada llamada cuesta segundos.
_whisper_model = None


def _get_model():
    global _whisper_model
    if _whisper_model is None:
        log.info("⏳ Cargando modelo Whisper '%s' (primera vez)...", WHISPER_MODEL)
        _whisper_model = whisper.load_model(WHISPER_MODEL)
    return _whisper_model


def add_subtitles(video_path, output_path):
    log.info("✍️ Añadiendo subtítulos virales a %s", video_path)

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video no existe: {video_path}")

    model = _get_model()
    result = model.transcribe(video_path, word_timestamps=True)

    video = VideoFileClip(video_path)
    clips = [video]

    try:
        for segment in result.get("segments", []):
            for word in segment.get("words", []):
                w_text = word.get("word", "").strip().upper()
                if not w_text:
                    continue
                start = word.get("start")
                end = word.get("end")
                if start is None or end is None or end <= start:
                    continue
                try:
                    txt = TextClip(
                        w_text,
                        fontsize=90,
                        color="yellow",
                        font=SUBTITLE_FONT,
                        stroke_color="black",
                        stroke_width=2,
                        size=(int(video.w * 0.8), None),
                        method="caption",
                    )
                except Exception as e:
                    log.warning("⚠️ No se pudo crear TextClip para '%s': %s", w_text, e)
                    continue
                txt = txt.set_start(start).set_end(end).set_position(("center", 400))
                clips.append(txt)

        final = CompositeVideoClip(clips)
        final.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            ffmpeg_params=["-pix_fmt", "yuv420p", "-crf", "28", "-movflags", "+faststart"],
            threads=4,
            logger=None,
        )
    finally:
        video.close()
        if "final" in locals():
            final.close()
