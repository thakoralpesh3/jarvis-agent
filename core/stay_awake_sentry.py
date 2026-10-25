"""
Aradhya Work StayAwake Sentry (AwakeGuard) Subsystem.
Autonomously prevents laptop from sleeping, suspending, dimming, or locking the screen
whenever active work is in progress (e.g. Antigravity, LibreOffice, IDEs, active terminals,
compilers, or Aradhya background missions).
"""

import os
import sys
import time
import signal
import psutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from config.settings import JarvisConfig, load_config
from tools.ironman_protocols import play_stark_sound


# Default process names and identifiers representing active work
WORK_PROCESS_PATTERNS: Set[str] = {
    # Antigravity & AI Development
    "antigravity", "jarvis-agent", "supervisor.py",

    # Office Suites & Document Editors
    "libreoffice", "soffice.bin", "soffice", "oosplash",
    "calc", "writer", "impress", "draw", "xed", "gedit", "kate",

    # Code Editors & IDEs
    "code", "vscode", "cursor", "sublime_text", "pycharm", "idea",
    "clion", "atom", "nvim", "vim",

    # Creative, Media & Video Production
    "gimp", "inkscape", "blender", "kdenlive", "audacity", "obs",
    "ffmpeg", "mencoder",

    # Terminals & Development Runtimes
    "gnome-terminal", "gnome-terminal-server", "x-terminal-emulator",
    "alacritty", "kitty", "tmux", "screen",

    # Compilers, Package Managers & Build Tools
    "cargo", "rustc", "gcc", "g++", "clang", "make", "cmake",
    "npm", "node", "yarn", "pytest"
}


class StayAwakeSentry:
    """
    Monitors system activity and dynamically holds sleep and screensaver inhibitors
    as long as work applications are open or background missions are running.
    """

    def __init__(self, config: Optional[JarvisConfig] = None):
        self.config = config or load_config()
        self.is_inhibited: bool = False
        self.dbus_cookie: Optional[int] = None
        self.systemd_inhibit_proc: Optional[subprocess.Popen] = None
        self.last_work_apps: List[str] = []
        self.last_pulse_time: float = 0.0
        self.force_stay_awake: bool = False
        self.force_until: float = 0.0
        self.status_reason: str = "Idle (No active work)"

    def detect_active_work(self) -> Tuple[bool, List[str]]:
        """
        Scan running processes and background task queues to determine if work is in progress.
        Returns (is_active, list_of_active_work_apps).
        """
        active_apps = set()

        # 1. Check manual override timer
        if self.force_stay_awake:
            if self.force_until == 0.0 or time.time() < self.force_until:
                active_apps.add("User Manual Force Keep-Awake")
                return True, list(active_apps)
            else:
                self.force_stay_awake = False
                self.force_until = 0.0

        # 2. Check running processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                p_name = (proc.info.get('name') or '').lower()
                cmdline = " ".join(proc.info.get('cmdline') or []).lower()

                for pattern in WORK_PROCESS_PATTERNS:
                    if pattern in p_name or pattern in cmdline:
                        # Normalize readable app label
                        label = pattern
                        if "antigravity" in p_name or "antigravity" in cmdline:
                            label = "Antigravity IDE"
                        elif any(k in p_name for k in ["soffice", "libreoffice"]):
                            label = "LibreOffice Suite"
                        elif "code" in p_name or "vscode" in p_name:
                            label = "VS Code"
                        elif "cursor" in p_name:
                            label = "Cursor IDE"
                        elif "terminal" in p_name:
                            label = "Terminal Session"
                        elif "blender" in p_name:
                            label = "Blender 3D"
                        elif "gimp" in p_name:
                            label = "GIMP"
                        elif "ffmpeg" in p_name:
                            label = "Media Encoding (ffmpeg)"
                        elif "pytest" in cmdline:
                            label = "Automated Test Suite (pytest)"

                        active_apps.add(label)
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # 3. Check Aradhya background mission queue
        queue_file = self.config.base_dir / "daemon_queue.json"
        if queue_file.exists():
            try:
                import json
                tasks = json.loads(queue_file.read_text(encoding="utf-8") or "[]")
                if tasks:
                    active_apps.add(f"Aradhya Task Queue ({len(tasks)} pending)")
            except Exception:
                pass

        is_active = len(active_apps) > 0
        return is_active, sorted(list(active_apps))

    def engage_inhibitors(self, reason: str = "Active work in progress") -> bool:
        """
        Engage multi-layered sleep and screensaver inhibitors:
        1. FreeDesktop ScreenSaver D-Bus Inhibit
        2. Systemd sleep & idle inhibitor
        3. Initial X11 screensaver reset pulse
        """
        success = False

        # 1. D-Bus FreeDesktop ScreenSaver Inhibit
        if self.dbus_cookie is None:
            try:
                cmd = [
                    "gdbus", "call", "--session",
                    "--dest", "org.freedesktop.ScreenSaver",
                    "--object-path", "/org/freedesktop/ScreenSaver",
                    "--method", "org.freedesktop.ScreenSaver.Inhibit",
                    "Aradhya StayAwake Sentry", reason
                ]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
                if res.returncode == 0 and "uint32" in res.stdout:
                    # Extract cookie e.g. (uint32 580727543,)
                    cookie_str = res.stdout.replace("(", "").replace(")", "").replace("uint32", "").replace(",", "").strip()
                    if cookie_str.isdigit():
                        self.dbus_cookie = int(cookie_str)
                        success = True
            except Exception:
                pass

        # 2. Systemd Sleep & Idle Inhibit Worker Process
        if self.systemd_inhibit_proc is None or self.systemd_inhibit_proc.poll() is not None:
            try:
                cmd = [
                    "systemd-inhibit",
                    "--what=idle:sleep:handle-lid-switch",
                    "--who=Aradhya StayAwake Sentry",
                    f"--why={reason}",
                    "sleep", "infinity"
                ]
                self.systemd_inhibit_proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    preexec_fn=os.setsid
                )
                success = True
            except Exception:
                pass

        # 3. X11 Display Keep-Alive Pulse
        self.pulse_display_keepalive()

        self.is_inhibited = True
        self.status_reason = reason
        return success

    def release_inhibitors(self) -> bool:
        """
        Release all sleep and screensaver inhibitors to restore normal power management.
        """
        # 1. Release D-Bus Cookie
        if self.dbus_cookie is not None:
            try:
                cmd = [
                    "gdbus", "call", "--session",
                    "--dest", "org.freedesktop.ScreenSaver",
                    "--object-path", "/org/freedesktop/ScreenSaver",
                    "--method", "org.freedesktop.ScreenSaver.UnInhibit",
                    str(self.dbus_cookie)
                ]
                subprocess.run(cmd, capture_output=True, text=True, timeout=3)
            except Exception:
                pass
            self.dbus_cookie = None

        # 2. Terminate systemd-inhibit worker
        if self.systemd_inhibit_proc is not None:
            try:
                if self.systemd_inhibit_proc.poll() is None:
                    os.killpg(os.getpgid(self.systemd_inhibit_proc.pid), signal.SIGTERM)
                    self.systemd_inhibit_proc.wait(timeout=1.0)
            except Exception:
                try:
                    self.systemd_inhibit_proc.kill()
                except Exception:
                    pass
            self.systemd_inhibit_proc = None

        self.is_inhibited = False
        self.status_reason = "Idle (Normal sleep & lockscreen enabled)"
        return True

    def pulse_display_keepalive(self) -> bool:
        """
        Send a non-intrusive reset pulse to the X11 screensaver to prevent screen blanking.
        """
        now = time.time()
        if now - self.last_pulse_time < 30.0:
            return True

        self.last_pulse_time = now
        try:
            res = subprocess.run(["xset", "s", "reset"], capture_output=True, timeout=2)
            return res.returncode == 0
        except Exception:
            return False

    def evaluate_and_sync(self) -> Dict[str, Any]:
        """
        Evaluates current work activity and transitions inhibitor state accordingly.
        Designed to be called periodically (every 15-20 seconds) in the daemon loop.
        """
        is_active, active_apps = self.detect_active_work()
        self.last_work_apps = active_apps
        state_changed = False
        action_taken = "none"

        if is_active:
            reason = f"Work in progress: {', '.join(active_apps[:4])}"
            if not self.is_inhibited:
                self.engage_inhibitors(reason)
                state_changed = True
                action_taken = "engaged"
            else:
                # Refresh display pulse periodically
                self.pulse_display_keepalive()
                self.status_reason = reason
        else:
            if self.is_inhibited:
                self.release_inhibitors()
                state_changed = True
                action_taken = "released"

        return {
            "is_active": is_active,
            "active_apps": active_apps,
            "is_inhibited": self.is_inhibited,
            "state_changed": state_changed,
            "action_taken": action_taken,
            "reason": self.status_reason
        }

    def set_force_mode(self, enable: bool, duration_minutes: int = 0) -> str:
        """
        Explicitly forces keep-awake mode on or off.
        """
        self.force_stay_awake = enable
        if enable:
            if duration_minutes > 0:
                self.force_until = time.time() + (duration_minutes * 60)
                dur_str = f"for the next {duration_minutes} minutes"
            else:
                self.force_until = 0.0
                dur_str = "indefinitely until manually toggled"

            reason = f"Manual force keep-awake {dur_str}"
            self.engage_inhibitors(reason)
            return f"StayAwake Sentry FORCED ON: Laptop will not sleep or lock screen {dur_str}."
        else:
            self.force_until = 0.0
            self.release_inhibitors()
            # Immediately re-sync with real work state
            self.evaluate_and_sync()
            return "StayAwake Sentry Force Mode DISABLED: Automatic work detection restored."

    def get_status_report(self) -> Dict[str, Any]:
        """Detailed status report of current StayAwake Sentry."""
        is_active, active_apps = self.detect_active_work()
        return {
            "is_inhibited": self.is_inhibited,
            "is_work_active": is_active,
            "active_work_apps": active_apps,
            "dbus_cookie": self.dbus_cookie,
            "systemd_inhibit_active": (self.systemd_inhibit_proc is not None and self.systemd_inhibit_proc.poll() is None),
            "force_mode": self.force_stay_awake,
            "status_reason": self.status_reason
        }
