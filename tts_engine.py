import os
from elevenlabs.client import ElevenLabs
from elevenlabs import save
from moviepy.editor import AudioFileClip, concatenate_audioclips
from dotenv import load_dotenv

load_dotenv()

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
VOICE_IDS = {
    "Peter": os.getenv("VOICE_PETER"),
    "Brian": os.getenv("VOICE_BRIAN")
}


def generate_dialogue_audio(script_data, output_filepath):
    """Genera las voces, las une y devuelve el timeline real."""
    print("🎙️ [TTS] Generando voces con ElevenLabs...")

    os.makedirs("temp", exist_ok=True)
    audio_clips = []
    real_timeline = []
    current_time = 0.0

    try:
        for i, line in enumerate(script_data["timeline"]):
            character = line[2]
            text = line[3]
            chunk_path = f"temp/chunk_{i}.mp3"

            # Generar audio
            audio_gen = client.generate(
                text=text,
                voice=VOICE_IDS[character],
                model="eleven_multilingual_v2"
            )
            save(audio_gen, chunk_path)

            # Cargar para medir duración
            clip = AudioFileClip(chunk_path)
            duration = clip.duration

            real_timeline.append((current_time, current_time + duration, character))
            current_time += duration
            audio_clips.append(clip)

        # Unir clips
        final_audio = concatenate_audioclips(audio_clips)
        final_audio.write_audiofile(output_filepath, fps=44100)

        # Limpieza de memoria
        for clip in audio_clips:
            clip.close()

        print(f"✅ Audio final generado: {output_filepath}")
        return real_timeline

    except Exception as e:
        print(f"❌ Error en TTS Engine: {e}")
        return None