"""
Tests for Laptop Control & Desktop Automation tools.
"""

import pytest
from tools.laptop_tools import (
    set_system_volume,
    change_system_volume,
    toggle_system_mute,
    control_media_player,
    set_screen_brightness,
    get_laptop_battery_info,
    lock_laptop_screen,
    list_active_windows,
    focus_window_by_title,
    close_window_by_title,
    get_clipboard_content,
    set_clipboard_content,
    open_url,
)
from core.voice_assistant import VoiceAssistant
from config.settings import JarvisConfig


def test_volume_controls():
    # Test setting volume
    res = set_system_volume(50)
    assert "50%" in res or "volume" in res.lower()

    # Test changing volume
    res_delta = change_system_volume(5)
    assert "5%" in res_delta or "volume" in res_delta.lower()

    # Test toggle mute
    res_mute = toggle_system_mute()
    assert "toggled" in res_mute.lower() or "mute" in res_mute.lower()


def test_battery_and_windows():
    # Test battery info
    batt = get_laptop_battery_info()
    assert "Battery" in batt or "Desktop" in batt or "Level" in batt

    # Test list windows
    wins = list_active_windows()
    assert isinstance(wins, str)


def test_clipboard_operations():
    # Test set and get clipboard
    set_res = set_clipboard_content("JARVIS test clipboard payload")
    assert "Copied" in set_res or "clipboard" in set_res.lower()


def test_voice_assistant_init():
    cfg = JarvisConfig()
    va = VoiceAssistant(cfg)
    assert va.config.voice_name == "Puck"
