import numpy as np
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, VideoFileClip
import random


def get_audio_volume(audio_clip, fps=10):
    """Analiza el volumen del audio para saber cuándo hacer saltar al personaje."""
    audio_data = audio_clip.to_soundarray(fps=fps)
    if len(audio_data.shape) > 1:
        audio_data = np.mean(audio_data, axis=1)
    return np.abs(audio_data)


def create_split_screen_video(audio_path, speaker_timeline, peter_path, brian_path, repo_bg_path, gameplay_path,
                              output_path):
    # 1. Cargar el audio principal (que contendrá las voces de ambos)
    audio = AudioFileClip(audio_path)
    duration = audio.duration

    # 2. Analizar el volumen para el efecto de habla
    fps_analysis = 10
    volumes = get_audio_volume(audio, fps=fps_analysis)

    # 3. MITAD INFERIOR: El Gameplay (Hipnosis visual con corte aleatorio)
    gameplay_clip = VideoFileClip(gameplay_path).without_audio()

    # Calculamos el tiempo máximo desde donde podemos empezar a cortar
    max_start = max(0, gameplay_clip.duration - duration)
    # Elegimos un segundo de inicio al azar
    random_start = random.uniform(0, max_start)

    # Cortamos el trozo aleatorio y lo redimensionamos
    gameplay_clip = gameplay_clip.subclip(random_start, random_start + duration).resize(width=1080)
    # Lo ubicamos exactamente de la mitad (960) hacia abajo
    gameplay_clip = gameplay_clip.set_position(("center", 960))

    # 4. MITAD SUPERIOR: El Fondo del Repo (Contexto)
    repo_bg = ImageClip(repo_bg_path).resize(width=1080).set_duration(duration)
    repo_bg = repo_bg.set_position(("center", 0))

    # 5. EL DIRECTOR DE CÁMARAS: Lógica de los Personajes
    peter_img = ImageClip(peter_path).resize(width=650)
    brian_img = ImageClip(brian_path).resize(width=650)

    def make_character_clip(speaker_name, img_clip):
        """Genera el comportamiento de cada personaje segundo a segundo"""

        def filter_position(t):
            # A. ¿Es el turno de hablar de este personaje?
            is_speaking = False
            for start, end, spk in speaker_timeline:
                if start <= t <= end and spk == speaker_name:
                    is_speaking = True
                    break

            # Si no le toca hablar, lo "escondemos" fuera de la pantalla
            if not is_speaking:
                return (-1000, -1000)

            # B. Si le toca hablar, aplicamos el salto según el volumen
            # (Indentación corregida: ahora está al mismo nivel que el 'if' anterior)
            index = int(t * fps_analysis)
            vol = volumes[index] if index < len(volumes) else 0

            # Posición base en la mitad superior (Y=250). Si grita/habla, sube 25 píxeles.
            y_pos = 250 - (25 if vol > 0.05 else 0)
            return ("center", y_pos)

        return img_clip.set_duration(duration).set_position(filter_position)

    # Aplicamos la lógica a ambos PNGs
    peter_dynamic = make_character_clip("Peter", peter_img)
    brian_dynamic = make_character_clip("Brian", brian_img)

    # 6. RENDERIZADO FINAL: Juntamos todas las capas
    # El orden importa: Fondo -> Gameplay -> Personajes encima
    final_video = CompositeVideoClip([repo_bg, gameplay_clip, peter_dynamic, brian_dynamic], size=(1080, 1920))
    final_video = final_video.set_audio(audio)

    print(f"🎬 Renderizando video viral de {duration} segundos...")
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")


if __name__ == "__main__":
    # ASÍ ES COMO LA IA LO EJECUTARÁ EN EL FUTURO:
    # timeline = [
    #     (0.0, 4.0, "Peter"),   # Peter habla los primeros 4 segs
    #     (4.0, 8.5, "Brian"),   # Brian responde
    #     (8.5, 12.0, "Peter")   # Peter remata
    # ]
    # create_split_screen_video(
    #     audio_path="assets/audio_final.mp3",
    #     speaker_timeline=timeline,
    #     peter_path="assets/peter.png",
    #     brian_path="assets/brian.png",
    #     repo_bg_path="assets/github_repo.png",
    #     gameplay_path="assets/minecraft_parkour.mp4",
    #     output_path="output/tiktok_listo.mp4"
    # )
    print("✅ Motor Split-Screen actualizado y listo.")