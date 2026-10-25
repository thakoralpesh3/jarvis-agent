"""
Universal Application Stoppage & Interrupted Task Resumption Tools for JARVIS.
Allows JARVIS to scan for any applications (like Antigravity or YouTube Agent) that stopped
working mid-prompt or mid-task, and automatically commands resumption from that exact point.
"""

from typing import Any, Dict, List, Optional


def _get_resumer():
    from core.universal_resumer import UniversalApplicationResumer
    return UniversalApplicationResumer()


def scan_and_resume_interrupted_apps() -> str:
    """
    Scan all monitored applications (including Antigravity IDE/CLI, YouTube Agent pipelines,
    and background jobs) to detect any tasks that stopped working unexpectedly, and automatically
    command them to resume execution from the exact point of stoppage.
    """
    resumer = _get_resumer()
    results = resumer.inspect_and_auto_resume_all()
    if not results:
        return "Universal Scan Complete: All monitored applications (Antigravity, YouTube Agent, background processes) are running nominally with no interrupted tasks detected, Sir."
    
    return "Universal Application Resumption Report:\n" + "\n".join(f"- {r}" for r in results)


def resume_antigravity_interrupted_work(conversation_id: str = "") -> str:
    """
    Inspect Antigravity conversation transcripts, identify any prompt or task that stopped working
    (e.g. stream interruption, server restart, or process killed), and automatically complete the work.
    
    Args:
        conversation_id: Optional specific conversation ID to target. If empty, scans all recent conversations.
    """
    resumer = _get_resumer()
    tasks = resumer.inspect_antigravity_interrupted_tasks()
    if not tasks:
        return "No interrupted Antigravity prompts found. All recent tasks completed successfully, Sir."

    resumed_msgs = []
    for t in tasks:
        if not conversation_id or t.get("conversation_id") == conversation_id:
            msg = resumer.auto_resume_antigravity_task(t)
            resumed_msgs.append(msg)

    return "\n".join(resumed_msgs) if resumed_msgs else "No matching interrupted Antigravity tasks found."
