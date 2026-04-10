import os, asyncio, torch, re
from dotenv import load_dotenv

load_dotenv()
device = torch.device('cpu')
model_tts, _ = torch.hub.load(repo_or_dir='snakers4/silero-models', model='silero_tts', language='en', speaker='v3_en', trust_repo=True)
model_tts.to(device)

async def generate_voice(text, character, index):
    text_clean = re.sub(r'[^a-zA-Z0-9\s!?]', '', text)
    temp_wav = f"assets/temp_{index}.wav"
    final_mp3 = f"assets/audio_{index}.mp3"

    # 1. Generar audio base
    speaker_id = 'en_1' if character.upper() == "PETER" else 'en_2'
    model_tts.save_wav(text=text_clean, speaker=speaker_id, sample_rate=48000, audio_path=temp_wav)

    # 2. Inferencia RVC Local
    pth = os.path.join("models", f"{character.upper()}.pth")
    index_file = os.path.join("models", f"{character.upper()}.index")

    # AJUSTE DE PITCH (Aqui esta la magia)
    pitch_shift = -5 if character.upper() == "PETER" else 12

    cmd = f"rvc-cli infer --input {temp_wav} --model {pth} --index {index_file} --output {final_mp3} --device cpu --pitch {pitch_shift}"
    process = await asyncio.create_subprocess_shell(cmd)
    await process.communicate()

    if os.path.exists(temp_wav): os.remove(temp_wav)
    return final_mp3
