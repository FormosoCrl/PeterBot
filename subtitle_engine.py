import os
import whisper
from moviepy.editor import TextClip, CompositeVideoClip, VideoFileClip


def transcribe_audio(audio_path):
    """
    Usa el modelo local Whisper de OpenAI (100% gratis) para generar
    la transcripción exacta de cada palabra con su segundo de inicio y fin.
    """
    print("🎙️ Analizando el audio con Whisper (esto puede tardar unos segundos)...")

    # Usamos el modelo 'base' porque es súper rápido y pesa poco.
    # Para más precisión en el servidor final, usaremos 'small' o 'medium'.
    model = whisper.load_model("base")

    # El parámetro word_timestamps=True es MAGIA: nos dice exactamente
    # el milisegundo en el que se dice cada palabra.
    result = model.transcribe(audio_path, word_timestamps=True, language="es")

    words_data = []
    # Navegamos por el JSON complejo que devuelve Whisper para sacar solo lo útil
    for segment in result['segments']:
        for word in segment['words']:
            words_data.append({
                "text": word['word'].strip().upper(),  # Mayúsculas para más impacto
                "start": word['start'],
                "end": word['end']
            })

    print(f"✅ Transcripción completa: {len(words_data)} palabras encontradas.")
    return words_data


def add_viral_subtitles(video_path, words_data, output_path):
    """
    Pega las palabras una a una sobre el video con estilo viral.
    """
    print("✍️ Quemando subtítulos virales en el video...")

    # Cargamos el video que ya montamos en video_engine.py
    video = VideoFileClip(video_path)

    subtitle_clips = []

    # IMPORTANTE: Si te da un error de "ImageMagick not found" al ejecutar,
    # tendrás que descargar e instalar ImageMagick en tu Windows.
    for word in words_data:
        # Aquí definimos la "Estética MrBeast"
        # Usamos Impact (o Arial Bold), amarillo brillante, con borde negro para que se lea en cualquier fondo.
        txt_clip = TextClip(
            word['text'],
            fontsize=90,
            color='yellow',
            font='Impact',
            stroke_color='black',
            stroke_width=3,
            method='caption',
            size=(800, None)  # Ajusta el ancho máximo del texto
        )

        # Posicionamos en el centro de la pantalla (donde se cruzan las dos mitades)
        # y le damos el tiempo exacto que nos dijo Whisper
        txt_clip = txt_clip.set_position('center').set_start(word['start']).set_end(word['end'])

        subtitle_clips.append(txt_clip)

    # Juntamos el video original con todos los "clips" de texto
    final_video = CompositeVideoClip([video] + subtitle_clips)

    # Exportamos (usamos hilos para que vaya más rápido)
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", threads=4)


if __name__ == "__main__":
    # Prueba del motor de subtítulos:
    # 1. Necesitas un audio (audio_final.mp3)
    # 2. Necesitas un video ya montado (sin subtítulos) de la prueba anterior
    #
    # words = transcribe_audio("assets/audio_final.mp3")
    # add_viral_subtitles("output/tiktok_listo.mp4", words, "output/tiktok_final_subtitulado.mp4")
    print("Módulo de Subtítulos listo.")