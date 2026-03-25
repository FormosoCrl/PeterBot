import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import save
from moviepy.editor import AudioFileClip, concatenate_audioclips

# 1. Cargamos los secretos del archivo .env de forma segura
load_dotenv()

# === 🔑 ZONA DE LLAVES (Segura) ===
# El script buscará estas variables dentro de tu archivo .env
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

VOICES = {
    "Peter": os.getenv("VOICE_PETER"),
    "Brian": os.getenv("VOICE_BRIAN")
}


# ==========================================

def generate_dialogue_audio(script_data, output_filepath="assets/audio_final.mp3"):
    """
    Lee el guion, genera las voces, las une en un solo archivo
    y devuelve el mapa de tiempos REAL (milisegundo exacto donde cambia de personaje).
    """
    print("🗣️ Conectando con ElevenLabs...")

    # Verificamos si la clave existe antes de intentar conectar
    if not ELEVENLABS_API_KEY:
        print("⚠️ Advertencia: No se encontró ELEVENLABS_API_KEY en el archivo .env.")
        print("⚠️ Saltando la generación de voz real...")
        return None

    # Inicializamos el cliente
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

    audio_clips = []
    real_timeline = []
    current_time = 0.0  # Llevaremos la cuenta del tiempo real acumulado

    # Carpeta temporal para guardar las frases sueltas antes de unirlas
    os.makedirs("temp", exist_ok=True)

    # Extraemos el timeline del guion generado por el brain.py
    # Formato que viene: (Inicio_estimado, Fin_estimado, Personaje, Texto)
    for i, line_data in enumerate(script_data["timeline"]):
        character = line_data[2]
        text = line_data[3]

        print(f"🎙️ Grabando a {character}: '{text[:30]}...'")

        chunk_path = f"temp/frase_{i}.mp3"

        try:
            # 1. Generar el audio real con la IA de ElevenLabs
            voice_id = VOICES.get(character)
            if not voice_id:
                raise ValueError(f"No se encontró el ID de voz para {character} en el .env")

            audio_generator = client.generate(
                text=text,
                voice=voice_id,
                model="eleven_multilingual_v2"  # Modelo que entiende español e inglés perfecto
            )
            save(audio_generator, chunk_path)

            # 2. Cargar el audio generado con MoviePy para saber cuánto dura EXACTAMENTE
            clip = AudioFileClip(chunk_path)
            duration = clip.duration
            audio_clips.append(clip)

            # 3. Registrar el tiempo REAL para el motor de video (Director de cámaras)
            start_time = current_time
            end_time = current_time + duration

            # Guardamos: Cuándo empieza, cuándo acaba, y quién habla (Omitimos el texto)
            real_timeline.append((start_time, end_time, character))

            # Actualizamos el contador de tiempo sumándole lo que duró esta frase
            current_time = end_time

        except Exception as e:
            print(f"❌ Error al generar la voz de {character}: {e}")
            return None

    # 4. Unir todas las frases sueltas en un solo archivo de audio fluido
    if audio_clips:
        print("🔗 Uniendo todos los clips de audio en uno solo...")
        final_audio = concatenate_audioclips(audio_clips)
        final_audio.write_audiofile(output_filepath, fps=44100)

        # 5. Limpieza profunda: Borramos los archivos temporales para no saturar el PC/Servidor
        for clip in audio_clips:
            clip.close()

        for i in range(len(script_data["timeline"])):
            try:
                os.remove(f"temp/frase_{i}.mp3")
            except:
                pass

        print(f"✅ Audio final maestro listo. Duración total: {round(current_time, 2)} segundos")

        # Devolvemos el mapa de tiempos matemáticamente perfecto
        return real_timeline
    else:
        return None


if __name__ == "__main__":
    print("Módulo TTS estructurado, seguro y a la espera del guion.")