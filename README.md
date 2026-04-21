# 🤖 PeterBot — Viral Content Factory

Pipeline totalmente automatizado para generar y publicar videos verticales
(TikTok / Instagram Reels / YouTube Shorts) con el dúo **Peter + Stewie**
comentando repos trending de GitHub.

---

## 🚀 Pipeline

1. **`brain.py`** — Scrapea GitHub Trending y genera un guión con **Gemini**
   (`gemini-3-flash-preview` por defecto, configurable con `GEMINI_MODEL`).
2. **`voice_processor.py`** — TTS con **Silero** (CPU) + clonación de voz con
   **RVC** local (`rvc-cli`). Modelos `.pth` / `.index` en `models/`.
3. **`video_editor.py`** — Compone el video vertical 1080×1920 con
   **MoviePy**: fondo (Minecraft parkour) + imágenes de personajes + audio.
4. **`subtitle_engine.py`** — Subtítulos word-level con **OpenAI Whisper**
   (modelo `base`).
5. **`uploader.py`** — Publica en TikTok e Instagram con **Playwright** y
   sesión persistente por cuenta.
6. **`main.py`** — Orquestador. Genera el batch del día siguiente a las
   `PRODUCE_HOUR` (22:00 por defecto) y publica a las 08:30 y 20:30 con
   jitter aleatorio.

---

## 🛠️ Tech stack

- Python 3.12
- Gemini API (`google-genai`)
- Silero TTS + RVC (`rvc-cli`)
- MoviePy 1.0.3 + ImageMagick (Windows: marca *Install legacy utilities*)
- OpenAI Whisper (local, CPU)
- Playwright Chromium headless
- Dotenv

---

## 📦 Instalación

```bash
git clone https://github.com/FormosoCrl/PeterBot.git
cd PeterBot

python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Linux (Contabo)
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

Además necesitas:

- **ImageMagick** instalado a nivel de sistema (para los subtítulos de MoviePy).
- **`rvc-cli`** instalado globalmente (no es pip-installable estándar, ver
  [RVC-CLI docs](https://rvc-cli.pages.dev/)).
- Modelos RVC en `models/PETER.pth`, `models/PETER.index`, `models/STEWIE.pth`,
  `models/STEWIE.index`.

---

## ⚙️ Configuración (`.env`)

```dotenv
# APIs
GEMINI_API_KEY=tu_key
GEMINI_MODEL=gemini-3-flash-preview   # opcional

# Comportamiento
DRY_RUN=true          # true = no publica en redes (recomendado 1ª vuelta)
PRODUCE_HOUR=22       # hora de generación del batch

# Sesiones persistentes por cuenta
REPO_PETER_SESSION_DIR=./sessions/repo_peter
DEV_PETER_SESSION_DIR=./sessions/dev_peter
```

---

## 🔐 Sesiones de navegador

Antes de la primera ejecución hay que loguearse manualmente en cada red
para cada identidad:

```bash
python get_session.py
```

El script abre Chromium no-headless, pide el nombre de la identidad
(ej. `repo_peter`) y guarda la sesión en `sessions/<identidad>/`.
Después, `uploader.py` levanta esa sesión en headless sin pedir login.

---

## 🎮 Uso

```bash
# Primera validación (no publica — safety guard + DRY_RUN)
DRY_RUN=true python main.py

# Producción real (cuando hayas validado al menos 3-4 rondas)
DRY_RUN=false python main.py
```

En Contabo lo típico es lanzarlo con `systemd` o `tmux` para que sobreviva
al logout.

---

## 🛡️ Safety guards

- Los clicks finales de `Post` / `Share` están **comentados** en
  `uploader.py`. Actívalos sólo cuando confirmes que los selectores y la
  sesión funcionan.
- `DRY_RUN=true` corta la llamada al uploader antes de abrir el navegador.
- `output/state.json` guarda los últimos 50 repos cubiertos para no
  repetir tema al día siguiente.

---

## 📁 Licencia

Proyecto privado. Uso personal. All rights reserved.
