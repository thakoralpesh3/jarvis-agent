"""
Proactive "Silent Shadow" Co-Pilot for JARVIS.
Periodically observes active workspace windows, error logs, and clipboard to proactively
catch mistakes, compile errors, or stalled processes before the user has to ask.
"""

import time
import threading
from typing import Optional, Dict, Any

from tools.laptop_tools import list_active_windows, get_clipboard_content
from tools.ironman_protocols import play_stark_sound
from tools.laptop_work_tools import send_desktop_notification


class SilentShadowCopilot:
    """Proactive background assistant catching errors and suggesting instant fixes."""

    def __init__(self):
        self.is_active = False
        self._thread: Optional[threading.Thread] = None
        self.last_checked_clipboard = ""

    def start(self) -> str:
        if self.is_active:
            return "Silent Shadow Co-Pilot is already active, Sir."

        self.is_active = True
        play_stark_sound("protocol")
        send_desktop_notification(
            "Aradhya Shadow Co-Pilot Armed",
            "Silent Shadow Co-Pilot is actively watching for errors and roadblocks.",
            urgency="low",
            user_commanded=False
        )

        def _shadow_loop():
            while self.is_active:
                try:
                    # Check clipboard for error traces
                    clip = get_clipboard_content()
                    if clip and clip != self.last_checked_clipboard:
                        self.last_checked_clipboard = clip
                        if any(err_kw in clip.lower() for err_kw in ["traceback", "error:", "exception:", "syntaxerror", "failed to compile"]):
                            play_stark_sound("alert")
                            send_desktop_notification(
                                "Aradhya Proactive Error Catch",
                                "Sir, I detected an error signature on your clipboard. Type /stuck to view the complete solution.",
                                details=f"Captured Error Signature:\n\n{clip[:400]}...",
                                urgency="normal",
                                user_commanded=False
                            )
                    time.sleep(15)
                except Exception:
                    time.sleep(15)

        self._thread = threading.Thread(target=_shadow_loop, daemon=True)
        self._thread.start()
        return "Silent Shadow Co-Pilot is now actively monitoring in the background, Sir."

    def stop(self) -> str:
        self.is_active = False
        return "Silent Shadow Co-Pilot paused, Sir."


# Singleton
_shadow_copilot: Optional[SilentShadowCopilot] = None


def get_shadow_copilot() -> SilentShadowCopilot:
    global _shadow_copilot
    if _shadow_copilot is None:
        _shadow_copilot = SilentShadowCopilot()
    return _shadow_copilot
