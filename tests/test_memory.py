"""
Tests for JARVIS Memory and Continuous Learning subsystem.
"""

import tempfile
from pathlib import Path
import pytest

from memory.database import DatabaseManager
from memory.semantic_memory import SemanticMemory
from memory.episodic_memory import EpisodicMemory
from memory.skill_store import SkillStore
from memory.memory_manager import MemoryManager
from config.settings import JarvisConfig


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_semantic_facts_crud(temp_dir):
    db_path = temp_dir / "test_memory.db"
    db = DatabaseManager(db_path)
    semantic = SemanticMemory(db)

    # 1. Insert facts
    semantic.add_or_update_fact("preference", "code_style", "Python 3.12 with type hints", 0.95)
    semantic.add_or_update_fact("user_fact", "user_name", "Tony Stark", 1.0)
    semantic.add_or_update_fact("system", "os", "Linux Mint", 1.0)

    # 2. Retrieve fact
    fact = semantic.get_fact("preference", "code_style")
    assert fact is not None
    assert fact["value"] == "Python 3.12 with type hints"

    # 3. Search facts
    results = semantic.search_relevant_facts("Python hints")
    assert len(results) >= 1
    assert results[0]["key"] == "code_style"

    # 4. Prompt context formatting
    context = semantic.format_context_for_prompt("Python")
    assert "code_style" in context
    assert "Python 3.12" in context


def test_lessons_learned_self_correction(temp_dir):
    db_path = temp_dir / "test_memory.db"
    db = DatabaseManager(db_path)
    episodic = EpisodicMemory(db)

    # 1. Add learned error avoidance rule
    lesson_id = episodic.add_lesson(
        trigger_pattern="running apt install",
        mistake="running apt install without sudo",
        lesson="Always use sudo when installing system debian packages",
        solution="sudo apt update && sudo apt install -y <package>",
        tags="bash,linux,apt"
    )
    assert lesson_id > 0

    # 2. Search relevant lesson
    matches = episodic.find_relevant_lessons("apt install ffmpeg")
    assert len(matches) >= 1
    assert "Always use sudo" in matches[0]["lesson"]

    # 3. Prompt context formatting
    formatted = episodic.format_lessons_for_prompt("apt install")
    assert "Mistake to avoid" in formatted
    assert "running apt install without sudo" in formatted


def test_episodic_logging(temp_dir):
    db_path = temp_dir / "test_memory.db"
    db = DatabaseManager(db_path)
    episodic = EpisodicMemory(db)

    ep_id = episodic.record_episode(
        session_id="session-123",
        user_prompt="Check disk usage",
        plan="Run df -h",
        steps=[{"tool": "execute_shell_command", "args": {"command": "df -h"}, "result": "100GB free"}],
        result="You have 100GB free on root.",
        success=True
    )
    assert ep_id > 0

    recent = episodic.get_recent_episodes(5)
    assert len(recent) == 1
    assert recent[0]["user_prompt"] == "Check disk usage"
    assert recent[0]["steps"][0]["tool"] == "execute_shell_command"


def test_memory_manager_assembly(temp_dir):
    config = JarvisConfig(
        base_dir=temp_dir,
        db_path=temp_dir / "jarvis.db",
        dynamic_tools_dir=temp_dir / "skills"
    )
    mgr = MemoryManager(config)
    mgr.semantic.add_or_update_fact("preference", "theme", "Dark Mode")
    mgr.learn_lesson("pip install", "forgot --break-system-packages", "Use virtualenv or break system packages flag")

    full_context = mgr.assemble_system_learning_context("pip install numpy")
    assert "Dark Mode" in full_context
    assert "Continuous Learning" in full_context
    assert "break system packages" in full_context
