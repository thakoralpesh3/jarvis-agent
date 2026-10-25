"""
Language switching and multilingual management tools for JARVIS.
Allows getting active language, listing supported languages, and switching languages dynamically.
"""

from typing import Any, Dict


def set_agent_language(language: str) -> str:
    """
    Switch the primary conversation language of JARVIS (e.g., 'gujarati', 'english', 'hindi', 'marathi').
    Default is Gujarati.
    
    Args:
        language: Language name or code (e.g. 'gujarati', 'gu', 'english', 'en', 'hindi', 'hi').
    """
    from core.language_manager import get_language_manager
    mgr = get_language_manager()
    res = mgr.set_language(language, notify=False)
    return res.get("message", f"Language set to {language}.")


def get_agent_language() -> str:
    """
    Get the currently active language of JARVIS.
    """
    from core.language_manager import get_language_manager
    mgr = get_language_manager()
    info = mgr.get_current_language()
    return f"હાલની સક્રિય ભાષા (Active Language): {info['native_name']} ({info['name']}, Code: `{info['code']}`)"


def list_supported_languages() -> str:
    """
    List all supported languages for JARVIS and instructions on how to switch.
    """
    from core.language_manager import get_language_manager
    mgr = get_language_manager()
    return mgr.list_supported_languages()
