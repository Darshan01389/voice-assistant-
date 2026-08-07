"""
speech_output.py
----------------
Text-to-speech using pyttsx3 (fully offline, no API needed).
"""

import threading
import pyttsx3
from config import TTS_RATE, TTS_VOLUME

# Engine lives in its own thread to avoid blocking the Flet UI event loop
_engine = None
_lock   = threading.Lock()


def _init_engine():
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
        _engine.setProperty("rate",   TTS_RATE)
        _engine.setProperty("volume", TTS_VOLUME)
        # Pick a slightly nicer voice if available
        voices = _engine.getProperty("voices")
        for v in voices:
            if "zira" in v.name.lower() or "female" in v.name.lower():
                _engine.setProperty("voice", v.id)
                break


def speak(text: str, on_done=None):
    """
    Speak `text` asynchronously.
    Calls on_done() when finished (optional callback for UI updates).
    """
    def _run():
        with _lock:
            _init_engine()
            _engine.say(text)
            _engine.runAndWait()
        if on_done:
            on_done()

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return t


def stop():
    """Stop any ongoing speech."""
    with _lock:
        if _engine:
            try:
                _engine.stop()
            except Exception:
                pass
