"""
Tests for Aradhya Hands-Free Wake Word Engine ("Hey Aradhya" / "હે આરાધ્યા"),
Human-like Natural Speech Extraction, and Immediate Hang/Lag Remediation.
"""

import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))
import pytest
from unittest.mock import MagicMock, patch

from config.settings import JarvisConfig
from core.wake_word import is_wake_word_triggered, WakeWordListener
from core.voice_assistant import extract_human_conversational_text, VoiceAssistant
from core.system_optimizer import SystemOptimizer


def test_wake_word_detection_english():
    """Verify wake word triggers correctly for English and phonetic phrases."""
    # Direct wake word only
    triggered, cmd = is_wake_word_triggered("Hey Aradhya")
    assert triggered is True
    assert cmd == ""

    # Wake word with directive in single sentence
    triggered, cmd = is_wake_word_triggered("Hey Aradhya please boost laptop speed")
    assert triggered is True
    assert "boost laptop speed" in cmd

    # Case insensitivity
    triggered, _ = is_wake_word_triggered("aradhya")
    assert triggered is True

    triggered, _ = is_wake_word_triggered("ay aradhya")
    assert triggered is True

    # Negative non-trigger
    triggered, cmd = is_wake_word_triggered("Good morning laptop")
    assert triggered is False
    assert cmd == ""


def test_wake_word_detection_gujarati():
    """Verify wake word triggers correctly for Gujarati script."""
    # Direct Gujarati wake word
    triggered, cmd = is_wake_word_triggered("હે આરાધ્યા")
    assert triggered is True
    assert cmd == ""

    triggered, cmd = is_wake_word_triggered("આરાધ્યા")
    assert triggered is True

    # Gujarati wake word with immediate command
    triggered, cmd = is_wake_word_triggered("હે આરાધ્યા લેપટોપ હેંગ થાય છે ઠીક કરો")
    assert triggered is True
    assert "હેંગ" in cmd or "ઠીક કરો" in cmd


def test_human_conversational_text_extraction():
    """Verify that raw technical markdown and tables are converted to natural human speech."""
    raw_markdown = """
### 🚀 ARADHYA PERFORMANCE OPTIMIZATION & SPEED BOOST REPORT
- **RAM વપરાશ:** 45% ➔ 42%
- **CPU:** 15%
| પ્રોસેસ | PID | સ્થિતિ |
|---|---|---|
| chrome | 1234 | Active |
| python | 5678 | Idle |

કામ સફળતાપૂર્વક પૂર્ણ થઈ ગયું છે, સાહેબ!
બીજું કોઈ કામ છે, સાહેબ?
સાહેબ, મારી પાસે આપના માટે એક નવો આઈડિયા/સજેશન છે, શું હું જણાવી શકું?
"""
    human_speech = extract_human_conversational_text(raw_markdown, lang="gu")

    # Tables and technical pipes must be completely absent
    assert "|" not in human_speech
    assert "---" not in human_speech
    assert "###" not in human_speech
    assert "🚀" not in human_speech
    assert "**" not in human_speech

    # Conversational human phrasing must be preserved
    assert "કામ સફળતાપૂર્વક પૂર્ણ થઈ ગયું છે, સાહેબ" in human_speech
    assert "બીજું કોઈ કામ છે, સાહેબ?" in human_speech
    assert "નવો આઈડિયા" in human_speech


def test_human_conversational_phonetics_gujarati():
    """Verify phonetic expansion for natural Gujarati audio pronunciation."""
    text = "CPU અને RAM વપરાશ 50% છે."
    speech = extract_human_conversational_text(text, lang="gu")

    assert "સીપીયુ" in speech
    assert "રેમ" in speech
    assert "ટકા" in speech
    assert "%" not in speech


def test_human_conversational_loanwords_gujarati():
    """Verify that English technical loanwords are transliterated to native Gujarati script."""
    text = "Laptop speed and battery are optimal."
    speech = extract_human_conversational_text(text, lang="gu")

    assert "લેપટોપ" in speech
    assert "સ્પીડ" in speech
    assert "બેટરી" in speech


def test_wake_word_listener_lifecycle():
    """Verify WakeWordListener start, stop, and agent attachment."""
    cfg = JarvisConfig()
    listener = WakeWordListener(config=cfg)

    assert listener.is_listening is False
    res_start = listener.start()
    assert "armed and listening" in res_start
    assert listener.is_listening is True

    res_stop = listener.stop()
    assert "deactivated" in res_stop
    assert listener.is_listening is False


def test_wake_word_handle_trigger_with_immediate_command():
    """Verify that wake trigger with immediate command directly dispatches."""
    callback_mock = MagicMock()
    cfg = JarvisConfig()
    listener = WakeWordListener(callback=callback_mock, config=cfg)

    # Trigger with immediate instruction
    listener.handle_wake_trigger(immediate_command="લેપટોપ સ્પીડ વધારો")

    callback_mock.assert_called_once_with("લેપટોપ સ્પીડ વધારો")


def test_hang_and_lag_immediate_remediation():
    """Verify that SystemOptimizer detects indicators and takes remediation steps."""
    optimizer = SystemOptimizer()
    indicators = optimizer.detect_hang_and_lag_indicators()

    assert "is_hanging" in indicators
    assert "is_lagging" in indicators
    assert "severity" in indicators
    assert "cpu_percent" in indicators
    assert "ram_percent" in indicators

    # Run auto remedy
    remedy = optimizer.auto_remedy_hang_and_lag(aggressive=False)
    assert remedy["success"] is True
    assert "gujarati_summary" in remedy
    assert "english_summary" in remedy
    assert "લેપટોપ હેંગિંગ અને લેગિંગ સફળતાપૂર્વક સુધારી" in remedy["gujarati_summary"]
