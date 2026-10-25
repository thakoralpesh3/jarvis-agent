"""
Comprehensive Browser Controller for JARVIS.
Provides both full automated browser control (navigation, form filling, element clicking, data scraping)
and desktop browser control (tab switching, closing, refreshing, hotkey navigation).
"""

import time
import os
import sys
import types
from pathlib import Path
from typing import Any, Dict, List, Optional

# Linux compatibility shim for PyAutoGUI
if 'mouseinfo' not in sys.modules:
    sys.modules['mouseinfo'] = types.ModuleType('mouseinfo')
if 'tkinter' not in sys.modules:
    _tk = types.ModuleType('tkinter')
    _tk.TkVersion = 8.6
    sys.modules['tkinter'] = _tk

import pyautogui


class BrowserAutomationSession:
    """Manages a persistent Playwright browser instance across tool calls."""

    _instance = None

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = BrowserAutomationSession()
        return cls._instance

    def ensure_page(self, headless: bool = False):
        if self.page and not self.page.is_closed():
            return self.page

        from playwright.sync_api import sync_playwright
        if not self.playwright:
            self.playwright = sync_playwright().start()

        # Try to launch Chromium or system Chrome/Firefox
        try:
            self.browser = self.playwright.chromium.launch(headless=headless, channel="chrome")
        except Exception:
            try:
                self.browser = self.playwright.chromium.launch(headless=headless)
            except Exception:
                try:
                    self.browser = self.playwright.firefox.launch(headless=headless)
                except Exception:
                    self.browser = self.playwright.chromium.launch(headless=True)

        self.context = self.browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        self.page = self.context.new_page()
        return self.page

    def close(self):
        if self.page:
            try:
                self.page.close()
            except Exception:
                pass
            self.page = None
        if self.context:
            try:
                self.context.close()
            except Exception:
                pass
            self.context = None
        if self.browser:
            try:
                self.browser.close()
            except Exception:
                pass
            self.browser = None
        if self.playwright:
            try:
                self.playwright.stop()
            except Exception:
                pass
            self.playwright = None


# --- Automated Browser Session Tools ---

def browser_navigate(url: str, headless: bool = False) -> str:
    """
    Open an automated web browser session and navigate to a URL.
    
    Args:
        url: Full URL or domain (e.g. 'https://google.com', 'github.com/trending').
        headless: If False, opens a visible browser window on your screen.
    """
    clean_url = url if url.startswith("http") else f"https://{url}"
    try:
        session = BrowserAutomationSession.get_instance()
        page = session.ensure_page(headless=headless)
        response = page.goto(clean_url, wait_until="domcontentloaded", timeout=25000)
        title = page.title()
        status = response.status if response else 200
        return f"Successfully navigated to '{clean_url}' (Status {status}). Page Title: '{title}'"
    except Exception as e:
        return f"Browser Navigation Error: {str(e)}"


def browser_click_element(selector_or_text: str) -> str:
    """
    Click on any button, link, tab, or element on the active automated browser page.
    
    Args:
        selector_or_text: CSS selector, XPath, or human text on the element (e.g. 'Log in', 'Submit', '#search-button', 'text=Sign up').
    """
    try:
        session = BrowserAutomationSession.get_instance()
        if not session.page:
            return "Error: No active browser session. Call browser_navigate first."

        page = session.page
        # Try text-based click first if not an explicit selector
        if not selector_or_text.startswith("#") and not selector_or_text.startswith(".") and not selector_or_text.startswith("//"):
            try:
                page.get_by_role("button", name=selector_or_text).click(timeout=3000)
                return f"Clicked button with text '{selector_or_text}'."
            except Exception:
                try:
                    page.get_by_text(selector_or_text, exact=False).first.click(timeout=3000)
                    return f"Clicked element containing text '{selector_or_text}'."
                except Exception:
                    pass

        # Selector click
        page.locator(selector_or_text).first.click(timeout=6000)
        return f"Clicked element matching '{selector_or_text}'."
    except Exception as e:
        return f"Error clicking element: {str(e)}"


def browser_type_text(selector_or_text: str, text: str, press_enter: bool = False) -> str:
    """
    Fill or type text into an input field or search bar on the automated browser page.
    
    Args:
        selector_or_text: CSS selector, placeholder, or label of input field (e.g. 'input[name=q]', 'Search', 'Username').
        text: Text to input.
        press_enter: If True, presses Enter key after typing to submit.
    """
    try:
        session = BrowserAutomationSession.get_instance()
        if not session.page:
            return "Error: No active browser session. Call browser_navigate first."

        page = session.page
        try:
            locator = page.get_by_placeholder(selector_or_text)
            locator.fill(text, timeout=3000)
        except Exception:
            try:
                locator = page.get_by_label(selector_or_text)
                locator.fill(text, timeout=3000)
            except Exception:
                locator = page.locator(selector_or_text).first
                locator.fill(text, timeout=5000)

        if press_enter:
            page.keyboard.press("Enter")
            time.sleep(1)
            return f"Typed '{text}' into '{selector_or_text}' and pressed Enter."
        return f"Typed '{text}' into '{selector_or_text}'."
    except Exception as e:
        return f"Error typing into field: {str(e)}"


def browser_extract_page_content(selector: str = "body", max_characters: int = 3500) -> str:
    """
    Extract readable text content from the currently open automated browser page.
    
    Args:
        selector: CSS selector to extract from (defaults to 'body' for full page).
        max_characters: Limit on returned text size.
    """
    try:
        session = BrowserAutomationSession.get_instance()
        if not session.page:
            return "Error: No active browser session."

        page = session.page
        text = page.locator(selector).inner_text(timeout=5000)
        cleaned = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        if len(cleaned) > max_characters:
            return cleaned[:max_characters] + f"\n\n... (Content truncated at {max_characters} characters)"
        return cleaned if cleaned else "(Page body is empty)"
    except Exception as e:
        return f"Error extracting page content: {str(e)}"


def browser_take_page_screenshot(output_path: Optional[str] = None) -> str:
    """
    Capture a screenshot of the automated browser page.
    
    Args:
        output_path: Target image file path (defaults to /tmp/browser_snapshot.png).
    """
    try:
        session = BrowserAutomationSession.get_instance()
        if not session.page:
            return "Error: No active browser session."

        target = Path(output_path) if output_path else Path(f"/tmp/browser_page_{int(time.time())}.png")
        target.parent.mkdir(parents=True, exist_ok=True)
        session.page.screenshot(path=str(target), full_page=False)
        return f"Browser screenshot saved to '{str(target)}'."
    except Exception as e:
        return f"Error capturing browser screenshot: {str(e)}"


def browser_close_session() -> str:
    """
    Close the active automated browser session.
    """
    try:
        session = BrowserAutomationSession.get_instance()
        session.close()
        return "Automated browser session closed."
    except Exception as e:
        return f"Error closing browser: {str(e)}"


# --- Desktop Browser Control (Chrome / Firefox / Brave tabs) ---

def desktop_browser_new_tab(url: str = "") -> str:
    """
    Open a new tab in the active desktop browser and optionally navigate to a URL.
    
    Args:
        url: Optional URL to type in the new tab address bar.
    """
    try:
        pyautogui.hotkey("ctrl", "t")
        time.sleep(0.3)
        if url:
            clean_url = url if url.startswith("http") else f"https://{url}"
            pyautogui.write(clean_url, interval=0.01)
            pyautogui.press("enter")
            return f"Opened new browser tab and navigated to '{clean_url}'."
        return "Opened new browser tab."
    except Exception as e:
        return f"Error opening tab: {str(e)}"


def desktop_browser_close_tab() -> str:
    """
    Close the current tab in the active desktop browser (Ctrl+W).
    """
    try:
        pyautogui.hotkey("ctrl", "w")
        return "Closed active browser tab."
    except Exception as e:
        return f"Error closing tab: {str(e)}"


def desktop_browser_switch_tab(direction: str = "next") -> str:
    """
    Switch between open browser tabs in the active desktop browser.
    
    Args:
        direction: 'next' (forward) or 'previous' (backward).
    """
    try:
        if direction.lower() in ["prev", "previous", "back"]:
            pyautogui.hotkey("ctrl", "shift", "tab")
            return "Switched to previous browser tab."
        else:
            pyautogui.hotkey("ctrl", "tab")
            return "Switched to next browser tab."
    except Exception as e:
        return f"Error switching tab: {str(e)}"


def desktop_browser_reload_page(hard_reload: bool = False) -> str:
    """
    Reload/refresh the current page in the active desktop browser.
    
    Args:
        hard_reload: If True, bypasses cache (Ctrl+Shift+R).
    """
    try:
        if hard_reload:
            pyautogui.hotkey("ctrl", "shift", "r")
            return "Performed hard reload of browser page."
        else:
            pyautogui.hotkey("ctrl", "r")
            return "Reloaded browser page."
    except Exception as e:
        return f"Error reloading page: {str(e)}"


def desktop_browser_history_nav(direction: str = "back") -> str:
    """
    Navigate back or forward in browser history.
    
    Args:
        direction: 'back' (Alt+Left) or 'forward' (Alt+Right).
    """
    try:
        if direction.lower() in ["forward", "fwd"]:
            pyautogui.hotkey("alt", "right")
            return "Navigated forward in browser history."
        else:
            pyautogui.hotkey("alt", "left")
            return "Navigated backward in browser history."
    except Exception as e:
        return f"Error navigating history: {str(e)}"


def desktop_browser_find_on_page(query: str) -> str:
    """
    Open the in-page search bar in the browser (Ctrl+F) and search for a term.
    
    Args:
        query: Search string.
    """
    try:
        pyautogui.hotkey("ctrl", "f")
        time.sleep(0.2)
        pyautogui.write(query, interval=0.01)
        pyautogui.press("enter")
        return f"Searching page for '{query}'."
    except Exception as e:
        return f"Error searching page: {str(e)}"
