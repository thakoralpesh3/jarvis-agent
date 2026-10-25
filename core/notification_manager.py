"""
Interactive Desktop Notification Subsystem with Click-to-View Details for JARVIS.
Dispatches native Linux desktop notifications with rich inline contents and interactive action triggers.
When the user clicks the notification or 'View Details', a rich Stark HUD details dialog
immediately displays full logs, task telemetry, diagnostics, or file details.
"""

import os
import sys
import json
import time
import uuid
import shutil
import threading
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.settings import DEFAULT_CONFIG_DIR
from tools.ironman_protocols import play_stark_sound


NOTIF_DIR = DEFAULT_CONFIG_DIR / "notifications"
NOTIF_HISTORY_FILE = DEFAULT_CONFIG_DIR / "notification_history.json"
ICON_PATH = "/home/alpesh/jarvis-agent/assets/jarvis.svg"


class NotificationManager:
    """Manages interactive desktop notifications and click-to-view details dialogs."""

    def __init__(self, notif_dir: Path = NOTIF_DIR):
        self.notif_dir = notif_dir
        self.notif_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = NOTIF_HISTORY_FILE
        self._ensure_history_file()

    def _ensure_history_file(self) -> None:
        if not self.history_file.exists():
            self.history_file.write_text("[]", encoding="utf-8")

    def _record_history(self, entry: Dict[str, Any]) -> None:
        try:
            items = self.get_history(limit=100)
            items.insert(0, entry)
            self.history_file.write_text(json.dumps(items[:50], indent=2), encoding="utf-8")
        except Exception:
            pass

    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve recent notification records."""
        try:
            data = json.loads(self.history_file.read_text(encoding="utf-8") or "[]")
            return data[:limit]
        except Exception:
            return []

    def show_details_dialog(self, title: str, details_text: str, details_file: Optional[Path] = None) -> None:
        """
        Display a rich graphical details modal on the user's desktop with full telemetry and action options.
        """
        play_stark_sound("protocol")
        
        # Ensure details file exists
        if not details_file or not details_file.exists():
            tmp_file = self.notif_dir / f"details_{int(time.time())}.txt"
            tmp_file.write_text(details_text, encoding="utf-8")
            details_file = tmp_file

        env = os.environ.copy()
        if "DISPLAY" not in env or not env["DISPLAY"]:
            env["DISPLAY"] = ":0"

        from config.settings import load_config
        cfg = load_config()
        agent_name = getattr(cfg, "agent_name", "Aradhya")

        if shutil.which("zenity"):
            try:
                cmd = [
                    "zenity",
                    "--text-info",
                    f"--title={agent_name} Telemetry: {title}",
                    f"--filename={str(details_file)}",
                    "--width=720",
                    "--height=560",
                    "--ok-label=Dismiss",
                    "--cancel-label=📋 Copy to Clipboard"
                ]
                res = subprocess.run(cmd, env=env, capture_output=True, text=True)
                # If user clicked Cancel / Copy to Clipboard (returncode 1 in zenity)
                if res.returncode == 1:
                    try:
                        from tools.laptop_tools import set_clipboard_content
                        set_clipboard_content(details_text)
                        play_stark_sound("ack")
                    except Exception:
                        pass
                return
            except Exception:
                pass

        # Fallback print if no GUI
        print(f"\n" + "=" * 60)
        print(f"📊 [{agent_name} NOTIFICATION DETAILS: {title}]")
        print(details_text)
        print("=" * 60 + "\n")

    def _wait_and_handle_click(self, proc: subprocess.Popen, title: str, details_text: str, details_file: Path) -> None:
        """Background thread handler that waits for user click on notification action."""
        try:
            stdout, _ = proc.communicate(timeout=60)
            action = stdout.strip().lower()
            # If user clicked anywhere on notification (default), clicked View Details button (details), or clicked 0
            if action and (action in ("details", "0", "default", "view details") or "detail" in action):
                if action != "dismiss":
                    self.show_details_dialog(title, details_text, details_file)
        except subprocess.TimeoutExpired:
            proc.kill()
        except Exception:
            pass

    def send_interactive_notification(
        self,
        title: str,
        message: str,
        details: Optional[str] = None,
        urgency: str = "normal",
        action_label: str = "🔍 View Details",
        user_commanded: bool = False
    ) -> str:
        """
        Send a desktop notification with rich inline content and click-to-view details modal.
        Respects user quiet-mode directive: unsolicited background notifications are silenced
        until explicitly commanded by the user.
        
        Args:
            title: Title header of the notification banner.
            message: Brief summary text displayed on the desktop banner.
            details: Comprehensive multi-line details, logs, diagnostics, or file paths.
            urgency: 'low', 'normal', or 'critical'.
            action_label: Button label on the notification banner.
            user_commanded: Set True only when explicitly requested by user command.
        """
        notif_id = f"notif_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")

        # Combine message and core details so the notification banner itself immediately displays related contents!
        banner_body = message
        if details and details.strip() != message.strip():
            # Extract first 3 lines of rich details for immediate banner visibility
            clean_details = "\n".join(line for line in details.splitlines() if not line.startswith("###") and not line.startswith("==="))[:280]
            if clean_details and clean_details not in message:
                banner_body = f"{message}\n\n{clean_details}"

        from config.settings import load_config
        cfg = load_config()
        agent_name = getattr(cfg, "agent_name", "Aradhya")

        # Format full multi-line details text for the modal popup
        full_details = f"""======================================================================
{agent_name.upper()} • NOTIFICATION TELEMETRY REPORT
======================================================================
📌 Event:       {title}
⏰ Timestamp:   {timestamp_str}
⚡ Urgency:     {urgency.upper()}
----------------------------------------------------------------------
📝 Summary:
{message}
----------------------------------------------------------------------
🔍 In-Depth Details & Complete Context:
{details or message}
======================================================================
"""
        # Save details file to disk
        details_file = self.notif_dir / f"{notif_id}.txt"
        details_file.write_text(full_details, encoding="utf-8")

        # Save to history
        self._record_history({
            "id": notif_id,
            "title": title,
            "message": message,
            "details": details or message,
            "timestamp": timestamp_str,
            "details_file": str(details_file),
            "urgency": urgency,
            "user_commanded": user_commanded
        })

        # Strict user directive: Suppress Chamunda / Royal Enfield / Workshop IoT notifications unless explicitly commanded by user!
        full_content = f"{title} {message} {details or ''}".lower()
        chamunda_re_terms = [
            "chamunda", "royal enfield", "re predictive", "workshop iot",
            "hunter 350", "classic 350", "bullet 350", "continental gt",
            "interceptor", "himalayan", "meteor 350", "re acoustic",
            "ecu obd", "dtc code", "spares catalog", "job card"
        ]
        if any(term in full_content for term in chamunda_re_terms):
            if not user_commanded:
                return "Notification suppressed (Chamunda / Royal Enfield notifications silenced until explicitly commanded)."

        if not user_commanded and not getattr(cfg, "allow_unsolicited_notifications", False):
            return f"Notification logged to telemetry history (Quiet Mode active: Screen popups silenced until explicitly commanded)."

        urg = urgency.lower() if urgency.lower() in ["low", "normal", "critical"] else "normal"

        # Suppress live desktop popups during automated tests
        if os.getenv("PYTEST_CURRENT_TEST") or os.getenv("TESTING"):
            return f"Notification dispatched: '{title}'. Related contents displayed on banner and in full modal."

        if shutil.which("notify-send"):
            try:
                env = os.environ.copy()
                if "DISPLAY" not in env or not env["DISPLAY"]:
                    env["DISPLAY"] = ":0"

                cmd = [
                    "notify-send",
                    "-t", "15000",  # Stay visible for 15 seconds
                    "-u", urg,
                    "-a", agent_name,
                    "--action=default=" + action_label,
                    "--action=details=" + action_label,
                    "--action=dismiss=Dismiss"
                ]
                if os.path.exists(ICON_PATH):
                    cmd.extend(["-i", ICON_PATH])
                cmd.extend([title, banner_body])

                proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
                
                # Spawn non-blocking background listener for click action
                t = threading.Thread(
                    target=self._wait_and_handle_click,
                    args=(proc, title, full_details, details_file),
                    daemon=True
                )
                t.start()

                return f"Notification dispatched: '{title}'. Related contents displayed on banner and in full modal."
            except Exception as e:
                return f"Notification dispatch error: {str(e)}"

        return f"Notification logged to {details_file}."

    def show_notification_center_gui(self) -> str:
        """Open a Zenity interactive list of all recent notifications with their details."""
        history = self.get_history(limit=25)
        if not history:
            return "No recent notifications in history, Sir."

        env = os.environ.copy()
        if "DISPLAY" not in env or not env["DISPLAY"]:
            env["DISPLAY"] = ":0"

        if shutil.which("zenity"):
            try:
                cmd = [
                    "zenity",
                    "--list",
                    "--title=JARVIS Notification Center",
                    "--text=Select any notification to inspect full telemetry and details:",
                    "--column=ID",
                    "--column=Time",
                    "--column=Title",
                    "--column=Summary",
                    "--width=750",
                    "--height=450",
                    "--ok-label=🔍 Open Details",
                    "--cancel-label=Close"
                ]
                for n in history:
                    cmd.extend([n["id"], n["timestamp"], n["title"], n["message"][:60]])

                res = subprocess.run(cmd, env=env, capture_output=True, text=True)
                selected_id = res.stdout.strip()
                if selected_id:
                    for n in history:
                        if n["id"] == selected_id:
                            self.show_details_dialog(n["title"], n["details"], Path(n.get("details_file", "")))
                            break
                return "Notification Center closed."
            except Exception as e:
                return f"Error opening Notification Center: {str(e)}"

        return "\n".join(f"- [{n['timestamp']}] **{n['title']}**: {n['message']}" for n in history)


# Global singleton instance
_notification_mgr: Optional[NotificationManager] = None


def get_notification_manager() -> NotificationManager:
    global _notification_mgr
    if _notification_mgr is None:
        _notification_mgr = NotificationManager()
    return _notification_mgr
