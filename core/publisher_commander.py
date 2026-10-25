"""
PublisheR AI Agent Commander & Daily Supervision Engine for Aradhya AI (JARVIS).
Integrates /home/alpesh/book-publishing-agent under Aradhya's command,
running daily trending book publication headlessly, supervising execution,
and ensuring Amazon KDP & Flipkart assets are completely generated.
"""

import os
import sys
import json
import time
import datetime
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from config.settings import DEFAULT_CONFIG_DIR
except Exception:
    DEFAULT_CONFIG_DIR = Path.home() / ".jarvis"

try:
    from tools.laptop_work_tools import send_desktop_notification
except Exception:
    def send_desktop_notification(title: str, message: str, user_commanded: bool = False):
        try:
            subprocess.run(["notify-send", "-a", "Aradhya", title, message], check=False)
        except Exception:
            pass

try:
    from tools.ironman_protocols import play_stark_sound
except Exception:
    def play_stark_sound(name: str):
        pass


PUBLISHER_AGENT_DIR = Path("/home/alpesh/book-publishing-agent")
PUBLISHER_SCRIPT = PUBLISHER_AGENT_DIR / "run_background_publisher.sh"
PUBLISHER_TRACKER_FILE = PUBLISHER_AGENT_DIR / "output" / "publisher_daily_tracker.json"
SCHEDULE_TRACKER_FILE = DEFAULT_CONFIG_DIR / "publisher_daily_schedule.json"


class PublisheRCommander:
    """Supreme controller and supervisor for the PublisheR AI Agent."""

    def __init__(self, publisher_dir: Path = PUBLISHER_AGENT_DIR):
        self.publisher_dir = publisher_dir
        self.schedule_file = SCHEDULE_TRACKER_FILE
        self.schedule_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schedule_file()

    def _ensure_schedule_file(self) -> None:
        if not self.schedule_file.exists():
            default_state = {
                "last_run_date": "",
                "last_run_timestamp": 0,
                "last_status": "standby",
                "last_book_title": "",
                "total_completed_books": 0,
                "history": []
            }
            self.schedule_file.write_text(json.dumps(default_state, indent=2), encoding="utf-8")

    def get_schedule_status(self) -> Dict[str, Any]:
        """Retrieve daily schedule telemetry."""
        try:
            return json.loads(self.schedule_file.read_text(encoding="utf-8") or "{}")
        except Exception:
            return {}

    def is_daily_run_due(self) -> bool:
        """Check if today's daily book publishing has already executed successfully."""
        today_str = datetime.date.today().isoformat()
        if PUBLISHER_TRACKER_FILE.exists():
            try:
                tdata = json.loads(PUBLISHER_TRACKER_FILE.read_text(encoding="utf-8") or "{}")
                if tdata.get("last_run_date") == today_str and tdata.get("runs_today_count", 0) >= tdata.get("daily_limit", 1):
                    return False
            except Exception:
                pass

        status = self.get_schedule_status()
        if status.get("last_run_date") == today_str and status.get("last_status") == "completed":
            return False

        return True

    def run_and_supervise_pipeline(
        self,
        category: Optional[str] = None,
        topic: Optional[str] = None,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Execute and supervise the PublisheR AI pipeline autonomously in the background.
        Drafts manuscript, interior PDF, cover wrap, Amazon & Flipkart listings.
        """
        if not self.publisher_dir.exists() or not PUBLISHER_SCRIPT.exists():
            return {"success": False, "error": f"PublisheR script not found at {PUBLISHER_SCRIPT}"}

        today_str = datetime.date.today().isoformat()
        if not force and not self.is_daily_run_due():
            return {
                "success": True,
                "status": "already_completed",
                "message": f"PublisheR AI has already published today's book for {today_str}."
            }

        play_stark_sound("protocol")
        send_desktop_notification(
            "Aradhya Autonomous Subagent Directive",
            "Commanding PublisheR AI: Initiating background book publishing pipeline...",
            user_commanded=False
        )

        cmd = ["bash", str(PUBLISHER_SCRIPT)]
        if force:
            cmd.append("--force")
        if category:
            cmd.extend(["--category", category])
        if topic:
            cmd.extend(["--topic", topic])

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(self.publisher_dir),
                capture_output=True,
                text=True,
                timeout=1200
            )

            if proc.returncode == 0:
                # Update schedule
                status_data = self.get_schedule_status()
                status_data["last_run_date"] = today_str
                status_data["last_run_timestamp"] = time.time()
                status_data["last_status"] = "completed"
                status_data["total_completed_books"] = status_data.get("total_completed_books", 0) + 1

                # Parse last book title from tracker if available
                if PUBLISHER_TRACKER_FILE.exists():
                    try:
                        tdata = json.loads(PUBLISHER_TRACKER_FILE.read_text(encoding="utf-8") or "{}")
                        status_data["last_book_title"] = tdata.get("last_book_title", "")
                    except Exception:
                        pass

                history_entry = {
                    "date": today_str,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "completed",
                    "details": "Autonomous execution succeeded"
                }
                status_data["history"] = (status_data.get("history", []) + [history_entry])[-30:]
                self.schedule_file.write_text(json.dumps(status_data, indent=2), encoding="utf-8")

                send_desktop_notification(
                    "Aradhya Autonomous Production Complete",
                    f"PublisheR AI completed today's book: {status_data.get('last_book_title', 'Daily Book')}",
                    user_commanded=False
                )
                return {"success": True, "status": "completed", "details": status_data}
            else:
                return {"success": False, "status": "failed", "error": proc.stderr[-500:] if proc.stderr else "Unknown error"}

        except Exception as e:
            return {"success": False, "status": "error", "error": str(e)}
