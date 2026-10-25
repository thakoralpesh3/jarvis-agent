"""
Tests for JARVIS Background Daemon.
"""

import tempfile
from pathlib import Path
import pytest

from core.daemon import JarvisDaemon
from config.settings import JarvisConfig


def test_daemon_lifecycle():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        cfg = JarvisConfig(
            base_dir=base,
            pid_file=base / "test_jarvis.pid",
            log_file=base / "test_daemon.log"
        )
        daemon = JarvisDaemon(cfg)

        # 1. Initial status (should be not running)
        running, pid = daemon.is_running()
        assert running is False
        assert pid is None
        assert "STANDBY" in daemon.status()

        # 2. Status message format
        status_msg = daemon.status()
        assert "Aradhya Background Daemon" in status_msg

        # 3. Get logs on empty file
        logs = daemon.get_logs()
        assert isinstance(logs, str)

        # 4. Background queue testing
        queue_res = daemon.queue_background_task("Scan disk and cleanup temp cache")
        assert queue_res["task_id"].startswith("bg_")
        assert queue_res["status"] == "queued"
        assert (base / "daemon_queue.json").exists()

        # Process queue with a mock executor
        executed = []
        def mock_executor(mission):
            executed.append(mission)
            return {"status": "completed", "summary": f"Executed {mission}"}

        daemon.process_background_queue(executor_fn=mock_executor)
        assert len(executed) == 1
        assert executed[0] == "Scan disk and cleanup temp cache"
