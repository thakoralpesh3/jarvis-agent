"""
Process Supervisor and Automatic Crash Recovery Watchdog for JARVIS.
Monitors the active JARVIS agent process, automatically restarts it if any crash, error,
or unexpected termination occurs, and immediately triggers task checkpoint resumption.
"""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path
from typing import List, Optional

from config.settings import DEFAULT_CONFIG_DIR
from tools.laptop_work_tools import send_desktop_notification
from tools.ironman_protocols import play_stark_sound


CRASH_LOG = DEFAULT_CONFIG_DIR / "crash.log"


class ProcessSupervisor:
    """Supervisor that monitors JARVIS process lifecycle and auto-restarts on crash."""

    def __init__(self, target_cmd: Optional[List[str]] = None, max_restarts: int = 10,
                 restart_cooldown_sec: float = 2.0):
        self.target_cmd = target_cmd or [sys.executable, str(Path(__file__).parent.parent / "main.py")]
        self.max_restarts = max_restarts
        self.restart_cooldown_sec = restart_cooldown_sec
        self._running = True
        DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def _log_crash(self, returncode: int, stderr_text: str = "") -> None:
        """Record crash details to persistent crash log."""
        try:
            with open(CRASH_LOG, "a", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Process crashed with exit code {returncode}.\n")
                if stderr_text:
                    f.write(f"Error output:\n{stderr_text}\n")
                f.write("-" * 50 + "\n")
        except Exception:
            pass

    def run(self) -> int:
        """
        Run the supervisor loop. If the target process crashes, auto-restarts and resumes tasks.
        """
        def _handle_sig(signum, frame):
            self._running = False

        signal.signal(signal.SIGINT, _handle_sig)
        signal.signal(signal.SIGTERM, _handle_sig)

        restart_count = 0
        root_dir = str(Path(__file__).parent.parent)

        while self._running and restart_count < self.max_restarts:
            proc = subprocess.Popen(
                self.target_cmd,
                cwd=root_dir,
                env=dict(os.environ, PYTHONPATH=root_dir)
            )

            try:
                ret = proc.wait()
            except KeyboardInterrupt:
                self._running = False
                try:
                    proc.terminate()
                except Exception:
                    pass
                return 0

            if not self._running or ret == 0:
                # Normal intentional shutdown
                return 0

            # Process stopped unexpectedly or crashed (ret != 0)
            restart_count += 1
            self._log_crash(ret)

            play_stark_sound("alert")
            send_desktop_notification(
                "Aradhya Crash Recovery",
                f"Process interrupted (Code: {ret}). Watchdog automatically restarting and resuming tasks...",
                urgency="critical",
                user_commanded=False
            )

            time.sleep(self.restart_cooldown_sec)

        return 1


if __name__ == "__main__":
    sup = ProcessSupervisor()
    sys.exit(sup.run())
