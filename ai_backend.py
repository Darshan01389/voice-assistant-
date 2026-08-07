"""
ai_backend.py
-------------
AI response engine.
  - PRIMARY  : Google Gemini 1.5 Flash (free tier, online)
  - FALLBACK : Ollama local LLM       (offline, e.g. llama3 / mistral)
"""

import requests
import google.genai as genai
from config import (
    GEMINI_API_KEY, GEMINI_MODEL,
    OLLAMA_BASE_URL, OLLAMA_MODEL,
    SYSTEM_PROMPT,
)

# ── Gemini setup ──────────────────────────────────────────
_gemini_model = None

def _get_gemini():
    global _gemini_model
    if _gemini_model is None and GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=SYSTEM_PROMPT,
        )
    return _gemini_model


def _gemini_chat(history: list[dict]) -> str:
    model = _get_gemini()

    if model is None:
        raise RuntimeError("Gemini API key not set.")

    prompt = ""

    for msg in history:
        role = "User" if msg["role"] == "user" else "Assistant"
        prompt += f"{role}: {msg['content']}\n"

    result = model.generate_content(prompt)

    return result.text.strip()


# ── Ollama setup ──────────────────────────────────────────

def _ollama_chat(history: list[dict]) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
    resp = requests.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json={"model": OLLAMA_MODEL, "messages": messages, "stream": False},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"].strip()


# ── Public interface ──────────────────────────────────────

def get_response(history: list[dict]) -> dict:
    """
    history: list of {"role": "user"|"assistant", "content": str}
    Returns:
        {"text": str, "backend": "gemini"|"ollama", "error": str|None}
    """
    # ── Try Gemini first ───────────────────────────────────
    if GEMINI_API_KEY:
        try:
            text = _gemini_chat(history)
            return {"text": text, "backend": "gemini", "error": None}
        except Exception as e:
            print(f"[Gemini error] {e} — falling back to Ollama")

    # ── Fallback: Ollama ───────────────────────────────────
    try:
        text = _ollama_chat(history)
        return {"text": text, "backend": "ollama", "error": None}
    except Exception as e:
        return {
            "text": "Sorry, I could not reach any AI backend right now.",
            "backend": None,
            "error": str(e),
        }
