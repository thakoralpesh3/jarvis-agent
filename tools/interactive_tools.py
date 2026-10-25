"""
Interactive User Communication and Dialog Tools for JARVIS.
Enables JARVIS to directly interact with the user via native GUI dialogs, interactive prompts,
confirmation modals, multiple-choice menus, and spoken voice inquiries.
"""

import os
import sys
import shutil
import subprocess
from typing import Any, Dict, List, Optional

from tools.laptop_work_tools import send_desktop_notification
from tools.ironman_protocols import play_stark_sound


def ask_user_confirmation(prompt: str, title: str = "Aradhya Confirmation Required", critical: bool = False) -> bool:
    """
    Prompt the user with an interactive Yes/No confirmation dialog.
    Uses native Linux desktop modal dialog (zenity) with automatic fallback to terminal prompt.
    
    Args:
        prompt: The question to ask the user (e.g. 'Sir, would you like me to delete the old backup archive?').
        title: Title of the confirmation dialog.
        critical: If True, uses alert styling and warning icon.
    """
    play_stark_sound("alert" if critical else "ack")

    # Try Zenity GUI Dialog
    if shutil.which("zenity") and os.getenv("DISPLAY"):
        try:
            icon_flag = "--warning" if critical else "--question"
            res = subprocess.run(
                ["zenity", icon_flag, "--title", title, "--text", prompt, "--ok-label", "Yes, Proceed", "--cancel-label", "No, Cancel", "--width", "380"],
                capture_output=True,
                timeout=30
            )
            return res.returncode == 0
        except Exception:
            pass

    # Terminal Fallback
    print(f"\n[Aradhya Interaction] {prompt} (y/n): ", end="", flush=True)
    try:
        ans = input().strip().lower()
        return ans in ("y", "yes", "true", "1")
    except Exception:
        return False


def prompt_user_input(question: str, title: str = "Aradhya Input Required", default_value: str = "") -> str:
    """
    Prompt the user for a text response or clarification.
    Uses native Linux desktop text entry dialog (zenity) with automatic fallback to terminal prompt.
    
    Args:
        question: The prompt asking the user for input or specification.
        title: Title of the dialog window.
        default_value: Initial text inside the input box.
    """
    play_stark_sound("ack")

    # Try Zenity GUI Entry
    if shutil.which("zenity") and os.getenv("DISPLAY"):
        try:
            cmd = ["zenity", "--entry", "--title", title, "--text", question, "--entry-text", default_value, "--width", "400"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if res.returncode == 0:
                return res.stdout.strip()
        except Exception:
            pass

    # Terminal Fallback
    print(f"\n[Aradhya Interaction] {question} [{default_value}]: ", end="", flush=True)
    try:
        ans = input().strip()
        return ans or default_value
    except Exception:
        return default_value


def ask_user_multiple_choice(question: str, options: List[str], title: str = "Aradhya Options Selection") -> str:
    """
    Present an interactive selection menu for the user to choose from multiple options.
    
    Args:
        question: The decision or choice question.
        options: List of choices (e.g. ['1. Deploy to Production', '2. Run Local Tests', '3. Abort']).
        title: Title of the choice dialog.
    """
    if not options:
        return ""

    play_stark_sound("protocol")

    # Try Zenity GUI List
    if shutil.which("zenity") and os.getenv("DISPLAY"):
        try:
            cmd = ["zenity", "--list", "--title", title, "--text", question, "--column", "Options", "--width", "420", "--height", "280"]
            cmd.extend(options)
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if res.returncode == 0:
                return res.stdout.strip()
        except Exception:
            pass

    # Terminal Fallback
    print(f"\n[Aradhya Interaction] {question}")
    for idx, opt in enumerate(options, 1):
        print(f"  {idx}. {opt}")
    print("Select option number or name: ", end="", flush=True)
    try:
        ans = input().strip()
        if ans.isdigit() and 1 <= int(ans) <= len(options):
            return options[int(ans) - 1]
        return ans
    except Exception:
        return options[0]


def display_user_message_box(message: str, title: str = "Aradhya Message", level: str = "info") -> None:
    """
    Display a native desktop message box to alert or inform the user.
    
    Args:
        message: Content text to display.
        title: Title of the message box.
        level: Severity level ('info', 'warning', 'error').
    """
    play_stark_sound("alert" if level in ("warning", "error") else "ack")

    if shutil.which("zenity") and os.getenv("DISPLAY"):
        try:
            flag = f"--{level}" if level in ("info", "warning", "error") else "--info"
            subprocess.Popen(["zenity", flag, "--title", title, "--text", message, "--width", "380"])
            return
        except Exception:
            pass

    send_desktop_notification(title, message)
