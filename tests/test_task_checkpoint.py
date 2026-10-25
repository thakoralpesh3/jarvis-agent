"""
Tests for Persistent Task Checkpointing and Auto-Resumption Subsystem.
"""

import tempfile
from pathlib import Path
import pytest
from core.task_checkpoint import TaskCheckpointManager


@pytest.fixture
def tmp_checkpoint_mgr():
    with tempfile.TemporaryDirectory() as tmpdir:
        chk_file = Path(tmpdir) / "test_checkpoints.json"
        mgr = TaskCheckpointManager(chk_file)
        yield mgr


def test_save_and_get_checkpoints(tmp_checkpoint_mgr):
    mgr = tmp_checkpoint_mgr
    mgr.save_checkpoint(
        task_id="task-001",
        task_type="conversation_turn",
        user_prompt="Run diagnostic sweep",
        session_id="session-xyz",
        steps_completed=[{"tool": "get_system_metrics", "result": "cpu: 10%"}],
        status="in_progress"
    )

    suspended = mgr.get_suspended_checkpoints()
    assert len(suspended) == 1
    assert suspended[0]["task_id"] == "task-001"
    assert suspended[0]["user_prompt"] == "Run diagnostic sweep"


def test_mark_suspended_and_clear(tmp_checkpoint_mgr):
    mgr = tmp_checkpoint_mgr
    mgr.save_checkpoint(
        task_id="task-002",
        task_type="conversation_turn",
        user_prompt="Summarize documents",
        session_id="session-xyz",
        steps_completed=[],
        status="in_progress"
    )

    mgr.mark_suspended("task-002", reason="WiFi disconnection")
    suspended = mgr.get_suspended_checkpoints()
    assert len(suspended) == 1
    assert suspended[0]["status"] == "suspended_network"
    assert suspended[0]["extra_data"]["suspension_reason"] == "WiFi disconnection"

    # Clear checkpoint
    mgr.clear_checkpoint("task-002")
    assert len(mgr.get_suspended_checkpoints()) == 0


def test_auto_resume_suspended_tasks(tmp_checkpoint_mgr):
    mgr = tmp_checkpoint_mgr
    mgr.save_checkpoint(
        task_id="task-003",
        task_type="conversation_turn",
        user_prompt="Check battery and thermals",
        session_id="session-xyz",
        steps_completed=[],
        status="suspended_network"
    )

    resumed_prompts = []

    class MockAgent:
        def run_turn(self, prompt: str):
            resumed_prompts.append(prompt)
            return "Resumed output"

    agent = MockAgent()
    count = mgr.auto_resume_suspended_tasks(agent)
    assert count == 1
    assert resumed_prompts == ["Check battery and thermals"]
    assert len(mgr.get_suspended_checkpoints()) == 0
