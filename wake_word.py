"""
wake_word.py
------------
Lightweight background thread that listens for the wake word
("hey assistant") using Google Speech Recognition.
No paid API needed — works with free Google STT.
"""

import threading
import speech_recognition as sr
from config import WAKE_WORD_ALTS


class WakeWordDetector:
    """
    Runs in a daemon thread.
    Calls `on_wake()` callback whenever the wake word is detected.
    """

    def __init__(self, on_wake, energy_threshold: int = 300):
        self._on_wake         = on_wake
        self._energy_threshold = energy_threshold
        self._running         = False
        self._thread          = None
        self._paused          = False   # pause during active recording

    # ── Public API ────────────────────────────────────────

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread  = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def pause(self):
        """Call while main mic is recording to avoid double-capture."""
        self._paused = True

    def resume(self):
        self._paused = False

    # ── Internal loop ─────────────────────────────────────

    def _loop(self):
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = self._energy_threshold
        recognizer.dynamic_energy_threshold = True

        while self._running:
            if self._paused:
                threading.Event().wait(0.3)
                continue
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    audio = recognizer.listen(source, timeout=3,
                                              phrase_time_limit=4)
                text = recognizer.recognize_google(audio).lower().strip()
                if any(ww in text for ww in WAKE_WORD_ALTS):
                    self._on_wake()
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                pass    # silence or unclear audio — keep looping
            except sr.RequestError:
                pass    # no internet — skip this cycle
            except Exception as e:
                print(f"[WakeWord] {e}")
