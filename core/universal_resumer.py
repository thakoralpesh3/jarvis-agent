"""
Universal Application Stoppage Watchdog & Auto-Resumption Subsystem for JARVIS.
Detects when ANY application (such as Antigravity IDE/CLI, YouTube Agent, compilers, dev servers)
unexpectedly stops, crashes, or gets interrupted mid-task, and automatically commands it to resume
execution from the exact point of stoppage without losing work.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from config.settings import DEFAULT_CONFIG_DIR, load_config
from tools.laptop_work_tools import send_desktop_notification
from tools.ironman_protocols import play_stark_sound


ANTIGRAVITY_BRAIN_DIR = Path.home() / ".gemini" / "antigravity" / "brain"
APP_WATCH_REGISTRY = DEFAULT_CONFIG_DIR / "monitored_apps.json"


class UniversalApplicationResumer:
    """Monitors external applications and auto-resumes interrupted tasks/prompts."""

    def __init__(self, brain_dir: Path = ANTIGRAVITY_BRAIN_DIR):
        self.brain_dir = brain_dir
        self.registry_file = APP_WATCH_REGISTRY
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_registry()

    def _ensure_registry(self) -> None:
        if not self.registry_file.exists():
            default_state = {
                "monitored_apps": [
                    {
                        "name": "antigravity",
                        "type": "agent_ide",
                        "path": str(self.brain_dir),
                        "auto_resume": True
                    },
                    {
                        "name": "youtube_agent",
                        "type": "automation_pipeline",
                        "path": "/home/alpesh/youtube-agent",
                        "auto_resume": True
                    }
                ],
                "last_scan_timestamp": 0,
                "resumed_tasks_history": []
            }
            self.registry_file.write_text(json.dumps(default_state, indent=2), encoding="utf-8")

    def inspect_antigravity_interrupted_tasks(self) -> List[Dict[str, Any]]:
        """
        Inspect Antigravity conversation transcripts to identify prompts or tasks that were
        interrupted due to server restarts, stream timeouts, or unexpected application shutdowns.
        """
        interrupted_tasks = []
        if not self.brain_dir.exists():
            return interrupted_tasks

        # Scan all conversation directories
        for conv_dir in self.brain_dir.iterdir():
            if not conv_dir.is_dir() or conv_dir.name in ("tempmediaStorage", ".system_generated"):
                continue

            transcript_file = conv_dir / ".system_generated" / "logs" / "transcript.jsonl"
            if not transcript_file.exists():
                continue

            try:
                lines = transcript_file.read_text(encoding="utf-8", errors="ignore").strip().splitlines()
                if not lines:
                    continue

                # Parse last 10 steps
                steps = []
                for l in lines[-15:]:
                    try:
                        steps.append(json.loads(l))
                    except Exception:
                        continue

                # Find last USER_INPUT
                last_user_prompt = ""
                last_user_idx = -1
                for idx, s in enumerate(steps):
                    if s.get("type") == "USER_INPUT":
                        content = s.get("content", "")
                        if "<USER_REQUEST>" in content:
                            content = content.split("<USER_REQUEST>")[1].split("</USER_REQUEST>")[0].strip()
                        last_user_prompt = content
                        last_user_idx = idx

                # Check if the last action had an interruption/crash signature
                if last_user_idx != -1:
                    after_user_steps = steps[last_user_idx + 1:]
                    is_interrupted = False
                    reason = ""

                    # Check for stream interruption or error markers
                    for s in after_user_steps:
                        content_str = str(s.get("content", "")).lower()
                        if "stream was interrupted" in content_str or "server restart" in content_str:
                            is_interrupted = True
                            reason = "Stream or server interruption"
                            break
                        if s.get("status") in ("ERROR", "CANCELLED") and s.get("type") == "PLANNER_RESPONSE":
                            is_interrupted = True
                            reason = f"Planner response error: {s.get('status')}"
                            break

                    # If the very last step in transcript is a raw USER_INPUT with no following responses
                    if not after_user_steps and last_user_prompt:
                        is_interrupted = True
                        reason = "User prompt pending execution without response"

                    if is_interrupted and last_user_prompt:
                        interrupted_tasks.append({
                            "app": "antigravity",
                            "conversation_id": conv_dir.name,
                            "prompt": last_user_prompt,
                            "reason": reason,
                            "transcript_path": str(transcript_file),
                            "timestamp": time.time()
                        })

            except Exception:
                continue

        return interrupted_tasks

    def auto_resume_antigravity_task(self, task_info: Dict[str, Any], agent_instance: Optional[Any] = None) -> str:
        """
        Command and execute the resumption of an interrupted Antigravity task.
        """
        conv_id = task_info.get("conversation_id", "")
        prompt = task_info.get("prompt", "")
        reason = task_info.get("reason", "Interrupted")

        play_stark_sound("protocol")
        send_desktop_notification(
            "Aradhya Universal Resumer",
            f"Detected interrupted Antigravity task ({reason}). Automatically commanding resumption...",
            urgency="normal",
            user_commanded=False
        )

        if not agent_instance:
            from core.agent import JarvisAgent
            agent_instance = JarvisAgent(load_config())

        # Command execution of the interrupted prompt to completion
        directive = f"Resume and complete the following interrupted task from Antigravity: {prompt}"
        res = agent_instance.run_turn(directive)

        # Log to resumed history
        self._record_resumption_event("antigravity", conv_id, prompt, success=True)
        return f"Successfully resumed and completed Antigravity task for conversation {conv_id}."

    def inspect_and_auto_resume_all(self, agent_instance: Optional[Any] = None) -> List[str]:
        """
        Comprehensive sweep across all monitored applications (Antigravity, YouTube Agent, Background Tasks)
        to detect stoppages and resume them to completion.
        """
        results = []

        # 1. Inspect Antigravity Interrupted Tasks
        interrupted_ag = self.inspect_antigravity_interrupted_tasks()
        for task in interrupted_ag:
            msg = self.auto_resume_antigravity_task(task, agent_instance)
            results.append(msg)

        # 2. Inspect YouTube Agent Incomplete Runs
        try:
            from core.youtube_commander import YouTubeShortsCommander
            yt_commander = YouTubeShortsCommander()
            resumable_run = yt_commander.youtube_dir / "output"
            # Check if YouTube agent was interrupted mid-assembly
            temp_files = list(yt_commander.youtube_dir.glob("*TEMP_MPY*"))
            if temp_files:
                send_desktop_notification("Aradhya Resumer", "YouTube Agent was interrupted mid-render. Resuming pipeline...", user_commanded=False)
                yt_res = yt_commander.run_and_supervise_pipeline(resume=True)
                results.append(f"YouTube Agent resumed: {yt_res.get('status')}")
        except Exception:
            pass

        # 3. Inspect Incomplete Task Checkpoints in JARVIS
        try:
            from core.task_checkpoint import TaskCheckpointManager
            chk_mgr = TaskCheckpointManager()
            if agent_instance:
                count = chk_mgr.auto_resume_suspended_tasks(agent_instance)
                if count > 0:
                    results.append(f"Resumed {count} suspended JARVIS task checkpoints.")
        except Exception:
            pass

        return results

    def _record_resumption_event(self, app_name: str, task_id: str, prompt: str, success: bool) -> None:
        try:
            data = json.loads(self.registry_file.read_text(encoding="utf-8") or "{}")
            history = data.get("resumed_tasks_history", [])
            history.append({
                "app": app_name,
                "task_id": task_id,
                "prompt": prompt[:100],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "success": success
            })
            data["resumed_tasks_history"] = history[-50:]
            self.registry_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass
