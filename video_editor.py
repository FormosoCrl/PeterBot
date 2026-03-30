import os
import PIL.Image

# 🛠️ PARCHE DE COMPATIBILIDAD
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, CompositeAudioClip


def create_minecraft_video(script_data, bg_path, output_path):
    print("🎞️ Renderizando video (Forzando resolución par 1080x1920)...")

    # 1. Cargar fondo
    bg = VideoFileClip(bg_path).without_audio()

    # 📏 PASO CLAVE: Primero reescalamos a 1920 de alto para mantener calidad
    bg_resized = bg.resize(height=1920)
    w_res, h_res = bg_resized.size

    # 📏 PASO CLAVE 2: Cortamos a exactamente 1080 de ancho.
    # 1080 es par, así que libx264 NO dará error.
    bg_v = bg_resized.crop(x_center=w_res / 2, width=1080)

    visuals = [bg_v]
    audios = []

    # 2. Procesar Timeline (Sin cambios en las features)
    for i, line in enumerate(script_data["timeline"]):
        start, end, char, _ = line
        audio_p = f"assets/audio_{i}.mp3"

        if os.path.exists(audio_p):
            audios.append(AudioFileClip(audio_p).set_start(start))
            img_p = f"assets/{char.lower()}.png"
            if os.path.exists(img_p):
                char_c = (ImageClip(img_p)
                          .set_start(start)
                          .set_duration(end - start)
                          .set_position(("center", "bottom"))
                          .resize(width=800))
                visuals.append(char_c)

    final_duration = script_data["timeline"][-1][1]

    final = (CompositeVideoClip(visuals)
             .set_audio(CompositeAudioClip(audios))
             .set_duration(final_duration))

    # 🚀 Escritura con parámetros de compatibilidad total
    final.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        ffmpeg_params=["-pix_fmt", "yuv420p"],
        threads=4
    )

    # Limpieza
    bg.close()
    bg_resized.close()
    final.close()