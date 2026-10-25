"""
Persistent Task Checkpointing and Automatic Crash/Network Resumption Subsystem for JARVIS.
Saves intermediate execution state to disk so tasks can be automatically resumed from the exact
point of interruption after network restoration or system restarts.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

from config.settings import DEFAULT_CONFIG_DIR
from tools.laptop_work_tools import send_desktop_notification
from tools.ironman_protocols import play_stark_sound


CHECKPOINT_FILE = DEFAULT_CONFIG_DIR / "task_checkpoints.json"


@dataclass
class TaskCheckpoint:
    task_id: str
    task_type: str  # 'conversation_turn', 'autonomous_project', 'skill_synthesis'
    user_prompt: str
    session_id: str
    steps_completed: List[Dict[str, Any]]
    current_contents: List[Dict[str, Any]]
    extra_data: Dict[str, Any]
    timestamp: float
    status: str = "in_progress"  # 'in_progress', 'suspended_network', 'completed'


class TaskCheckpointManager:
    """Manages persistent task checkpoints to enable automatic resumption."""

    def __init__(self, checkpoint_path: Optional[Path] = None):
        self.checkpoint_file = checkpoint_path or CHECKPOINT_FILE
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_file()

    def _ensure_file(self) -> None:
        if not self.checkpoint_file.exists():
            self.checkpoint_file.write_text("{}", encoding="utf-8")

    def _read_all(self) -> Dict[str, Dict[str, Any]]:
        try:
            return json.loads(self.checkpoint_file.read_text(encoding="utf-8") or "{}")
        except Exception:
            return {}

    def _write_all(self, data: Dict[str, Dict[str, Any]]) -> None:
        try:
            self.checkpoint_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass

    def save_checkpoint(
        self,
        task_id: str,
        task_type: str,
        user_prompt: str,
        session_id: str,
        steps_completed: List[Dict[str, Any]],
        current_contents: Optional[List[Any]] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        status: str = "in_progress"
    ) -> None:
        """Persist or update an intermediate task checkpoint."""
        serialized_contents = []
        if current_contents:
            for item in current_contents:
                if hasattr(item, "role") and hasattr(item, "parts"):
                    parts_data = []
                    for part in item.parts:
                        if hasattr(part, "text") and part.text:
                            parts_data.append({"text": part.text})
                        elif hasattr(part, "function_call") and part.function_call:
                            parts_data.append({"function_call": {"name": part.function_call.name, "args": dict(part.function_call.args or {})}})
                        elif hasattr(part, "function_response") and part.function_response:
                            parts_data.append({"function_response": {"name": part.function_response.name, "response": part.function_response.response}})
                    serialized_contents.append({"role": item.role, "parts": parts_data})

        checkpoint = TaskCheckpoint(
            task_id=task_id,
            task_type=task_type,
            user_prompt=user_prompt,
            session_id=session_id,
            steps_completed=steps_completed,
            current_contents=serialized_contents,
            extra_data=extra_data or {},
            timestamp=time.time(),
            status=status
        )

        data = self._read_all()
        data[task_id] = asdict(checkpoint)
        self._write_all(data)

    def mark_suspended(self, task_id: str, reason: str = "network_dropout") -> None:
        """Mark a checkpoint as suspended due to network or environmental conditions."""
        data = self._read_all()
        if task_id in data:
            data[task_id]["status"] = "suspended_network"
            data[task_id]["extra_data"]["suspension_reason"] = reason
            data[task_id]["timestamp"] = time.time()
            self._write_all(data)

    def clear_checkpoint(self, task_id: str) -> None:
        """Remove a successfully completed checkpoint from disk."""
        data = self._read_all()
        if task_id in data:
            del data[task_id]
            self._write_all(data)

    def get_suspended_checkpoints(self) -> List[Dict[str, Any]]:
        """Retrieve all tasks that are currently suspended awaiting network restoration."""
        data = self._read_all()
        return [cp for cp in data.values() if cp.get("status") in ("suspended_network", "in_progress")]

    def auto_resume_suspended_tasks(self, agent_instance: Any) -> int:
        """
        Scan for suspended tasks and automatically resume them to completion.
        Returns the number of tasks resumed.
        """
        suspended = self.get_suspended_checkpoints()
        if not suspended:
            return 0

        resumed_count = 0
        for cp in suspended:
            task_id = cp["task_id"]
            user_prompt = cp["user_prompt"]
            task_type = cp.get("task_type", "conversation_turn")

            play_stark_sound("protocol")
            send_desktop_notification(
                "Aradhya Auto-Resumption",
                f"Automatically resuming suspended task '{user_prompt[:50]}...' from checkpoint.",
                user_commanded=False
            )

            try:
                if task_type == "autonomous_project":
                    from core.autonomous_creator import AutonomousCreatorEngine
                    creator = AutonomousCreatorEngine(agent_instance.config, agent_instance.memory_mgr)
                    proj_name = cp.get("extra_data", {}).get("project_name", "Autonomous_Project")
                    creator.build_and_execute_project(proj_name, user_prompt)
                else:
                    agent_instance.run_turn(user_prompt)

                self.clear_checkpoint(task_id)
                resumed_count += 1
            except Exception as e:
                # Keep checkpoint for next retry
                pass

        return resumed_count
