import whisper, os
from moviepy.editor import TextClip, CompositeVideoClip, VideoFileClip


def add_subtitles(video_path, output_path):
    print("✍️ Añadiendo subtítulos virales...")
    model = whisper.load_model("base")
    result = model.transcribe(video_path, word_timestamps=True)

    video = VideoFileClip(video_path)
    clips = [video]

    for segment in result['segments']:
        for word in segment['words']:
            txt = TextClip(word['word'].strip().upper(), fontsize=90, color='yellow', font='Impact',
                           stroke_color='black', stroke_width=2, size=(video.w * 0.8, None), method='caption')
            txt = txt.set_start(word['start']).set_end(word['end']).set_position('center')
            clips.append(txt)

    final = CompositeVideoClip(clips)
    final.write_videofile(output_path, fps=24, codec="libx264")