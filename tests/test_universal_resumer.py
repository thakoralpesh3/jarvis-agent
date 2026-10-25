"""
Tests for Universal Application Stoppage & Auto-Resumption Subsystem.
"""

import json
import tempfile
from pathlib import Path
import pytest
from core.universal_resumer import UniversalApplicationResumer


@pytest.fixture
def tmp_resumer_env():
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_brain = Path(tmpdir) / "brain"
        fake_brain.mkdir(parents=True, exist_ok=True)
        
        # Create a mock interrupted conversation
        conv_dir = fake_brain / "mock-conv-123"
        logs_dir = conv_dir / ".system_generated" / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        transcript_file = logs_dir / "transcript.jsonl"
        lines = [
            json.dumps({"type": "USER_INPUT", "status": "DONE", "content": "<USER_REQUEST>Build a web scraper and export to CSV</USER_REQUEST>"}),
            json.dumps({"type": "PLANNER_RESPONSE", "status": "ERROR", "content": "Error: The stream was interrupted."})
        ]
        transcript_file.write_text("\n".join(lines), encoding="utf-8")

        resumer = UniversalApplicationResumer(brain_dir=fake_brain)
        resumer.registry_file = Path(tmpdir) / "registry.json"
        resumer._ensure_registry()
        yield resumer, conv_dir


def test_inspect_antigravity_interrupted_tasks(tmp_resumer_env):
    resumer, conv_dir = tmp_resumer_env
    interrupted = resumer.inspect_antigravity_interrupted_tasks()
    assert len(interrupted) == 1
    task = interrupted[0]
    assert task["app"] == "antigravity"
    assert task["conversation_id"] == "mock-conv-123"
    assert "Build a web scraper" in task["prompt"]
    assert "Stream or server interruption" in task["reason"]


def test_auto_resume_antigravity_task_mocked(tmp_resumer_env):
    resumer, conv_dir = tmp_resumer_env
    interrupted = resumer.inspect_antigravity_interrupted_tasks()
    assert len(interrupted) == 1

    class MockAgent:
        def __init__(self):
            self.resumed_directives = []
        def run_turn(self, directive: str):
            self.resumed_directives.append(directive)
            return "Task completed successfully"

    agent = MockAgent()
    msg = resumer.auto_resume_antigravity_task(interrupted[0], agent_instance=agent)
    assert "Successfully resumed" in msg
    assert len(agent.resumed_directives) == 1
    assert "Build a web scraper" in agent.resumed_directives[0]


def test_inspect_and_auto_resume_all_clean(tmp_resumer_env):
    resumer, conv_dir = tmp_resumer_env
    # Clear the transcript so it's clean
    (conv_dir / ".system_generated" / "logs" / "transcript.jsonl").unlink()
    
    results = resumer.inspect_and_auto_resume_all()
    assert isinstance(results, list)
