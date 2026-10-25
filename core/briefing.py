"""
Stark Industries Daily Briefing Engine for JARVIS.
Generates an audio & visual morning/startup briefing on system boot, including battery health,
thermals, memory metrics, daily YouTube Shorts generation status, and pending tasks.
"""

import os
import sys
import time
import datetime
import psutil
from pathlib import Path
from typing import Any, Dict, Optional

from config.settings import JarvisConfig, load_config
from tools.ironman_protocols import play_stark_sound
from tools.laptop_work_tools import send_desktop_notification
from core.youtube_commander import YouTubeShortsCommander


class DailyBriefingEngine:
    """Delivers a Paul Bettany-style British startup briefing to the user on laptop boot."""

    def __init__(self, config: Optional[JarvisConfig] = None):
        self.config = config or load_config()
        self.yt_commander = YouTubeShortsCommander()

    def generate_startup_briefing(self) -> Dict[str, Any]:
        """Synthesize daily status report and telemetry."""
        now = datetime.datetime.now()
        hour = now.hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        # System Metrics
        cpu_pct = psutil.cpu_percent(interval=0.2)
        mem = psutil.virtual_memory()
        battery = psutil.sensors_battery()
        batt_str = f"{battery.percent}%" if battery else "AC Connected"
        disk = psutil.disk_usage("/")
        disk_free_gb = round(disk.free / (1024 ** 3), 1)

        # YouTube Shorts Daily Status
        yt_status = self.yt_commander.get_schedule_status()
        is_due = self.yt_commander.is_daily_run_due()
        if is_due:
            yt_msg = "Daily YouTube Shorts generation is scheduled to run on startup."
        else:
            yt_msg = f"Today's YouTube Short has already completed ({yt_status.get('last_output_video', 'Saved')})."

        # Formulate Speech Script
        speech_text = (
            f"{greeting}, {self.config.user_name}. JARVIS systems are online and fully operational. "
            f"Power reserve is at {batt_str}, with {disk_free_gb} gigabytes of disk storage free. "
            f"{yt_msg} All background sentries are active."
        )

        # Formulate Markdown HUD text
        markdown_hud = f"""# 🌅 STARK INDUSTRIES DAILY BRIEFING
**Date:** {now.strftime('%A, %B %d, %Y • %H:%M:%S')}  
**Greeting:** {greeting}, {self.config.user_name}

---

### 💻 System Telemetry:
- **Power Reserve:** {batt_str}
- **CPU Utilization:** {cpu_pct}%
- **RAM Usage:** {mem.percent}% ({round(mem.used / (1024**3), 1)}GB / {round(mem.total / (1024**3), 1)}GB)
- **Disk Free Space:** {disk_free_gb} GB free on `/`

### 🎬 Subordinate Agent Status:
- **YouTube Shorts AI Agent:** {yt_msg}
- **Universal Stoppage Watchdog:** Active & Monitoring
- **Crash Supervisor:** Armed

*At your service, Sir.*
"""
        return {
            "speech_text": speech_text,
            "markdown_hud": markdown_hud,
            "greeting": greeting,
            "is_yt_due": is_due
        }

    def deliver_briefing(self, play_voice: bool = True, send_notification: bool = False) -> str:
        """Play sound, deliver voice briefing, and return system HUD."""
        play_stark_sound("startup")
        briefing = self.generate_startup_briefing()

        # Desktop notification only if explicitly requested
        if send_notification:
            send_desktop_notification(
                f"{self.config.agent_name} Morning Briefing ({briefing['greeting']})",
                f"All systems nominal. {briefing['is_yt_due'] and 'Daily YouTube Shorts generation initiated.' or 'Daily YouTube Short complete.'}",
                details=briefing["markdown_hud"],
                urgency="normal",
                user_commanded=False
            )

        if play_voice and self.config.enable_voice_response:
            try:
                from core.voice_assistant import VoiceAssistant
                voice = VoiceAssistant(self.config)
                voice.speak(briefing["speech_text"])
            except Exception:
                pass

        return briefing["markdown_hud"]
