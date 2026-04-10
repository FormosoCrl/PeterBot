import os

ARCHIVOS_CLAVE = [
    'brain.py',
    'voice_processor.py',
    'video_editor.py',
    'subtitle_engine.py',
    'uploader.py',
    'main.py',
    'README.md'
]

with open('repo_dump_limpio.txt', 'w', encoding='utf-8') as out:
    for f in ARCHIVOS_CLAVE:
        if os.path.exists(f):
            out.write(f"\n{'='*50}\nARCHIVO: {f}\n{'='*50}\n")
            try:
                with open(f, 'r', encoding='utf-8') as infile:
                    out.write(infile.read() + "\n")
            except Exception as e:
                out.write(f"Error al leer: {e}\n")

print("✅ Archivo repo_dump_limpio.txt generado. ¡Esta vez en versión humana!")
