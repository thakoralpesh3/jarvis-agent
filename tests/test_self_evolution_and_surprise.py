"""
Tests for Aradhya Autonomous Self-Evolution Engine & Proactive Surprise/Innovation Muse.
"""

import os
import pytest
from unittest.mock import MagicMock, patch

from core.self_evolution import SelfEvolutionEngine
from core.innovation_surprise import InnovationSurpriseEngine, SURPRISE_IDEAS_CATALOGUE
from tools.evolution_tools import (
    surprise_me_with_idea,
    trigger_self_evolution_cycle,
    get_agent_evolution_status,
)
from core.offline_commander import OfflineCommander
from config.settings import JarvisConfig


def test_surprise_ideas_catalogue():
    assert len(SURPRISE_IDEAS_CATALOGUE) >= 5
    for idea in SURPRISE_IDEAS_CATALOGUE:
        assert "title" in idea
        assert "category" in idea
        assert "gujarati_pitch" in idea
        assert "autonomous_steps" in idea


def test_self_evolution_cycle():
    engine = SelfEvolutionEngine()
    res = engine.run_evolution_cycle(auto_synthesize=False)
    assert isinstance(res, dict)
    assert res["success"] is True
    assert "current_generation" in res
    assert "dispatch_latency_ms" in res
    assert "gujarati_summary" in res
    assert "english_summary" in res
    assert "ઇવોલ્યુશન" in res["gujarati_summary"] or "Evolution" in res["english_summary"]


def test_self_evolution_ledger():
    engine = SelfEvolutionEngine()
    ledger = engine.get_evolution_ledger()
    assert isinstance(ledger, dict)
    assert "current_generation" in ledger
    assert "total_evolution_cycles" in ledger
    assert "history" in ledger


def test_innovation_surprise_engine_generation():
    engine = InnovationSurpriseEngine()
    # Force curated catalogue to avoid network latency during unit testing
    with patch("core.innovation_surprise.check_internet_connection", return_value=False):
        idea = engine.generate_surprise_idea()
        assert isinstance(idea, dict)
        assert idea["success"] is True
        assert "title" in idea
        assert "category" in idea
        assert "gujarati_pitch" in idea

        report = engine.format_surprise_report(idea)
        assert isinstance(report, str)
        assert "ARADHYA PROACTIVE INNOVATION & SURPRISE" in report or "AROHI PROACTIVE INNOVATION & SURPRISE" in report
        assert "💡" in report


def test_evolution_tools():
    # 1. Surprise me tool
    with patch("core.innovation_surprise.check_internet_connection", return_value=False):
        res_surprise = surprise_me_with_idea()
        assert "PROACTIVE INNOVATION & SURPRISE" in res_surprise

    # 2. Trigger evolution tool
    res_evo = trigger_self_evolution_cycle()
    assert "AUTONOMOUS SELF-EVOLUTION REPORT" in res_evo
    assert "Generation" in res_evo

    # 3. Evolution status tool
    res_stat = get_agent_evolution_status()
    assert "Aradhya Evolution & Adaptation Ledger" in res_stat


def test_offline_commander_surprise_and_evolution_gujarati():
    commander = OfflineCommander(JarvisConfig())

    with patch("core.innovation_surprise.check_internet_connection", return_value=False):
        # Gujarati surprise request
        res_gu = commander.execute_offline_turn("આરાધ્યા, મને કોઈ નવો સરપ્રાઈઝ આઈડિયા આપો")
        assert "આઈડિયા" in res_gu or "SURPRISE" in res_gu or "સરપ્રાઈઝ" in res_gu

    # Gujarati evolution request
    res_evo = commander.execute_offline_turn("પોતાને ઇવોલ્વ કરો અને સેલ્ફ ટ્યુનિંગ ચલાવો")
    assert "ઇવોલ્યુશન" in res_evo or "EVOLUTION" in res_evo or "Generation" in res_evo

    # Gujarati total laptop control
    res_ctrl = commander.execute_offline_turn("લેપટોપ સંપૂર્ણ કંટ્રોલ કરો")
    assert "સંપૂર્ણ નિયંત્રણ" in res_ctrl or "control" in res_ctrl.lower()


def test_offline_commander_surprise_and_evolution_english():
    cfg_en = JarvisConfig(language="english")
    cmd_en = OfflineCommander(cfg_en)

    with patch("core.innovation_surprise.check_internet_connection", return_value=False):
        # English surprise
        res_en = cmd_en.execute_offline_turn("surprise me with an innovative idea")
        assert "surprise" in res_en.lower() or "idea" in res_en.lower() or "innovation" in res_en.lower()

    # English total laptop control
    res_ctrl = cmd_en.execute_offline_turn("control whole laptop")
    assert "control" in res_ctrl.lower() or "authority" in res_ctrl.lower()
