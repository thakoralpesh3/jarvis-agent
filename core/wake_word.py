"""
Hands-Free Background Wake Word Listener for Aradhya ("Hey Aradhya" / "હે આરાધ્યા").
Continuously listens in background, audibly responds to the user, and captures follow-up instructions.
"""

import os
import sys
import time
import re
import io
import wave
import threading
from pathlib import Path
from typing import Optional, Callable, Tuple, Any

from config.settings import JarvisConfig, load_config
from tools.ironman_protocols import play_stark_sound
from tools.laptop_work_tools import send_desktop_notification
from core.voice_assistant import VoiceAssistant


WAKE_TRIGGERS = [
    # Gujarati script
    "હે આરાધ્યા", "આરાધ્યા", "હે આરાધ્ય", "આરાધ્ય", "હેય આરાધ્યા", "સુનો આરાધ્યા", "સાંભળો આરાધ્યા",
    # English & Romanized phonetic variants
    "hey aradhya", "aradhya", "aaradhya", "he aradhya", "ay aradhya", "hey aaradhya",
    "listen aradhya", "aradhya listen", "hey radhya", "radhya",
    # Legacy alias
    "hey jarvis", "jarvis"
]


def is_wake_word_triggered(text: str) -> Tuple[bool, str]:
    """
    Check if the text contains a wake word trigger.
    Returns (is_triggered, remaining_command_after_wake_word).
    """
    if not text or not text.strip():
        return False, ""

    clean = text.strip().lower()

    # Sort triggers longest first to match "hey aradhya" / "હે આરાધ્યા" before single-word "aradhya"
    sorted_triggers = sorted(WAKE_TRIGGERS, key=len, reverse=True)

    for trigger in sorted_triggers:
        trigger_low = trigger.lower()
        if trigger_low in clean:
            remainder = clean.replace(trigger_low, "").strip(" ,.-!?:")
            return True, remainder

    return False, ""


class WakeWordListener:
    """
    Hands-free background wake word listener.
    Continuously samples microphone audio in a daemon thread, monitors energy levels,
    detects 'Hey Aradhya', speaks back an audible acknowledgment, and captures user instructions.
    """

    def __init__(self, callback: Optional[Callable[[str], Any]] = None, config: Optional[JarvisConfig] = None):
        self.config = config or load_config()
        self.callback = callback
        self.is_listening = False
        self._thread: Optional[threading.Thread] = None
        self._voice: Optional[VoiceAssistant] = None
        self._agent: Optional[Any] = None
        self._lock = threading.Lock()

    @property
    def voice(self) -> VoiceAssistant:
        if self._voice is None:
            self._voice = VoiceAssistant(self.config)
        return self._voice

    def set_agent(self, agent: Any) -> None:
        """Attach active agent instance for autonomous background execution."""
        self._agent = agent

    def start(self) -> str:
        """Activate hands-free background wake word listener thread."""
        if self.is_listening:
            return "Wake word listener is already active, Sir."

        self.is_listening = True
        play_stark_sound("protocol")
        send_desktop_notification(
            "Aradhya Wake Word Armed",
            "Hands-free voice trigger 'Hey Aradhya' (હે આરાધ્યા) is active and listening in background.",
            urgency="low",
            user_commanded=False
        )

        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        return "Hands-free 'Hey Aradhya' wake word engine armed and listening in background, Sir."

    def stop(self) -> str:
        """Deactivate wake word listener."""
        self.is_listening = False
        return "Wake word listener deactivated, Sir."

    def _listen_loop(self) -> None:
        """Background continuous microphone monitoring loop with energy gating."""
        sample_rate = 16000
        chunk_seconds = 2.5

        # Avoid hardware microphone contention during unit tests
        if os.getenv("PYTEST_CURRENT_TEST"):
            while self.is_listening:
                time.sleep(0.5)
            return

        try:
            import sounddevice as sd
            import numpy as np
        except ImportError:
            sd = None
            np = None

        while self.is_listening:
            try:
                # If audio libraries are missing, sleep gracefully
                if sd is None or np is None:
                    time.sleep(2)
                    continue

                # Record 2.5 second audio buffer
                recording = sd.rec(
                    int(chunk_seconds * sample_rate),
                    samplerate=sample_rate,
                    channels=1,
                    dtype='int16'
                )
                sd.wait()

                if not self.is_listening:
                    break

                # Energy / RMS Gate: Only process when speech is detected (saves 99% CPU & network)
                max_amp = int(np.max(np.abs(recording)))
                if max_amp < 1600:
                    time.sleep(0.05)
                    continue

                # Encode to WAV in memory
                wav_io = io.BytesIO()
                with wave.open(wav_io, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(sample_rate)
                    wf.writeframes(recording.tobytes())
                wav_bytes = wav_io.getvalue()

                # Transcribe spoken chunk
                transcription = self.voice.transcribe_audio_with_gemini(wav_bytes)
                if not transcription:
                    continue

                # Check for wake word trigger
                triggered, command_remainder = is_wake_word_triggered(transcription)
                if triggered:
                    self.handle_wake_trigger(immediate_command=command_remainder)

            except Exception:
                time.sleep(1)

    def handle_wake_trigger(self, immediate_command: str = "") -> None:
        """
        Executed immediately when 'Hey Aradhya' / 'હે આરાધ્યા' is detected.
        Audibly responds to Alpesh Sir and captures/executes the instruction.
        """
        with self._lock:
            curr_lang = getattr(self.config, "language", "gujarati").lower()
            is_gu = curr_lang in ("gu", "gujarati")

            # 1. Play acknowledgment chime
            play_stark_sound("ack")

            # 2. Audible human response
            wake_greeting = (
                "જી અલ્પેશ સાહેબ! હું સાંભળી રહી છું, આપનો શું આદેશ છે?"
                if is_gu else
                "Yes Alpesh Sir! I am listening. What are your orders?"
            )

            send_desktop_notification(
                "આરાધ્યા સક્રિય (Aradhya Awakened)",
                wake_greeting,
                urgency="normal",
                user_commanded=False
            )

            # Speak response aloud
            self.voice.speak(wake_greeting)

            # 3. Check if user already provided the directive in the wake sentence
            user_instruction = immediate_command.strip()

            # 4. If no command in wake phrase, actively record user's follow-up instruction
            if not user_instruction:
                instruction_wav = self.voice.record_microphone_audio(
                    duration_seconds=5,
                    require_speech=True
                )
                if instruction_wav:
                    user_instruction = self.voice.transcribe_audio_with_gemini(instruction_wav)

            # 5. Execute user's voice instruction
            if user_instruction and "(silence)" not in user_instruction.lower():
                self._dispatch_instruction(user_instruction)
            else:
                standby_msg = "હું સ્ટેન્ડબાય પર છું, સાહેબ." if is_gu else "Standing by, Sir."
                self.voice.speak(standby_msg)

    def _dispatch_instruction(self, instruction: str) -> None:
        """Dispatch detected instruction to callback or agent."""
        curr_lang = getattr(self.config, "language", "gujarati").lower()
        is_gu = curr_lang in ("gu", "gujarati")

        ack_msg = "તરત જ કરું છું, સાહેબ." if is_gu else "Right away, Sir."
        self.voice.speak(ack_msg)

        if self.callback:
            self.callback(instruction)
        elif self._agent:
            result = self._agent.run_turn(instruction, speak_response=True)
            send_desktop_notification(
                "Aradhya Task Completed",
                f"Voice command executed: {instruction[:50]}",
                details=result[:150] if result else "",
                urgency="normal",
                user_commanded=True
            )
        else:
            # Fallback: queue background task in daemon
            from core.daemon import JarvisDaemon
            daemon = JarvisDaemon(self.config)
            daemon.queue_background_task(instruction)
            send_desktop_notification(
                "Aradhya Task Queued",
                f"Queued voice command: {instruction[:50]}",
                urgency="normal",
                user_commanded=True
            )


# Global singleton instance
_wake_listener: Optional[WakeWordListener] = None


def get_wake_listener(config: Optional[JarvisConfig] = None) -> WakeWordListener:
    global _wake_listener
    if _wake_listener is None:
        _wake_listener = WakeWordListener(config=config)
    return _wake_listener
