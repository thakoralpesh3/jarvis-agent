"""
AI Model Management, Auto-Upgrade & Switching Tools for JARVIS.
Allows checking available models, switching models, and automatically upgrading to the latest Gemini release.
"""

from typing import Any, Dict, List, Optional


def check_and_upgrade_model(notify: bool = False) -> str:
    """
    Check if a newer Gemini AI model is available from Google GenAI API
    (e.g., auto-upgrading to Gemini 3.8 Flash when released) and automatically apply the upgrade.
    """
    from core.model_manager import get_model_manager
    mgr = get_model_manager()
    res = mgr.auto_upgrade_model(notify=notify)
    return res.get("message", "Model check completed.")


def list_available_ai_models() -> str:
    """
    List all accessible Gemini models, the current active model, and the newest discovered versions.
    """
    from core.model_manager import get_model_manager
    mgr = get_model_manager()
    return mgr.get_status_report()


def set_ai_model(model_name: str, notify: bool = False) -> str:
    """
    Switch the active AI model to a specific model version.
    
    Args:
        model_name: The model identifier (e.g. 'gemini-3.8-flash', 'gemini-3.7-flash', 'gemini-3.1-pro-preview', 'gemini-flash-latest').
    """
    from core.model_manager import get_model_manager
    mgr = get_model_manager()
    res = mgr.set_model(model_name=model_name, notify=notify)
    return res.get("message", f"Model set to {model_name}")
