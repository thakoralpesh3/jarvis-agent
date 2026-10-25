"""
Tests for Stark Daily Startup Briefing Engine.
"""

import pytest
from core.briefing import DailyBriefingEngine
from tools.briefing_tools import get_daily_briefing


def test_generate_startup_briefing():
    engine = DailyBriefingEngine()
    briefing = engine.generate_startup_briefing()
    assert isinstance(briefing, dict)
    assert "speech_text" in briefing
    assert "markdown_hud" in briefing
    assert "greeting" in briefing
    assert "STARK INDUSTRIES DAILY BRIEFING" in briefing["markdown_hud"]


def test_deliver_briefing_tool():
    res = get_daily_briefing()
    assert isinstance(res, str)
    assert "DAILY BRIEFING" in res
