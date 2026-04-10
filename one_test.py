# -*- coding: utf-8 -*-
import asyncio
import os
from datetime import datetime
from brain import generate_script
from voice_processor import generate_voice
from video_editor import create_minecraft_video
from subtitle_engine import add_subtitles

async def run_single():
    acc = "Repo-Peter"
    slot = "AM"
    
    print(f"INICIANDO PRUEBA UNICA: {acc} ({slot})")
    print("Generando guion con Gemini...")
    script = generate_script(acc)
    
    if not script:
        print("ERROR: Gemini no devolvio un guion valido.")
        return
    
    print("Generando voces clonadas...")
    for i, line in enumerate(script["timeline"]):
        await generate_voice(line[3], line[2], f"{acc}_{slot}_{i}")
    
    video_base = f"output/base_{acc}_{slot}.mp4"
    video_final = f"output/FINAL_{acc}_{slot}.mp4"
    
    print("Montando video base (Minecraft + Personajes)...")
    create_minecraft_video(script, "assets/minecraft_parkour.mp4", video_base, audio_prefix=f"{acc}_{slot}")
    
    print("Anadiendo subtitulos...")
    try:
        if os.path.exists(video_base):
            add_subtitles(video_base, video_final)
            print(f"EXITO! Video con subtitulos listo en: {video_final}")
            os.remove(video_base)
        else:
            print("ERROR: El video base no se creo.")
    except Exception as e:
        print(f"Error en subtitulos: {e}. Renombrando video base.")
        if os.path.exists(video_base):
            os.rename(video_base, video_final)

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    os.makedirs("assets", exist_ok=True)
    asyncio.run(run_single())