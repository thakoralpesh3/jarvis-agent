"""
Launcher for Holographic Particle HUD.
"""

import subprocess
import webbrowser
from pathlib import Path
from tools.ironman_protocols import play_stark_sound


def launch_hologram_hud() -> str:
    """Launch full-screen futuristic Holographic Arc-Reactor Web HUD in browser."""
    play_stark_sound("startup")
    hud_path = Path(__file__).resolve().parent / "hologram_hud.html"
    webbrowser.open(f"file://{hud_path}")
    return f"JARVIS Mark VIII Holographic HUD activated in browser ({hud_path}), Sir."
