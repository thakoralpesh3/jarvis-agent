"""
Tests for Process Supervisor and Crash Watchdog.
"""

import sys
import tempfile
from pathlib import Path
import pytest
from core.supervisor import ProcessSupervisor


def test_supervisor_init():
    sup = ProcessSupervisor(target_cmd=["python3", "--version"])
    assert sup.max_restarts == 10
    assert sup.target_cmd == ["python3", "--version"]


def test_supervisor_log_crash(tmp_path):
    sup = ProcessSupervisor()
    sup._log_crash(1, "Test error message")
    from config.settings import DEFAULT_CONFIG_DIR
    crash_log = DEFAULT_CONFIG_DIR / "crash.log"
    assert crash_log.exists()
    content = crash_log.read_text(encoding="utf-8")
    assert "exit code 1" in content


def test_supervisor_clean_exit():
    # Target command exits with code 0 -> supervisor terminates cleanly with code 0
    sup = ProcessSupervisor(target_cmd=[sys.executable, "-c", "import sys; sys.exit(0)"])
    res = sup.run()
    assert res == 0
