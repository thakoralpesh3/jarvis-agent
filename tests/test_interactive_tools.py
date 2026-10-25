"""
Tests for Interactive User Tools.
"""

from unittest.mock import patch
import pytest
from tools.interactive_tools import (
    ask_user_confirmation,
    prompt_user_input,
    ask_user_multiple_choice,
    display_user_message_box,
)


def test_ask_user_confirmation_terminal_yes():
    with patch("builtins.input", return_value="y"), patch("shutil.which", return_value=None):
        res = ask_user_confirmation("Confirm test action?")
        assert res is True


def test_ask_user_confirmation_terminal_no():
    with patch("builtins.input", return_value="n"), patch("shutil.which", return_value=None):
        res = ask_user_confirmation("Confirm test action?")
        assert res is False


def test_prompt_user_input_terminal():
    with patch("builtins.input", return_value="Custom User Response"), patch("shutil.which", return_value=None):
        res = prompt_user_input("What is your project name?", default_value="DefaultProject")
        assert res == "Custom User Response"


def test_prompt_user_input_default():
    with patch("builtins.input", return_value=""), patch("shutil.which", return_value=None):
        res = prompt_user_input("What is your project name?", default_value="DefaultProject")
        assert res == "DefaultProject"


def test_ask_user_multiple_choice_terminal():
    options = ["Option A", "Option B", "Option C"]
    with patch("builtins.input", return_value="2"), patch("shutil.which", return_value=None):
        res = ask_user_multiple_choice("Select an option:", options)
        assert res == "Option B"


def test_display_user_message_box():
    # Should execute without throwing exceptions
    display_user_message_box("Test informational notification", title="Unit Test", level="info")
