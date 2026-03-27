import os, asyncio, ast, torch, re
from gradio_client import Client, handle_file
from dotenv import load_dotenv

load_dotenv()
SPACES_POOL = ast.literal_eval(os.getenv("RVC_SERVERS", "[]"))
device = torch.device('cpu')
model_tts, _ = torch.hub.load(repo_or_dir='snakers4/silero-models', model='silero_tts', language='en', speaker='v3_en',
                              trust_repo=True)
model_tts.to(device)


async def generate_voice(text, character, index):
    # ⚡ LIMPIEZA TOTAL: Solo una exclamación/pregunta AL FINAL
    text_clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    if "?" in text:
        text_clean = text_clean.strip() + "?"
    elif "!" in text:
        text_clean = text_clean.strip() + "!"
    text_clean = " ".join(text_clean.split())

    temp_base = f"temp_{character.lower()}.wav"
    final_output = f"assets/audio_{index}.mp3"

    speaker_id = 'en_1' if character.upper() == "PETER" else 'en_2'
    model_tts.save_wav(text=text_clean, speaker=speaker_id, sample_rate=48000, audio_path=temp_base)

    for space in SPACES_POOL:
        for intento in range(2):
            try:
                client = Client(space, token=os.getenv("HF_TOKEN"), verbose=False)
                pth = os.path.join("models", f"{character.upper()}.pth")
                idx = os.path.join("models", f"{character.upper()}.index")

                # --- 🛠️ MEJORA DE CALIDAD ---
                # Peter al 0.5 para que no sea robótico, Stewie al 0.75 porque su modelo es más fuerte
                idx_val = 0.5 if character.upper() == "PETER" else 0.75

                if "rvc-zero" in space.lower():
                    result = client.predict([handle_file(temp_base)], handle_file(pth), "rmvpe", 0, handle_file(idx),
                                            idx_val, 3, 0.25, 0.5, False, False, "mp3", 1, api_name="/run")
                else:
                    result = client.predict("Local file", handle_file(temp_base), handle_file(pth), 0, "rmvpe", idx_val,
                                            3, 0, 0.25, 0.33, "mp3", fn_index=0)

                if result:
                    audio_path = result[0] if isinstance(result, (list, tuple)) else result
                    if os.path.exists(final_output): os.remove(final_output)
                    os.rename(audio_path, final_output);
                    return final_output
            except Exception:
                if intento == 0: await asyncio.sleep(60)
    return None