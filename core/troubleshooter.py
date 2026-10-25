"""
Stuck Point Troubleshooter & Laptop Problem Solver for JARVIS.
Inspects active desktop context, open windows, terminal history, clipboard contents,
and system error logs to diagnose what the user is stuck on and deliver immediate solutions.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional
from google import genai
from google.genai import types

from config.settings import JarvisConfig, load_config
from tools.laptop_tools import list_active_windows, get_clipboard_content
from tools.vision_tools import capture_screen
from tools.laptop_work_tools import send_desktop_notification
from tools.ironman_protocols import play_stark_sound
from core.network_resilience import execute_with_network_resume, is_network_error


class LaptopTroubleshooter:
    """Diagnoses laptop errors, compile issues, stuck processes, and delivers direct solutions."""

    def __init__(self, config: Optional[JarvisConfig] = None):
        self.config = config or load_config()
        self.client = genai.Client(api_key=self.config.api_key) if self.config.api_key else None

    def capture_environment_context(self) -> Dict[str, Any]:
        """Collect active window, clipboard, bash history snippet, and screen capture context."""
        context = {}
        
        # 1. Active Windows
        try:
            context["active_windows"] = list_active_windows()
        except Exception:
            context["active_windows"] = []

        # 2. Clipboard Contents
        try:
            context["clipboard"] = get_clipboard_content()[:2000]
        except Exception:
            context["clipboard"] = ""

        # 3. Recent Bash History (last 15 commands)
        try:
            hist_file = Path.home() / ".bash_history"
            if hist_file.exists():
                lines = hist_file.read_text(encoding="utf-8", errors="ignore").strip().splitlines()
                context["recent_commands"] = lines[-15:]
            else:
                context["recent_commands"] = []
        except Exception:
            context["recent_commands"] = []

        # 4. Recent System / X11 Errors (dmesg / journalctl snippet)
        try:
            res = subprocess.run(
                "journalctl --user -n 20 --no-pager -p 3 2>/dev/null || true",
                shell=True,
                capture_output=True,
                text=True,
                timeout=2
            )
            context["recent_errors"] = res.stdout.strip()[:1000]
        except Exception:
            context["recent_errors"] = ""

        return context

    def _call_gemini(self, models_to_try: List[str], prompt: str) -> Any:
        """Call Gemini API with model fallback list."""
        last_err = None
        for model_id in models_to_try:
            try:
                return self.client.models.generate_content(
                    model=model_id,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                    )
                )
            except Exception as e:
                last_err = e
                if is_network_error(e) and model_id == models_to_try[-1]:
                    raise e
                continue
        if last_err:
            raise last_err
        return None

    def diagnose_and_solve_stuck_point(self, user_description: str = "") -> str:
        """
        Analyze the user's current predicament and synthesize an exact, actionable solution.
        """
        if not self.client:
            return "Aradhya Error: Gemini API key not configured."

        play_stark_sound("protocol")
        env_ctx = self.capture_environment_context()

        prompt = f"""You are Aradhya, an autonomous tactical AI assistant and master troubleshooter with full control over this system.
The user is working on their laptop and is currently stuck or encountering an error.
Your task is to analyze their environment, identify the exact issue, and provide an immediate, foolproof solution.

User Problem Description: {user_description or 'User is stuck on their current screen/task and needs immediate resolution.'}

Environment Telemetry:
- Active Windows: {env_ctx.get('active_windows', [])}
- Current Clipboard Content: {env_ctx.get('clipboard', '')}
- Recent Terminal Commands: {env_ctx.get('recent_commands', [])}
- Recent System Logs: {env_ctx.get('recent_errors', '')}

Provide a concise, direct tactical response:
1. **Diagnosis**: Exactly what went wrong or why the task is blocked.
2. **Immediate Solution / Fix**: Exact commands to run, code modifications, or steps to take.
3. **Prevention Advice**: How to ensure it doesn't happen again.

Keep it actionable, precise, and crisp."""

        candidate_models = [self.config.model_name, "gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.1-pro-preview"]
        seen = set()
        models_to_try = [m for m in candidate_models if not (m in seen or seen.add(m))]

        try:
            response = execute_with_network_resume(lambda: self._call_gemini(models_to_try, prompt))
            if response and response.text:
                play_stark_sound("ack")
                send_desktop_notification("Aradhya Solution Ready", "Sir, I have analyzed the issue and prepared your solution.")
                return response.text.strip()
            return "Sir, I analyzed the system context but was unable to isolate an error signature. Please provide a brief note on what you are trying to achieve."
        except Exception as e:
            return f"Troubleshooting analysis error: {str(e)}"
