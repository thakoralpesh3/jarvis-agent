"""
Unit Tests for Dynamic Model Discovery & Auto-Upgrade System.
"""

import pytest
from config.settings import JarvisConfig
from core.model_manager import ModelManager, get_model_manager
from tools.model_tools import list_available_ai_models, check_and_upgrade_model, set_ai_model


def test_model_version_parsing():
    mgr = ModelManager()
    v, tier = mgr._parse_version("gemini-3.8-flash")
    assert v == 3.8
    assert tier == "flash"

    v2, tier2 = mgr._parse_version("gemini-3.1-pro-preview")
    assert v2 == 3.1
    assert tier2 == "pro"


def test_latest_model_discovery():
    mgr = ModelManager()
    latest_flash = mgr.get_latest_flash_model()
    assert "flash" in latest_flash
    assert mgr._parse_version(latest_flash)[0] >= 3.7


def test_auto_upgrade_logic():
    # Simulate an older model in config
    cfg = JarvisConfig(model_name="gemini-3.5-flash", api_key="")
    mgr = ModelManager(config=cfg)
    
    # Should detect 3.8 is newer than 3.5 and upgrade
    res = mgr.auto_upgrade_model(notify=False)
    assert res["upgraded"] is True
    assert mgr._parse_version(res["new_model"])[0] >= 3.7


def test_set_model():
    mgr = ModelManager()
    res = mgr.set_model("gemini-3.8-flash")
    assert res["success"] is True
    assert res["new_model"] == "gemini-3.8-flash"


def test_model_tools():
    rep = list_available_ai_models()
    assert "Active Primary Model" in rep

    up = check_and_upgrade_model()
    assert len(up) > 5
