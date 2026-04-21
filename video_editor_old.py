import os
import PIL.Image
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, CompositeAudioClip

if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

def create_minecraft_video(script_data, bg_path, output_path, audio_prefix=""):
    print(f"🎞️ Renderizando video: {output_path}")
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
        if os.path.exists(audio_p):
            a_clip = AudioFileClip(audio_p).set_start(current_time)
            actual_duration = a_clip.duration
            audios.append(a_clip)
            img_p = f"assets/{char.lower()}.png"
            if os.path.exists(img_p):
                char_c = (ImageClip(img_p).set_start(current_time)
                          .set_duration(actual_duration)
                          .set_position(("center", "bottom")).resize(width=800))
                visuals.append(char_c)
            current_time += actual_duration + 0.3
    if not audios:
        print("❌ Error: No hay audios.")
        return
    final_v = CompositeVideoClip(visuals).set_audio(CompositeAudioClip(audios)).set_duration(current_time + 0.5)
    final_v.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", ffmpeg_params=["-pix_fmt", "yuv420p"], threads=4)
    bg.close()
    final_v.close()
    for a in audios: a.close()
