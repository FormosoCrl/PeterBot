import whisper
import os
from moviepy.editor import TextClip, CompositeVideoClip, VideoFileClip


def transcribe_audio(audio_path):
    print("🎙️ [Whisper] Transcribiendo audio para subtítulos...")
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, word_timestamps=True, language="es")

    words_data = []
    for segment in result['segments']:
        for word in segment['words']:
            words_data.append({
                "text": word['word'].strip().upper(),
                "start": word['start'],
                "end": word['end']
            })
    return words_data


def add_viral_subtitles(video_path, words_data, output_path):
    print("✍️ [Editor] Quemando subtítulos virales...")
    video = VideoFileClip(video_path)
    subtitle_clips = []

    for word in words_data:
        # Estilo Impact Amarillo (Viral)
        txt = TextClip(
            word['text'],
            fontsize=95,
            color='yellow',
            font='Impact',
            stroke_color='black',
            stroke_width=3,
            method='caption',
            size=(900, None)
        )
        txt = txt.set_start(word['start']).set_end(word['end']).set_position('center')
        subtitle_clips.append(txt)

    final = CompositeVideoClip([video] + subtitle_clips)
    final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

    final.close();
    video.close()