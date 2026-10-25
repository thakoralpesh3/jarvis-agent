"""
Tests for Interactive Notification Manager and Click-to-View Details.
"""

import tempfile
from pathlib import Path
import pytest
from core.notification_manager import NotificationManager
from tools.laptop_work_tools import view_recent_notifications, open_notification_details


@pytest.fixture
def tmp_notif_mgr():
    with tempfile.TemporaryDirectory() as tmpdir:
        notif_dir = Path(tmpdir) / "notifications"
        mgr = NotificationManager(notif_dir=notif_dir)
        mgr.history_file = Path(tmpdir) / "history.json"
        mgr._ensure_history_file()
        yield mgr


def test_send_and_get_notification(tmp_notif_mgr):
    mgr = tmp_notif_mgr
    res = mgr.send_interactive_notification(
        title="Test Build Success",
        message="Project compiled in 1.2s",
        details="Full compiler output:\n- 12 modules verified\n- 0 syntax errors\n- Artifact: main.py",
        urgency="normal"
    )

    history = mgr.get_history(limit=5)
    assert len(history) == 1
    assert history[0]["title"] == "Test Build Success"
    assert "12 modules verified" in history[0]["details"]
    assert Path(history[0]["details_file"]).exists()


def test_view_recent_notifications_tool():
    res = view_recent_notifications(limit=5)
    assert isinstance(res, str)
    assert len(res) > 0


def test_open_notification_details_not_found():
    res = open_notification_details("invalid_id_999")
    assert "not found" in res


def test_unsolicited_chamunda_notification_suppression(tmp_notif_mgr):
    mgr = tmp_notif_mgr
    # Unsolicited Chamunda notification should be strictly suppressed
    res = mgr.send_interactive_notification(
        title="Chamunda Stock Alert",
        message="Royal Enfield Oil Filter low stock",
        user_commanded=False
    )
    assert "suppressed" in res.lower() or "silenced" in res.lower()

    # Explicitly commanded notification should be allowed
    res_cmd = mgr.send_interactive_notification(
        title="Chamunda Stock Report",
        message="Requested Royal Enfield stock data",
        user_commanded=True
    )
    assert "dispatched" in res_cmd.lower()

