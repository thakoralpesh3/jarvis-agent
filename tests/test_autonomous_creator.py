"""
Tests for Autonomous Idea Suggestion and Project Creator.
"""

from pathlib import Path
import pytest
from tools.autonomous_creator_tools import (
    suggest_innovative_ideas,
    build_and_execute_project_autonomously,
)
from config.settings import load_config
from core.autonomous_creator import AutonomousCreatorEngine, PROJECTS_BASE_DIR


def test_autonomous_creator_engine_init():
    cfg = load_config()
    engine = AutonomousCreatorEngine(cfg)
    assert engine.client is not None
    assert PROJECTS_BASE_DIR.exists()


def test_suggest_innovative_ideas():
    ideas = suggest_innovative_ideas("system automation")
    assert isinstance(ideas, str)
    assert len(ideas) > 20
    assert "Project" in ideas or "Idea" in ideas or "Stark" in ideas
