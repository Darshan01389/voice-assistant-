"""
main.py
-------
Flet UI for the Voice Assistant.
Dark, futuristic aesthetic with animated mic button,
chat bubbles, status bar, and keyboard shortcut (Space).
"""

import flet as ft
import threading
from assistant import VoiceAssistant

# ── Colour palette ────────────────────────────────────────
BG         = "#0D0F14"
SURFACE    = "#161920"
SURFACE2   = "#1E2330"
ACCENT     = "#00E5FF"
ACCENT2    = "#7C4DFF"
USER_BG    = "#1A2744"
AI_BG      = "#151D2E"
TEXT_PRI   = "#E8EAF0"
TEXT_SEC   = "#6B7280"
SUCCESS    = "#00C853"
WARNING    = "#FF6D00"


def main(page: ft.Page):
    page.title        = "Voice Assistant"
    page.bgcolor      = BG
    page.window_width  = 480
    page.window_height = 780
    page.window_resizable = False
    page.padding      = 0
    page.fonts        = {
        "Orbitron": "https://fonts.gstatic.com/s/orbitron/v29/yMJMMIlzdpvBhQQL_SC3X9yhF25-T1nyKS6BogtAre6vCA.woff2",
        "Inter":    "https://fonts.gstatic.com/s/inter/v13/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyfAZ9hiJ-Ek-_EeA.woff2",
    }
    page.theme = ft.Theme(font_family="Inter")

    # ── State ─────────────────────────────────────────────
    wake_enabled = ft.Ref[ft.Switch]()
    status_text  = ft.Ref[ft.Text]()
    mic_btn      = ft.Ref[ft.IconButton]()
    chat_list    = ft.ListView(expand=True, spacing=8, padding=ft.padding.symmetric(horizontal=16, vertical=8))
    pulse_ring   = ft.Ref[ft.Container]()
    backend_chip = ft.Ref[ft.Text]()

    # ── Callbacks ─────────────────────────────────────────
    def set_status(msg: str):
        if status_text.current:
            status_text.current.value = msg
            page.update()

    def add_user_msg(text: str):
        bubble = ft.Container(
            content=ft.Column([
                ft.Text("YOU", size=10, color=ACCENT, weight=ft.FontWeight.BOLD,
                        font_family="Orbitron"),
                ft.Text(text, color=TEXT_PRI, size=14, selectable=True),
            ], spacing=4),
            bgcolor=USER_BG,
            border_radius=ft.BorderRadius(12, 12, 2, 12),
            padding=ft.padding.all(14),
            margin=ft.margin.only(left=60),
            border=ft.border.all(1, "#1E3A5F"),
        )
        chat_list.controls.append(bubble)
        page.update()

    def add_ai_msg(text: str, backend: str):
        color_map = {"gemini": "#4285F4", "ollama": ACCENT2, None: TEXT_SEC}
        b_color   = color_map.get(backend, TEXT_SEC)
        b_label   = (backend or "error").upper()
        if backend_chip.current:
            backend_chip.current.value = f"● {b_label}"
            backend_chip.current.color = b_color
        bubble = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("ASSISTANT", size=10, color=b_color,
                            weight=ft.FontWeight.BOLD, font_family="Orbitron"),
                    ft.Container(
                        ft.Text(b_label, size=9, color=b_color),
                        bgcolor=f"{b_color}22",
                        border_radius=4,
                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                        border=ft.border.all(1, b_color),
                    ),
                ], spacing=8),
                ft.Text(text, color=TEXT_PRI, size=14, selectable=True),
            ], spacing=4),
            bgcolor=AI_BG,
            border_radius=ft.BorderRadius(12, 12, 12, 2),
            padding=ft.padding.all(14),
            margin=ft.margin.only(right=60),
            border=ft.border.all(1, "#1E2A3F"),
        )
        chat_list.controls.append(bubble)
        page.update()

    def set_listening(active: bool):
        if pulse_ring.current:
            pulse_ring.current.bgcolor = ACCENT if active else "transparent"
            pulse_ring.current.border  = ft.border.all(2, ACCENT if active else SURFACE2)
        if mic_btn.current:
            mic_btn.current.icon_color = ACCENT if active else TEXT_SEC
        page.update()

    def set_speaking(active: bool):
        if pulse_ring.current:
            pulse_ring.current.bgcolor = f"{ACCENT2}44" if active else "transparent"
        page.update()

    def on_wake_ui():
        set_status("🔔 Wake word detected!")
        page.update()

    callbacks = {
        "on_status":    set_status,
        "on_user_msg":  add_user_msg,
        "on_ai_msg":    add_ai_msg,
        "on_listening": set_listening,
        "on_speaking":  set_speaking,
        "on_wake":      on_wake_ui,
    }

    va = VoiceAssistant(callbacks)

    # ── Header ────────────────────────────────────────────
    header = ft.Container(
        ft.Row([
            ft.Column([
                ft.Text("VOICE ASSISTANT", size=16, color=ACCENT,
                        weight=ft.FontWeight.BOLD, font_family="Orbitron"),
                ft.Text("Gemini + Ollama  •  Whisper + Google STT",
                        size=10, color=TEXT_SEC),
            ], spacing=2, expand=True),
            ft.Text("● LIVE", ref=backend_chip, size=11, color=SUCCESS,
                    font_family="Orbitron"),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        bgcolor=SURFACE,
        padding=ft.padding.symmetric(horizontal=20, vertical=14),
        border=ft.border.only(bottom=ft.BorderSide(1, SURFACE2)),
    )

    # ── Chat area ─────────────────────────────────────────
    chat_area = ft.Container(
        content=chat_list,
        expand=True,
        bgcolor=BG,
    )

    # ── Mic button area ───────────────────────────────────
    def on_mic_click(_):
        va.start_listening()

    def on_clear(_):
        chat_list.controls.clear()
        va.clear_history()
        page.update()

    def on_wake_toggle(e):
        if e.control.value:
            va.start_wake_word()
        else:
            va.stop_wake_word()
            set_status("Wake word disabled  •  Press Space or tap mic")

    mic_area = ft.Container(
        ft.Column([
            # Pulse ring + mic button
            ft.Stack([
                ft.Container(
                    ref=pulse_ring,
                    width=80, height=80,
                    border_radius=40,
                    bgcolor="transparent",
                    border=ft.border.all(2, SURFACE2),
                    animate=ft.animation.Animation(400, ft.AnimationCurve.EASE_IN_OUT),
                ),
                ft.Container(
                    ft.IconButton(
                        ref=mic_btn,
                        icon=ft.icons.MIC,
                        icon_size=28,
                        icon_color=TEXT_SEC,
                        on_click=on_mic_click,
                        tooltip="Press to speak (or press Space)",
                        style=ft.ButtonStyle(
                            bgcolor={ft.MaterialState.DEFAULT: SURFACE2,
                                     ft.MaterialState.HOVERED: "#252D40"},
                            shape=ft.CircleBorder(),
                            padding=ft.padding.all(16),
                        ),
                    ),
                    left=5, top=5,
                ),
            ], width=80, height=80),

            # Status text
            ft.Text(ref=status_text,
                    value="Press mic or Space to speak",
                    size=12, color=TEXT_SEC, text_align=ft.TextAlign.CENTER),

            # Controls row
            ft.Row([
                ft.Row([
                    ft.Text("Wake Word", size=12, color=TEXT_SEC),
                    ft.Switch(ref=wake_enabled, value=False,
                              active_color=ACCENT, on_change=on_wake_toggle),
                ], spacing=6),
                ft.IconButton(
                    icon=ft.icons.DELETE_OUTLINE,
                    icon_color=TEXT_SEC, icon_size=20,
                    tooltip="Clear conversation",
                    on_click=on_clear,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
        bgcolor=SURFACE,
        padding=ft.padding.symmetric(horizontal=20, vertical=16),
        border=ft.border.only(top=ft.BorderSide(1, SURFACE2)),
    )

    # ── Keyboard shortcut (Space) ─────────────────────────
    def on_keyboard(e: ft.KeyboardEvent):
        if e.key == " " and not e.shift and not e.ctrl and not e.alt:
            va.start_listening()

    page.on_keyboard_event = on_keyboard

    # ── Layout ────────────────────────────────────────────
    page.add(
        ft.Column([
            header,
            chat_area,
            mic_area,
        ], expand=True, spacing=0)
    )

    # Welcome message
    add_ai_msg(
        "Hello! I'm your voice assistant powered by Gemini and Ollama. "
        "Tap the mic button, press Space, or enable the wake word to start.",
        "gemini",
    )
    set_status("Ready — tap mic or press Space to speak")


ft.app(target=main)
