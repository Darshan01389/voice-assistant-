# 🎙️ Voice Assistant
**Speech Recognition + AI Response System**  
Built with Python · Flet UI · Gemini + Ollama · Whisper + Google STT

---

## ✨ Features
- 🎤 **Dual STT**: Google Speech API (online) → Whisper (offline fallback)
- 🤖 **Dual AI**: Gemini 1.5 Flash (free tier) → Ollama LLaMA3 (offline fallback)
- 🔊 **TTS**: pyttsx3 offline text-to-speech
- 🔔 **Wake word**: Say *"Hey Assistant"* to trigger hands-free
- ⌨️ **Hotkey**: Press `Space` to speak
- 💬 **Chat UI**: Beautiful dark Flet interface with conversation history

---

## 🚀 Quick Setup

### 1. Clone / download the project
```bash
cd voice_assistant
```

### 2. Install system dependencies

**Ubuntu/Debian:**
```bash
sudo apt install portaudio19-dev python3-pyaudio ffmpeg
```

**macOS:**
```bash
brew install portaudio ffmpeg
```

**Windows:**  
Download and install [FFmpeg](https://ffmpeg.org/download.html) and add to PATH.

### 3. Install Python packages
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

Get a **FREE** Gemini API key at: https://aistudio.google.com/app/apikey  
*(No credit card required)*

### 5. (Optional) Set up Ollama for offline AI
```bash
# Install Ollama from https://ollama.com
ollama pull llama3       # or: ollama pull mistral
```

### 6. Run the app
```bash
python main.py
```

---

## 🎮 How to Use

| Action | How |
|---|---|
| **Start speaking** | Click mic button or press `Space` |
| **Wake word** | Say *"Hey Assistant"* (enable toggle first) |
| **Stop TTS** | Click mic button while speaking |
| **Clear chat** | Click the 🗑️ trash icon |

---

## 🏗️ Project Structure

```
voice_assistant/
├── main.py          # Flet UI
├── assistant.py     # Core orchestration
├── speech_input.py  # Google STT + Whisper
├── speech_output.py # pyttsx3 TTS
├── wake_word.py     # Wake word detection
├── ai_backend.py    # Gemini + Ollama
├── config.py        # Settings
├── .env             # Your API keys (gitignored)
├── .env.example     # Template
└── requirements.txt
```

---

## ⚙️ Configuration (`config.py`)

| Setting | Default | Description |
|---|---|---|
| `WHISPER_MODEL` | `base` | STT model size (tiny/base/small/medium) |
| `WAKE_WORD` | `hey assistant` | Trigger phrase |
| `TTS_RATE` | `175` | Speech speed (words/min) |
| `OLLAMA_MODEL` | `llama3` | Local AI model |
| `SYSTEM_PROMPT` | See file | AI persona/instructions |

---

## 🔧 Troubleshooting

**Mic not working?**
```bash
# Test mic with Python
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

**PyAudio install fails?**
```bash
pip install pipwin && pipwin install pyaudio  # Windows
```

**Ollama connection refused?**
```bash
ollama serve  # Start Ollama server
```

---

## 📋 Requirements
- Python 3.9+
- Microphone
- Internet (for Gemini + Google STT) or Ollama installed (for offline)
