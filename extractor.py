import os

IGNORE_DIRS = {'.venv310', '__pycache__', 'assets', 'output', 'logs', 'browser_session', '.git', 'models'}
ALLOWED_EXT = {'.py', '.json', '.txt', '.md'}

with open('repo_dump.txt', 'w', encoding='utf-8') as out:
    out.write("=== ESTRUCTURA DEL REPOSITORIO ===\n")
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        level = root.replace('.', '').count(os.sep)
        indent = ' ' * 4 * level
        out.write(f"{indent}{os.path.basename(root)}/\n")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if any(f.endswith(ext) for ext in ALLOWED_EXT):
                out.write(f"{subindent}{f}\n")

    out.write("\n\n=== CONTENIDO DE LOS ARCHIVOS ===\n")
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            if any(f.endswith(ext) for ext in ALLOWED_EXT):
                filepath = os.path.join(root, f)
                out.write(f"\n{'='*50}\nARCHIVO: {filepath}\n{'='*50}\n")
                try:
                    with open(filepath, 'r', encoding='utf-8') as infile:
                        out.write(infile.read() + "\n")
                except Exception as e:
                    out.write(f"No se pudo leer: {e}\n")

print("✅ Archivo repo_dump.txt generado con exito!")
