"""
assistant.py
------------
Orchestrates: mic input → AI response → TTS output.
Maintains conversation history.
"""

import threading
from speech_input  import listen_once
from speech_output import speak, stop as tts_stop
from ai_backend    import get_response
from wake_word     import WakeWordDetector


class VoiceAssistant:
    def __init__(self, ui_callbacks: dict):
        """
        ui_callbacks keys (all optional):
          on_status(str)        → update status label
          on_user_msg(str)      → append user bubble
          on_ai_msg(str, str)   → append AI bubble (text, backend_name)
          on_listening(bool)    → mic indicator on/off
          on_speaking(bool)     → speaker indicator on/off
          on_wake()             → wake-word detected notification
        """
        self._cb       = ui_callbacks
        self._history  : list[dict] = []
        self._busy     = False

        # Wake word detector
        self._wake = WakeWordDetector(on_wake=self._handle_wake)

    # ── Public API ────────────────────────────────────────

    def start_wake_word(self):
        self._wake.start()
        self._status("Wake word active — say 'Hey Assistant' or press Space")

    def stop_wake_word(self):
        self._wake.stop()

    def start_listening(self):
        """Called when user presses the mic button or Space key."""
        if self._busy:
            return
        threading.Thread(target=self._pipeline, daemon=True).start()

    def clear_history(self):
        self._history.clear()
        self._status("Conversation cleared.")

    def stop_speaking(self):
        tts_stop()

    # ── Internal pipeline ─────────────────────────────────

    def _handle_wake(self):
        self._cb.get("on_wake", lambda: None)()
        if not self._busy:
            threading.Thread(target=self._pipeline, daemon=True).start()

    def _pipeline(self):
        self._busy = True
        self._wake.pause()

        try:
            # 1. Listen
            self._status("Listening…")
            self._cb.get("on_listening", lambda v: None)(True)
            result = listen_once(timeout=6, phrase_limit=12)
            self._cb.get("on_listening", lambda v: None)(False)

            if result["error"] == "timeout":
                self._status("Timed out — try again.")
                return
            if not result["text"]:
                self._status("Couldn't understand — try again.")
                return

            user_text = result["text"]
            engine_tag = f"[{result['engine']}]"
            self._cb.get("on_user_msg", lambda t: None)(user_text)
            self._status(f"Understood {engine_tag}  •  Thinking…")

            # 2. AI response
            self._history.append({"role": "user", "content": user_text})
            ai_result = get_response(self._history)
            ai_text   = ai_result["text"]
            backend   = ai_result["backend"] or "error"
            self._history.append({"role": "assistant", "content": ai_text})

            self._cb.get("on_ai_msg", lambda t, b: None)(ai_text, backend)
            self._status(f"Speaking…  [{backend}]")

            # 3. Speak
            self._cb.get("on_speaking", lambda v: None)(True)
            speak(ai_text, on_done=lambda: (
                self._cb.get("on_speaking", lambda v: None)(False),
                self._status("Ready — press Space or say 'Hey Assistant'"),
            ))

        finally:
            self._busy = False
            self._wake.resume()

    def _status(self, msg: str):
        self._cb.get("on_status", lambda m: None)(msg)
