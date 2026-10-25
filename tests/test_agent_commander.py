"""
Tests for Supreme Multi-Agent Commander.
"""

import pytest
from core.agent_commander import AgentCommander


def test_list_subordinate_agents():
    commander = AgentCommander()
    agents = commander.list_subordinate_agents()
    assert isinstance(agents, list)
    assert len(agents) >= 2
    names = [a["name"] for a in agents]
    assert "youtube_shorts_agent" in names
    assert "autonomous_project_creator" in names


def test_command_unknown_agent():
    commander = AgentCommander()
    res = commander.command_agent("non_existent_agent", "do something")
    assert res.get("success") is False
