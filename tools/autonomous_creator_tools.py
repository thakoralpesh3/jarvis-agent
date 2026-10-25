"""
Autonomous Project Creator and Idea Suggestion Tools for JARVIS.
Equips JARVIS with the ability to propose novel ideas and autonomously execute entire projects end-to-end.
"""

from typing import Any, Optional
from config.settings import load_config


_creator_engine: Optional[Any] = None


def _get_creator_engine():
    global _creator_engine
    if _creator_engine is None:
        from core.autonomous_creator import AutonomousCreatorEngine
        cfg = load_config()
        _creator_engine = AutonomousCreatorEngine(cfg)
    return _creator_engine


def suggest_innovative_ideas(domain_or_context: str = "") -> str:
    """
    Brainstorm and propose 3 highly innovative, practical project ideas that JARVIS can build, test,
    and run autonomously from start to finish.
    
    Args:
        domain_or_context: Optional area of interest (e.g. 'system automation', 'developer productivity', 'AI tools', 'crypto tracker', 'file organizer').
    """
    engine = _get_creator_engine()
    return engine.suggest_innovative_ideas(domain_or_context)


def build_and_execute_project_autonomously(project_name: str, project_description: str) -> str:
    """
    Autonomously create, code, test, debug, and run a complete project from scratch to 100% full completion.
    Writes all required files into ~/jarvis_projects/<project_name>, verifies syntax, and runs tests.
    
    Args:
        project_name: Clean name of the project to build (e.g. 'Daily_News_Summarizer', 'Local_Port_Scanner', 'Markdown_Note_Searcher').
        project_description: Comprehensive specifications of features, logic, and goals to build.
    """
    engine = _get_creator_engine()
    return engine.build_and_execute_project(project_name, project_description)
