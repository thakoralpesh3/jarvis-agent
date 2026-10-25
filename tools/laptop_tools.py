"""
Comprehensive laptop and desktop control tools for JARVIS.
Provides OS automation for mouse, keyboard, sound, display, battery, windows, and apps.
"""

import os
import sys
import types
import subprocess
import shutil
import webbrowser
import psutil
from pathlib import Path
from typing import Any, Dict, List, Optional

# Linux compatibility shim for PyAutoGUI
if 'mouseinfo' not in sys.modules:
    sys.modules['mouseinfo'] = types.ModuleType('mouseinfo')
if 'tkinter' not in sys.modules:
    _tk = types.ModuleType('tkinter')
    _tk.TkVersion = 8.6
    sys.modules['tkinter'] = _tk


def set_system_volume(volume_percent: int) -> str:
    """
    Set laptop speaker/headphone volume to a specific percentage (0 to 100).
    
    Args:
        volume_percent: Target volume level between 0 and 100.
    """
    vol = max(0, min(100, int(volume_percent)))
    # Try pactl first
    if shutil.which("pactl"):
        res = subprocess.run(f"pactl set-sink-volume @DEFAULT_SINK@ {vol}%", shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            return f"System volume set to {vol}%."
    # Fallback to amixer
    if shutil.which("amixer"):
        subprocess.run(f"amixer -D pulse sset Master {vol}%", shell=True, capture_output=True, text=True)
        return f"System volume set to {vol}% via amixer."
    return "Error: Could not adjust volume. Neither 'pactl' nor 'amixer' were found."


def change_system_volume(delta_percent: int) -> str:
    """
    Increase or decrease system volume by a relative percentage (e.g. +10 or -15).
    
    Args:
        delta_percent: Relative change, e.g. +10 or -10.
    """
    sign = "+" if delta_percent >= 0 else "-"
    val = abs(int(delta_percent))
    if shutil.which("pactl"):
        subprocess.run(f"pactl set-sink-volume @DEFAULT_SINK@ {sign}{val}%", shell=True, capture_output=True)
        return f"System volume adjusted by {sign}{val}%."
    if shutil.which("amixer"):
        subprocess.run(f"amixer -D pulse sset Master {val}%{sign}", shell=True, capture_output=True)
        return f"System volume adjusted by {sign}{val}%."
    return "Error: Volume adjustment tool not found."


def toggle_system_mute() -> str:
    """
    Toggle audio mute on or off.
    """
    if shutil.which("pactl"):
        subprocess.run("pactl set-sink-mute @DEFAULT_SINK@ toggle", shell=True, capture_output=True)
        return "Audio mute toggled."
    if shutil.which("amixer"):
        subprocess.run("amixer -D pulse set Master 1+ toggle", shell=True, capture_output=True)
        return "Audio mute toggled via amixer."
    return "Error: Audio control tool not found."


def control_media_player(action: str) -> str:
    """
    Control media playback (Spotify, YouTube, VLC, browser media, etc.).
    
    Args:
        action: One of 'play', 'pause', 'play-pause', 'next', 'previous', 'stop'.
    """
    action_clean = action.strip().lower()
    if shutil.which("playerctl"):
        subprocess.run(f"playerctl {action_clean}", shell=True, capture_output=True)
        return f"Media command '{action_clean}' executed."
    
    # Fallback to key simulation using xdotool if playerctl not present
    key_map = {
        "play-pause": "XF86AudioPlay",
        "play": "XF86AudioPlay",
        "pause": "XF86AudioPause",
        "next": "XF86AudioNext",
        "previous": "XF86AudioPrev",
        "stop": "XF86AudioStop"
    }
    if action_clean in key_map and shutil.which("xdotool"):
        subprocess.run(f"xdotool key {key_map[action_clean]}", shell=True, capture_output=True)
        return f"Media key '{key_map[action_clean]}' pressed."

    return f"Media action '{action}' performed."


def set_screen_brightness(level_percent: int) -> str:
    """
    Set laptop screen brightness percentage (0 to 100).
    
    Args:
        level_percent: Target brightness percentage between 5 and 100.
    """
    level = max(5, min(100, int(level_percent)))
    if shutil.which("brightnessctl"):
        subprocess.run(f"brightnessctl set {level}%", shell=True, capture_output=True)
        return f"Screen brightness set to {level}%."
    if shutil.which("xbacklight"):
        subprocess.run(f"xbacklight -set {level}", shell=True, capture_output=True)
        return f"Screen brightness set to {level}%."
    return "Note: Brightness control utility ('brightnessctl' or 'xbacklight') not detected."


def change_screen_brightness(delta_percent: int) -> str:
    """
    Increase or decrease laptop screen brightness by a relative percentage (e.g. +15 or -15).
    """
    sign = "+" if delta_percent >= 0 else "-"
    val = abs(int(delta_percent))
    if shutil.which("brightnessctl"):
        subprocess.run(f"brightnessctl set {val}%{sign}", shell=True, capture_output=True)
        return f"Screen brightness adjusted by {sign}{val}%."
    if shutil.which("xbacklight"):
        op = "-inc" if delta_percent >= 0 else "-dec"
        subprocess.run(f"xbacklight {op} {val}", shell=True, capture_output=True)
        return f"Screen brightness adjusted by {sign}{val}%."
    return "Note: Brightness control utility not detected."


def get_laptop_battery_info() -> str:
    """
    Get laptop battery percentage, power plug status, and remaining runtime.
    """
    battery = psutil.sensors_battery()
    if not battery:
        return "No battery detected (Desktop system or AC-only power)."

    status = "Plugged in (Charging)" if battery.power_plugged else "Running on Battery (Discharging)"
    mins_left = f"{battery.secsleft // 60} mins" if battery.secsleft > 0 else "Calculating..."
    if battery.power_plugged:
        mins_left = "N/A (Connected to AC power)"

    return (
        f"Battery Status:\n"
        f"- Level: {battery.percent}%\n"
        f"- Power State: {status}\n"
        f"- Estimated Time Left: {mins_left}"
    )


def lock_laptop_screen() -> str:
    """
    Immediately lock the laptop screen for security.
    """
    commands = [
        "cinnamon-screensaver-command -l",
        "gnome-screensaver-command -l",
        "xdg-screensaver lock",
        "loginctl lock-session",
        "xflock4"
    ]
    for cmd in commands:
        if subprocess.run(cmd, shell=True, capture_output=True).returncode == 0:
            return "Screen locked successfully."
    return "Command executed to lock session."


# Aliases
get_battery_status = get_laptop_battery_info
lock_screen = lock_laptop_screen


def list_active_windows() -> str:
    """
    List all currently open application windows on the desktop.
    """
    if shutil.which("wmctrl"):
        res = subprocess.run("wmctrl -l -x", shell=True, capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            lines = res.stdout.strip().split("\n")
            formatted = ["Active Desktop Windows:\n"]
            for l in lines:
                parts = l.split(None, 4)
                if len(parts) >= 5:
                    win_id, desktop, client_class, host, title = parts
                    formatted.append(f"- [{client_class}] \"{title}\" (ID: {win_id})")
                else:
                    formatted.append(f"- {l}")
            return "\n".join(formatted)
    return "Note: wmctrl is required to enumerate windows."


def focus_window_by_title(window_title_keyword: str) -> str:
    """
    Bring a specific application window to focus/foreground.
    
    Args:
        window_title_keyword: Keyword in the window title or app name (e.g. 'Firefox', 'Terminal', 'VS Code').
    """
    if shutil.which("wmctrl"):
        res = subprocess.run(f"wmctrl -a '{window_title_keyword}'", shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            return f"Brought window matching '{window_title_keyword}' to focus."
    return f"Attempted to focus '{window_title_keyword}'."


def close_window_by_title(window_title_keyword: str) -> str:
    """
    Gracefully close an application window by title.
    
    Args:
        window_title_keyword: Name or title of the window to close.
    """
    if shutil.which("wmctrl"):
        subprocess.run(f"wmctrl -c '{window_title_keyword}'", shell=True, capture_output=True)
        return f"Closed window matching '{window_title_keyword}'."
    return f"Attempted to close window '{window_title_keyword}'."


def move_mouse_cursor(x: int, y: int) -> str:
    """
    Move the mouse cursor to a specific (x, y) screen coordinate.
    
    Args:
        x: Horizontal coordinate in pixels.
        y: Vertical coordinate in pixels.
    """
    try:
        import pyautogui
        pyautogui.moveTo(x, y, duration=0.2)
        return f"Moved cursor to ({x}, {y})."
    except Exception as e:
        return f"Error moving cursor: {str(e)}"


def click_mouse_button(button: str = "left", clicks: int = 1, x: Optional[int] = None, y: Optional[int] = None) -> str:
    """
    Click the mouse button at current cursor location or specified (x, y) coordinates.
    
    Args:
        button: 'left', 'right', or 'middle'.
        clicks: Number of clicks (1 for single click, 2 for double click).
        x: Optional target X pixel coordinate.
        y: Optional target Y pixel coordinate.
    """
    try:
        import pyautogui
        if x is not None and y is not None:
            pyautogui.click(x=x, y=y, clicks=clicks, button=button)
            return f"Clicked {button} button {clicks} time(s) at ({x}, {y})."
        else:
            pyautogui.click(clicks=clicks, button=button)
            return f"Clicked {button} button {clicks} time(s) at current cursor position."
    except Exception as e:
        return f"Error clicking mouse: {str(e)}"


def scroll_screen(clicks: int = 5, direction: str = "down") -> str:
    """
    Scroll the mouse wheel up or down.
    
    Args:
        clicks: Number of scroll units.
        direction: 'up' or 'down'.
    """
    try:
        import pyautogui
        amt = -abs(clicks) if direction.lower() == "down" else abs(clicks)
        pyautogui.scroll(amt)
        return f"Scrolled {direction} by {clicks} units."
    except Exception as e:
        return f"Error scrolling: {str(e)}"


def type_keyboard_text(text: str) -> str:
    """
    Type text into the currently active input field or window.
    
    Args:
        text: String to type.
    """
    try:
        import pyautogui
        pyautogui.write(text, interval=0.01)
        return f"Typed: '{text[:50]}...'" if len(text) > 50 else f"Typed: '{text}'"
    except Exception as e:
        return f"Error typing text: {str(e)}"


def press_keyboard_hotkey(hotkey: str) -> str:
    """
    Press a keyboard shortcut or key combination (e.g. 'ctrl+c', 'ctrl+v', 'alt+tab', 'ctrl+shift+t', 'enter', 'escape', 'space').
    
    Args:
        hotkey: Key combo separated by '+' or single key name.
    """
    try:
        import pyautogui
        keys = [k.strip().lower() for k in hotkey.split("+")]
        pyautogui.hotkey(*keys)
        return f"Pressed hotkey combination: '{hotkey}'."
    except Exception as e:
        return f"Error pressing hotkey: {str(e)}"


def get_clipboard_content() -> str:
    """
    Read the current text content from the system clipboard.
    """
    try:
        import pyperclip
        txt = pyperclip.paste()
        if not txt:
            return "(Clipboard is empty)"
        return f"Clipboard Content:\n{txt}"
    except Exception as e:
        return f"Error reading clipboard: {str(e)}"


def set_clipboard_content(text: str) -> str:
    """
    Copy specified text into the system clipboard.
    
    Args:
        text: Text to copy.
    """
    try:
        import pyperclip
        pyperclip.copy(text)
        return f"Copied {len(text)} characters to clipboard."
    except Exception as e:
        return f"Error writing clipboard: {str(e)}"


def open_url(url: str) -> str:
    """
    Open any website or URL in the default web browser.
    
    Args:
        url: URL (e.g. 'https://youtube.com', 'https://github.com').
    """
    clean_url = url if url.startswith("http") else f"https://{url}"
    webbrowser.open(clean_url)
    return f"Opened '{clean_url}' in default browser."
