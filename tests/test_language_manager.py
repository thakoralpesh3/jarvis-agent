"""
Unit Tests for Multilingual & Default Gujarati Language Subsystem.
"""

import pytest
from config.settings import JarvisConfig, load_config
from core.language_manager import LanguageManager, get_language_manager
from tools.language_tools import get_agent_language, list_supported_languages, set_agent_language


def test_default_language_is_gujarati():
    mgr = LanguageManager()
    curr = mgr.get_current_language()
    assert curr["key"] == "gujarati"
    assert curr["code"] == "gu"
    assert "ગુજરાતી" in curr["native_name"]


def test_language_system_prompt_instruction():
    mgr = LanguageManager()
    prompt = mgr.get_system_language_instruction()
    assert "ગુજરાતી" in prompt
    assert "Gujlish" in prompt or "GUJARATI" in prompt


def test_switch_to_english_and_back():
    mgr = LanguageManager()
    
    # Switch to English
    res_en = mgr.set_language("english")
    assert res_en["success"] is True
    assert mgr.get_current_language()["key"] == "english"
    prompt_en = mgr.get_system_language_instruction()
    assert "English" in prompt_en

    # Switch back to Gujarati
    res_gu = mgr.set_language("gujarati")
    assert res_gu["success"] is True
    assert mgr.get_current_language()["key"] == "gujarati"


def test_switch_by_short_code():
    mgr = LanguageManager()
    res = mgr.set_language("hi")
    assert res["success"] is True
    assert mgr.get_current_language()["key"] == "hindi"

    # Reset to gujarati
    mgr.set_language("gu")
    assert mgr.get_current_language()["key"] == "gujarati"


def test_language_tools():
    rep = list_supported_languages()
    assert "ગુજરાતી" in rep
    assert "English" in rep

    active_info = get_agent_language()
    assert "ગુજરાતી" in active_info

    msg = set_agent_language("gujarati")
    assert "ગુજરાતી" in msg
