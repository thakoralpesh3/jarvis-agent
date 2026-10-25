"""
Tests for YouTube Shorts AI Agent Commander and Daily Schedule Supervision.
"""

import tempfile
from pathlib import Path
import pytest
from core.youtube_commander import YouTubeShortsCommander


@pytest.fixture
def tmp_yt_commander():
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_yt_dir = Path(tmpdir) / "youtube-agent"
        fake_yt_dir.mkdir(parents=True, exist_ok=True)
        (fake_yt_dir / "output").mkdir(parents=True, exist_ok=True)
        
        commander = YouTubeShortsCommander(youtube_dir=fake_yt_dir)
        commander.schedule_file = Path(tmpdir) / "schedule.json"
        commander._ensure_schedule_file()
        yield commander


def test_schedule_status(tmp_yt_commander):
    commander = tmp_yt_commander
    status = commander.get_schedule_status()
    assert isinstance(status, dict)
    assert status.get("last_status") == "standby"
    assert commander.is_daily_run_due() is True


def test_update_schedule_status(tmp_yt_commander):
    commander = tmp_yt_commander
    commander._update_schedule_status("completed", video_path="/fake/video.mp4", details="Test success")
    
    status = commander.get_schedule_status()
    assert status.get("last_status") == "completed"
    assert status.get("total_completed_shorts") == 1
    assert commander.is_daily_run_due() is False
