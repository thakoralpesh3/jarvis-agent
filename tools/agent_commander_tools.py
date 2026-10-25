"""
Agent Commander and Stuck Troubleshooter Tools for JARVIS.
Equips JARVIS with multi-agent orchestration, YouTube Shorts AI Agent supervision,
and active laptop problem-solving tools.
"""

from typing import Any, Dict, List, Optional
from config.settings import load_config


def _get_commander():
    from core.agent_commander import AgentCommander
    return AgentCommander(load_config())


def _get_troubleshooter():
    from core.troubleshooter import LaptopTroubleshooter
    return LaptopTroubleshooter(load_config())


def command_youtube_shorts_agent(action: str = "run_daily_pipeline", topic: str = "", niche: str = "", dry_run: bool = False) -> str:
    """
    Command and oversee the YouTube Shorts AI Agent (/home/alpesh/youtube-agent).
    Executes the automated short video generation pipeline (script, audio, visuals, video assembly, and upload)
    and actively supervises execution to ensure 100% completion.
    
    Args:
        action: Directive ('run_daily_pipeline', 'check_status', 'resume').
        topic: Specific video topic/concept (e.g. 'Mindblowing Quantum Physics Facts').
        niche: Niche category (e.g. 'Science & Technology', 'Stoicism', 'AI Tools').
        dry_run: If True, renders video locally without publishing to YouTube.
    """
    commander = _get_commander()
    
    if action == "check_status":
        status = commander.youtube_commander.get_schedule_status()
        return f"YouTube Shorts Agent Telemetry: Last Run: {status.get('last_run_date', 'Never')}, Status: {status.get('last_status', 'standby')}, Total Completed: {status.get('total_completed_shorts', 0)}, Last Video: {status.get('last_output_video', 'None')}"
    
    res = commander.command_agent("youtube_shorts_agent", task=topic, niche=niche, dry_run=dry_run)
    if res.get("success"):
        return f"YouTube Shorts Agent finished successfully, Sir. Output video: {res.get('video_path')} (Attempts: {res.get('attempts', 1)})"
    else:
        return f"YouTube Shorts Agent execution failed: {res.get('error')}"


def list_subordinate_agents() -> str:
    """
    Inspect all subordinate AI agents under JARVIS's command and their current operational status.
    """
    commander = _get_commander()
    agents = commander.list_subordinate_agents()
    
    lines = ["### 🤖 Subordinate AI Agents Under JARVIS Supreme Command:"]
    for ag in agents:
        lines.append(f"- **{ag['name']}** [{ag['status'].upper()}]")
        lines.append(f"  Role: {ag['role']}")
        lines.append(f"  Location: `{ag['path']}`")
        lines.append(f"  Last Run: {ag['last_run']} | Total Completed: {ag['total_completed']}")
    return "\n".join(lines)


def diagnose_stuck_situation(context_description: str = "") -> str:
    """
    Actively inspect the laptop environment (open windows, clipboard, terminal history, error logs)
    and provide an immediate, step-by-step solution when the user is stuck or encountering a problem.
    
    Args:
        context_description: Optional description of what you are trying to accomplish or what failed.
    """
    troubleshooter = _get_troubleshooter()
    return troubleshooter.diagnose_and_solve_stuck_point(context_description)


def diagnose_and_heal_subagent(agent_name: str, error_trace: str) -> str:
    """
    Diagnose an issue or crash in a subordinate AI agent, generate the code fix, and apply self-healing.
    
    Args:
        agent_name: Name of subordinate agent (e.g. 'youtube_shorts_agent', 'autonomous_project_creator').
        error_trace: Full error message or traceback snippet.
    """
    commander = _get_commander()
    return commander.diagnose_and_heal_subagent(agent_name, error_trace)
