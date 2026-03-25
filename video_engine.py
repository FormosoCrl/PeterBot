import numpy as np
import random
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, VideoFileClip


def get_audio_volume_map(audio_clip, fps=10):
    """Convierte el audio en un array de volumen para animar los PNGs."""
    audio_data = audio_clip.to_soundarray(fps=fps)
    if len(audio_data.shape) > 1:
        audio_data = np.mean(audio_data, axis=1)
    return np.abs(audio_data)


def create_split_screen_video(audio_path, speaker_timeline, peter_path, brian_path, repo_bg_path, gameplay_path,
                              output_path):
    print("🎬 [Video] Iniciando ensamblado de video...")

    # 1. Audio y Volumen
    audio = AudioFileClip(audio_path)
    volume_map = get_audio_volume_map(audio)
    duration = audio.duration

    # 2. Mitad Inferior: Gameplay aleatorio
    gameplay = VideoFileClip(gameplay_path).without_audio()
    max_start = max(0, gameplay.duration - duration)
    start_point = random.uniform(0, max_start)
    gameplay = gameplay.subclip(start_point, start_point + duration).resize(width=1080)
    gameplay = gameplay.set_position(("center", 960))

    # 3. Mitad Superior: Fondo del Repo
    repo_bg = ImageClip(repo_bg_path).resize(width=1080).set_duration(duration)
    repo_bg = repo_bg.set_position(("center", 0))

    # 4. Lógica de Personajes Dinámicos
    def make_character_clip(name, img_path):
        img = ImageClip(img_path).resize(width=650).set_duration(duration)

        def animar_posicion(t):
            # ¿Habla este personaje ahora?
            is_speaking = any(s <= t <= e and char == name for s, e, char in speaker_timeline)
            if not is_speaking:
                return (-2000, -2000)  # Escondido

            # Efecto salto según volumen
            idx = int(t * 10)
            vol = volume_map[idx] if idx < len(volume_map) else 0
            y_offset = 30 if vol > 0.05 else 0
            return ("center", 250 - y_offset)

        return img.set_position(animar_posicion)

    peter = make_character_clip("Peter", peter_path)
    brian = make_character_clip("Brian", brian_path)

    # 5. Renderizado
    final = CompositeVideoClip([repo_bg, gameplay, peter, brian], size=(1080, 1920))
    final = final.set_audio(audio)

    print(f"🚀 Renderizando MP4 final...")
    final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", threads=4)

    # Limpieza crítica de RAM
    final.close();
    audio.close();
    gameplay.close();
    repo_bg.close()