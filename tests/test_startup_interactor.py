"""
Unit Tests for Startup Voice Interactor & Autonomous Self-Task Proposer.
"""

import pytest
from unittest.mock import MagicMock
from config.settings import JarvisConfig
from core.startup_interactor import StartupVoiceInteractor


class MockAgent:
    def __init__(self, language="gujarati"):
        self.config = JarvisConfig(language=language)
        self.voice = MagicMock()
        self.voice.speak = MagicMock()
        self.voice.record_microphone_audio = MagicMock(return_value=None)
        self.voice.transcribe_audio_with_gemini = MagicMock(return_value="")
        self.registry = MagicMock()
        self.registry._tools = ["run_jarvis_self_optimization", "generate_wholesale_purchase_order"]
        self.registry.execute = MagicMock(return_value="Executed")
        self.run_turn = MagicMock(return_value="Command finished successfully.")


def test_no_work_detection():
    agent = MockAgent(language="gujarati")
    interactor = StartupVoiceInteractor(agent)

    # Negative responses in Gujarati and English
    assert interactor.is_negative_or_no_work("") is True
    assert interactor.is_negative_or_no_work("no") is True
    assert interactor.is_negative_or_no_work("કંઈ નથી") is True
    assert interactor.is_negative_or_no_work("કાંઈ નથી") is True
    assert interactor.is_negative_or_no_work("kai nathi") is True
    assert interactor.is_negative_or_no_work("nothing right now") is True

    # Real work command should NOT be negative
    assert interactor.is_negative_or_no_work("check battery voltage") is False
    assert interactor.is_negative_or_no_work("classic 350 service") is False


def test_suggestion_request_detection():
    agent = MockAgent(language="gujarati")
    interactor = StartupVoiceInteractor(agent)

    assert interactor.is_asking_for_suggestions("તારી પાસે કોઈ આઇડિયા છે?") is True
    assert interactor.is_asking_for_suggestions("કંઈક સૂચન આપો") is True
    assert interactor.is_asking_for_suggestions("give me some suggestions") is True
    assert interactor.is_asking_for_suggestions("check stock") is False


def test_autonomous_work_proposals():
    agent = MockAgent(language="gujarati")
    interactor = StartupVoiceInteractor(agent)
    proposals = interactor.get_autonomous_work_proposals()
    assert "સ્વયંસંચાલિત" in proposals["report"]
    assert "ચામુંડા" not in proposals["report"]
    assert "રોયલ એનફિલ્ડ" not in proposals["report"]
    assert len(proposals["speech"]) > 10

    agent_en = MockAgent(language="english")
    interactor_en = StartupVoiceInteractor(agent_en)
    proposals_en = interactor_en.get_autonomous_work_proposals()
    assert "Autonomous" in proposals_en["report"]
    assert "Chamunda" not in proposals_en["report"]
    assert "Royal Enfield" not in proposals_en["report"]



def test_execute_autonomous_tasks():
    agent = MockAgent(language="gujarati")
    interactor = StartupVoiceInteractor(agent)
    summary = interactor.execute_autonomous_tasks()
    assert "System Optimization" in summary or "સફળતાપૂર્વક" in summary
    assert agent.voice.speak.called


def test_interactive_startup_no_work_flow():
    agent = MockAgent(language="gujarati")
    interactor = StartupVoiceInteractor(agent)
    
    # User says nothing / silence
    res = interactor.run_interactive_startup()
    assert res["action"] == "autonomous_self_work"
    assert "સફળતાપૂર્વક" in res["execution_summary"] or "System Optimization" in res["execution_summary"]
