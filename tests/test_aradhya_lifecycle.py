"""
Tests for Aradhya AI Agent Lifecycle, Post-Command Work Completion,
New Work Inquiry, Proactive Idea Permission Protocol, and Launcher Conversation Tracking.
"""

import os
import json
import pytest
from pathlib import Path

from config.settings import JarvisConfig, load_config
from core.agent import JarvisAgent
from core.offline_commander import OfflineCommander
from ui.cli import save_conversation_turn, render_conversation_panel


def test_agent_name_is_aradhya():
    """Verify that the agent name is Aradhya by default."""
    cfg = JarvisConfig()
    assert cfg.agent_name == "Aradhya"

    loaded_cfg = load_config()
    assert loaded_cfg.agent_name == "Aradhya"


def test_offline_commander_post_command_lifecycle_gujarati():
    """Verify post-command work-done confirmation and next-work inquiry in Gujarati."""
    commander = OfflineCommander()
    commander.config.language = "gujarati"
    res = commander.execute_offline_turn("વોલ્યુમ વધારો")

    assert "કામ સફળતાપૂર્વક પૂર્ણ થઈ ગયું છે, સાહેબ" in res
    assert "બીજું કોઈ કામ છે, સાહેબ?" in res
    assert "નવો આઈડિયા/સજેશન" in res or "જણાવી શકું" in res


def test_offline_commander_post_command_lifecycle_english():
    """Verify post-command work-done confirmation and next-work inquiry in English."""
    commander = OfflineCommander()
    commander.config.language = "english"
    res = commander.execute_offline_turn("volume up")

    assert "Work completed successfully, Sir." in res
    assert "Is there any other work for me, Sir?" in res
    assert "new idea/suggestion" in res or "may I share it" in res.lower()


def test_offline_commander_permission_granted():
    """Verify that Aradhya presents the idea when permission is granted by user."""
    commander = OfflineCommander()
    commander.config.language = "gujarati"
    res = commander.execute_offline_turn("હા જણાવો")

    assert "આઈડિયા" in res or "સરપ્રાઈઝ" in res
    assert "Alpesh Sir" in res or "જી સાહેબ" in res


def test_offline_commander_standby_on_no_work():
    """Verify polite standby when user has no further work."""
    commander = OfflineCommander()
    commander.config.language = "gujarati"
    res = commander.execute_offline_turn("ના, કંઈ નહીં")

    assert "સ્ટેન્ડબાય" in res or "તૈયાર" in res
    assert "જી સાહેબ" in res


def test_launcher_conversation_save_and_display(tmp_path):
    """Verify that conversation turns are saved and can be displayed in launcher."""
    cfg = JarvisConfig(base_dir=tmp_path)
    agent = JarvisAgent(cfg)

    save_conversation_turn(
        agent=agent,
        user_text="લેપટોપ ઝડપી બનાવો",
        is_voice=True,
        tools_used=[{"name": "boost_laptop_to_max_speed", "preview": "Reclaimed 120MB"}],
        response="કામ પૂર્ણ થઈ ગયું છે સાહેબ."
    )

    conv_file = tmp_path / "conversation_history.json"
    assert conv_file.exists()

    with open(conv_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == 1
    assert data[0]["user"] == "લેપટોપ ઝડપી બનાવો"
    assert data[0]["mode"] == "voice"
    assert data[0]["tools"][0]["name"] == "boost_laptop_to_max_speed"
    assert data[0]["response"] == "કામ પૂર્ણ થઈ ગયું છે સાહેબ."


def test_desktop_launchers_exist():
    """Verify that Aradhya desktop launchers and assets exist and legacy Arohi files are removed."""
    desktop_file = Path("/home/alpesh/Desktop/Aradhya.desktop")
    app_file = Path("/home/alpesh/.local/share/applications/aradhya.desktop")
    svg_file = Path("/home/alpesh/jarvis-agent/assets/aradhya.svg")

    assert desktop_file.exists()
    assert app_file.exists()
    assert svg_file.exists()

    # Legacy Arohi files must be deleted
    legacy_desktop = Path("/home/alpesh/Desktop/Arohi.desktop")
    legacy_app = Path("/home/alpesh/.local/share/applications/arohi.desktop")
    assert not legacy_desktop.exists()
    assert not legacy_app.exists()
