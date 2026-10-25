"""
Tests for Aradhya's Offline Autonomous Command Engine and Failover.
"""

import os
import pytest
from unittest.mock import MagicMock, patch

from core.offline_commander import OfflineCommander
from config.settings import JarvisConfig


def test_offline_volume_commands():
    commander = OfflineCommander(JarvisConfig())

    # Mute (Gujarati)
    res_gu = commander.execute_offline_turn("અવાજ બંધ કરો")
    assert "મ્યૂટ" in res_gu or "audio mute" in res_gu.lower()

    # Mute (English)
    cfg_en = JarvisConfig(language="english")
    cmd_en = OfflineCommander(cfg_en)
    res_en = cmd_en.execute_offline_turn("mute volume")
    assert "mute" in res_en.lower()

    # Volume Up
    res_up = commander.execute_offline_turn("વોલ્યુમ વધારો")
    assert "વોલ્યુમ" in res_up or "volume" in res_up.lower()

    # Set specific volume
    res_set = cmd_en.execute_offline_turn("set volume to 40")
    assert "40%" in res_set


def test_offline_brightness_commands():
    commander = OfflineCommander(JarvisConfig())
    res = commander.execute_offline_turn("બ્રાઇટનેસ વધારો")
    assert "બ્રાઇટનેસ" in res or "brightness" in res.lower()


def test_offline_battery_command():
    commander = OfflineCommander(JarvisConfig())
    res = commander.execute_offline_turn("બેટરી કેટલી છે?")
    assert "બેટરી" in res or "battery" in res.lower()


def test_offline_sluggishness_and_boost():
    commander = OfflineCommander(JarvisConfig())
    # Gujarati sluggishness
    res_gu = commander.execute_offline_turn("લેપટોપ બહુ ધીમું ચાલે છે, સ્પીડ બૂસ્ટ કરો")
    assert "ઓપ્ટિમાઇઝેશન" in res_gu or "optimization" in res_gu.lower() or "બૂસ્ટ" in res_gu or "speed" in res_gu.lower()

    # English boost
    cfg_en = JarvisConfig(language="english")
    cmd_en = OfflineCommander(cfg_en)
    res_en = cmd_en.execute_offline_turn("boost laptop performance, clean background processes")
    assert "optimization" in res_en.lower() or "terminated" in res_en.lower() or "speed" in res_en.lower()


def test_offline_process_termination():
    commander = OfflineCommander(JarvisConfig())
    res = commander.execute_offline_turn("kill process nonexistent_test_proc_123")
    assert "nonexistent_test_proc_123" in res


def test_offline_lock_screen():
    commander = OfflineCommander(JarvisConfig())
    res = commander.execute_offline_turn("સ્ક્રીન લોક કરો")
    assert "લૉક" in res or "locked" in res.lower()


def test_offline_disk_usage():
    commander = OfflineCommander(JarvisConfig())
    res = commander.execute_offline_turn("ડિસ્ક સ્ટોરેજ કેટલી ખાલી છે?")
    assert "ડિસ્ક" in res or "disk" in res.lower() or "storage" in res.lower()


def test_offline_date_time():
    commander = OfflineCommander(JarvisConfig())
    res = commander.execute_offline_turn("સમય શું થયો છે?")
    assert "સમય" in res or "time" in res.lower() or "202" in res


def test_offline_shell_execution():
    commander = OfflineCommander(JarvisConfig())
    res = commander.execute_offline_turn("run echo hello_aradhya_offline")
    assert "hello_aradhya_offline" in res


def test_offline_fallback_query():
    commander = OfflineCommander(JarvisConfig())
    res = commander.execute_offline_turn("explain quantum mechanics in detail")
    assert "ઑફલાઇન" in res or "offline" in res.lower()


def test_agent_run_turn_offline_failover():
    from core.agent import JarvisAgent
    cfg = JarvisConfig()
    agent = JarvisAgent(cfg)

    # Force network check to return False (simulating complete offline state)
    with patch("core.agent.check_internet_connection", return_value=False):
        res = agent.run_turn("બેટરી સ્ટેટસ ચેક કરો")
        assert isinstance(res, str)
        assert len(res) > 0
        assert "બેટરી" in res or "battery" in res.lower()


def test_offline_hang_and_lag_commands():
    commander = OfflineCommander(JarvisConfig())
    # Gujarati hang command
    res_gu = commander.execute_offline_turn("લેપટોપ બહુ હેંગ થાય છે, પ્રોબ્લેમ સોલ્વ કરો")
    assert "હેંગિંગ" in res_gu or "HANG" in res_gu or "સુધારી" in res_gu

    # English lag command
    cfg_en = JarvisConfig(language="english")
    cmd_en = OfflineCommander(cfg_en)
    res_en = cmd_en.execute_offline_turn("laptop keep lagging and freezing, fix it immediately")
    assert "hang" in res_en.lower() or "lag" in res_en.lower() or "remediation" in res_en.lower()

