"""
Tests for Aradhya Work StayAwake Sentry (AwakeGuard) & Sleep Prevention Subsystem.
"""

import os
import pytest
from unittest.mock import MagicMock, patch

from core.stay_awake_sentry import StayAwakeSentry, WORK_PROCESS_PATTERNS
from tools.stay_awake_tools import inspect_stay_awake_status, toggle_force_stay_awake
from core.offline_commander import OfflineCommander
from config.settings import JarvisConfig


def test_stay_awake_patterns():
    assert "antigravity" in WORK_PROCESS_PATTERNS
    assert "libreoffice" in WORK_PROCESS_PATTERNS
    assert "code" in WORK_PROCESS_PATTERNS
    assert "gnome-terminal" in WORK_PROCESS_PATTERNS


def test_detect_active_work():
    sentry = StayAwakeSentry()
    is_active, active_apps = sentry.detect_active_work()
    assert isinstance(is_active, bool)
    assert isinstance(active_apps, list)
    # On the live test environment, antigravity or pytest/python is running
    assert is_active is True
    assert len(active_apps) > 0


def test_engage_and_release_inhibitors():
    sentry = StayAwakeSentry()
    # Engage inhibitors
    success = sentry.engage_inhibitors(reason="Test work active")
    assert sentry.is_inhibited is True
    assert "Test work" in sentry.status_reason

    # Release inhibitors
    released = sentry.release_inhibitors()
    assert released is True
    assert sentry.is_inhibited is False
    assert sentry.dbus_cookie is None
    assert sentry.systemd_inhibit_proc is None


def test_evaluate_and_sync():
    sentry = StayAwakeSentry()
    sync_res = sentry.evaluate_and_sync()
    assert isinstance(sync_res, dict)
    assert "is_active" in sync_res
    assert "is_inhibited" in sync_res
    assert "active_apps" in sync_res
    assert "action_taken" in sync_res

    # Cleanup after test
    sentry.release_inhibitors()


def test_force_mode():
    sentry = StayAwakeSentry()
    # Force on with duration
    msg_on = sentry.set_force_mode(enable=True, duration_minutes=15)
    assert "FORCED ON" in msg_on
    assert sentry.force_stay_awake is True
    assert sentry.is_inhibited is True

    # Force off
    msg_off = sentry.set_force_mode(enable=False)
    assert "DISABLED" in msg_off
    assert sentry.force_stay_awake is False

    # Cleanup
    sentry.release_inhibitors()


def test_inspect_stay_awake_status_tool():
    report = inspect_stay_awake_status()
    assert isinstance(report, str)
    assert "Aradhya Work StayAwake Sentry Status" in report
    assert "Protection State:" in report
    assert "Detected Active Work Applications" in report


def test_toggle_force_stay_awake_tool():
    # Toggle off to restore auto
    res = toggle_force_stay_awake(enable=False)
    assert isinstance(res, str)
    assert "Aradhya StayAwake Mode Updated" in res
    assert "ઓટોમેટિક વર્ક ડિટેક્શન" in res


def test_offline_commander_stay_awake_gujarati():
    commander = OfflineCommander(JarvisConfig())
    # Gujarati command: Do not let it sleep during work
    res_gu = commander.execute_offline_turn("કામ ચાલુ હોય ત્યારે સ્લીપ કે લોકસ્ક્રીન ન થવા દો")
    assert "સ્ટે-અવેક" in res_gu or "StayAwake" in res_gu or "સ્લીપ" in res_gu

    # Status check
    res_stat = commander.execute_offline_turn("સ્ટે અવેક સ્ટેટસ ચેક કરો")
    assert "સ્ટે અવેક" in res_stat or "StayAwake" in res_stat or "Protection State" in res_stat


def test_offline_commander_stay_awake_english():
    cfg_en = JarvisConfig(language="english")
    cmd_en = OfflineCommander(cfg_en)
    res_en = cmd_en.execute_offline_turn("if there is any work going on, do not let it go to sleep or lockscreen")
    assert "stayawake" in res_en.lower() or "sleep" in res_en.lower() or "awake" in res_en.lower()
