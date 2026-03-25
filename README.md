# 🤖 PeterBot: The Viral Content Factory

**PeterBot** is a fully automated video generation pipeline designed to create "Split-Screen" viral content for TikTok, YouTube Shorts, and Instagram Reels. Featuring the iconic duo Peter and Brian, this bot scrapes GitHub repositories, generates AI-powered dialogues, and assembles high-engagement videos with dynamic subtitles.

---

## 🚀 Features

* **Automated Scraper:** Uses Playwright to capture clean, dark-mode screenshots of GitHub repositories or tech news.
* **AI Dialogue System:** Integrated with ElevenLabs for high-quality, emotional voiceovers.
* **Dynamic Video Engine:** Built on MoviePy to handle split-screen layouts, character "jumping" effects based on audio volume, and random gameplay background selection.
* **Viral Subtitles:** Powered by OpenAI's Whisper for word-level synchronization and "MrBeast-style" animated captions.
* **Auto-Distribution:** (In Progress) Logic for multi-platform uploading.

---

## 🛠️ Tech Stack

* **Language:** Python 3.12
* **Video Editing:** MoviePy
* **Browser Automation:** Playwright
* **Speech & Audio:** ElevenLabs API & OpenAI Whisper (Local)
* **Environment:** Dotenv for secure credential management

---

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/youruser/PeterBot.git](https://github.com/youruser/PeterBot.git)
   cd PeterBot
Setup Virtual Environment:

Bash
python -m venv .venv1
# Activate on Windows:
.\.venv1\Scripts\activate
Install Dependencies:

Bash
pip install -r requirements.txt
playwright install
External Requirement:
Install ImageMagick on your OS. Crucial for Windows: Check the box "Install legacy utilities (e.g. convert)" during installation.

⚙️ Configuration
Create a .env file in the root directory and fill in your credentials:

Fragmento de código
ELEVENLABS_API_KEY=your_key_here
VOICE_PETER=your_peter_voice_id
VOICE_BRIAN=your_brian_voice_id

# Optional for future features:
OPENAI_API_KEY=your_openai_key
TIKTOK_SESSION_ID=your_session_id
🎮 Usage
Place your base assets in the assets/ folder:

peter.png / brian.png (Transparent backgrounds)

minecraft_parkour.mp4 (Or any background gameplay)

audio_final.mp3 (Test audio if API is not set)

Run the master script:

Bash
python main.py
Output:
Find your rendered masterpiece in the output/ folder.

🛡️ License
This project is private and intended for personal use. All rights reserved.