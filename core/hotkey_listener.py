"""
Global Desktop Hotkey Summoner for JARVIS.
Allows invoking JARVIS from anywhere on the laptop via a quick floating prompt dialog or voice command.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from config.settings import load_config
from tools.ironman_protocols import play_stark_sound
from tools.laptop_work_tools import send_desktop_notification


def summon_quick_prompt() -> None:
    """Launch quick floating desktop entry dialog to give orders to JARVIS."""
    play_stark_sound("protocol")
    
    if shutil.which("zenity") and os.getenv("DISPLAY"):
        try:
            cmd = [
                "zenity",
                "--entry",
                "--title=Aradhya Quick Command",
                "--text=Sir, what are your orders?",
                "--width=450"
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                user_cmd = res.stdout.strip()
                from core.agent import JarvisAgent
                agent = JarvisAgent(load_config())
                response = agent.run_turn(user_cmd)
                
                send_desktop_notification(
                    f"Aradhya: {user_cmd[:30]}",
                    response[:120] + "...",
                    details=f"Command: {user_cmd}\n\nResponse:\n{response}",
                    urgency="normal"
                )
        except Exception:
            pass


if __name__ == "__main__":
    summon_quick_prompt()
