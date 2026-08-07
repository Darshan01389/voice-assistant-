import os
from dotenv import load_dotenv

load_dotenv()

# ─── Gemini ───────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL   = "gemini-1.5-flash"

# ─── Ollama (local) ───────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "llama3")   # change to mistral etc.

# ─── Speech Recognition ───────────────────────────────────
WHISPER_MODEL   = "base"          # tiny | base | small | medium | large
WAKE_WORD       = "hey assistant"
WAKE_WORD_ALTS  = ["hey assistant", "hi assistant", "hello assistant"]

# ─── TTS ──────────────────────────────────────────────────
TTS_RATE   = 175    # words-per-minute
TTS_VOLUME = 1.0    # 0.0 – 1.0

# ─── Assistant Persona ────────────────────────────────────
SYSTEM_PROMPT = (
    "You are a helpful, concise voice assistant. "
    "Keep responses short and conversational (2-3 sentences max) "
    "since they will be spoken aloud. Avoid markdown, bullet points, "
    "or special characters."
)
