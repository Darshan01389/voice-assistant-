"""
speech_input.py
---------------
Captures microphone audio and converts to text.
Strategy:
  1. Try Google Web Speech API (free, online)
  2. Fallback to OpenAI Whisper (offline)
"""

import io
import speech_recognition as sr
from config import WHISPER_MODEL

# Lazy-load Whisper so startup is fast even if not used
_whisper_model = None

def _get_whisper():
    global _whisper_model
    if _whisper_model is None:
        import whisper
        _whisper_model = whisper.load_model(WHISPER_MODEL)
    return _whisper_model


def listen_once(timeout: int = 5, phrase_limit: int = 10) -> dict:
    """
    Record one utterance from the mic.
    Returns:
        {"text": str, "engine": "google" | "whisper", "error": str | None}
    """
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 0.8

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=timeout,
                                      phrase_time_limit=phrase_limit)
        except sr.WaitTimeoutError:
            return {"text": "", "engine": None, "error": "timeout"}

    # ── 1. Google STT ──────────────────────────────────────
    try:
        text = recognizer.recognize_google(audio)
        return {"text": text.strip(), "engine": "google", "error": None}
    except sr.UnknownValueError:
        pass          # couldn't understand – try whisper
    except sr.RequestError:
        pass          # no internet – try whisper

    # ── 2. Whisper fallback ────────────────────────────────
    try:
        import tempfile, wave, numpy as np
        model = _get_whisper()
        raw = audio.get_wav_data()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(raw)
            tmp_path = f.name
        result = model.transcribe(tmp_path, fp16=False, language="en")
        text = result["text"].strip()
        import os; os.unlink(tmp_path)
        return {"text": text, "engine": "whisper", "error": None}
    except Exception as e:
        return {"text": "", "engine": None, "error": str(e)}
