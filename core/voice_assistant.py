"""
Voice Assistant subsystem for JARVIS.
Provides real-time Speech-To-Text (STT) via Gemini multimodal audio and Text-To-Speech (TTS) output.
"""

import os
import io
import time
import wave
import tempfile
import threading
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Callable
from google import genai
from google.genai import types

from config.settings import JarvisConfig


import hashlib

AUDIO_CACHE_DIR = Path.home() / ".jarvis" / "audio_cache"


def extract_human_conversational_text(text: str, lang: str = "gu") -> str:
    """
    Extract clean, natural, human conversational speech from raw agent responses.
    Strips markdown formatting, tables, ASCII borders, code blocks, diffs, terminal outputs,
    system paths, emojis, and symbols so Aradhya sounds like a natural human assistant
    rather than a robotic screen reader.
    """
    if not text or not text.strip():
        return ""

    import re

    # 1. Remove code blocks and inline code
    clean = re.sub(r"```[\s\S]*?```", "", text)
    clean = re.sub(r"`[^`]*`", "", clean)

    # 2. Remove markdown tables (lines containing table pipes or separators)
    clean_lines = []
    for line in clean.splitlines():
        line_s = line.strip()
        if line_s.startswith("|") or line_s.endswith("|") or "|---" in line_s or line_s.count("|") >= 2:
            continue
        if re.match(r"^[\-\*\=\_]{3,}$", line_s):
            continue
        clean_lines.append(line)
    clean = "\n".join(clean_lines)

    # 3. Remove markdown links and URLs
    clean = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", clean)
    clean = re.sub(r"http\S+", "", clean)

    # 4. Remove file paths like /home/alpesh/...
    clean = re.sub(r"\/[a-zA-Z0-9_\.\-]+(?:\/[a-zA-Z0-9_\.\-]+)+", "", clean)

    # 5. Remove markdown headers, list markers, blockquotes
    clean = re.sub(r"^[#>\s\-\*\+]+", "", clean, flags=re.MULTILINE)
    clean = re.sub(r"^\s*\d+\.\s*", "", clean, flags=re.MULTILINE)

    # 6. Remove formatting markers
    clean = re.sub(r"[\*_~]", "", clean)

    # 7. Phonetic replacements and English loanword transliteration for natural Gujarati flow
    if "gu" in lang.lower():
        clean = re.sub(r"%", " ટકા ", clean)
        clean = re.sub(r"&", " અને ", clean)
        loanwords = [
            (r"\blaptop\b", "લેપટોપ"),
            (r"\bspeed\b", "સ્પીડ"),
            (r"\bbattery\b", "બેટરી"),
            (r"\bchrome\b", "ક્રોમ"),
            (r"\bvolume\b", "વોલ્યુમ"),
            (r"\bbrightness\b", "બ્રાઇટનેસ"),
            (r"\bsystem\b", "સિસ્ટમ"),
            (r"\bonline\b", "ઓનલાઇન"),
            (r"\boffline\b", "ઓફલાઇન"),
            (r"\bprocess(?:es)?\b", "પ્રોસેસ"),
            (r"\btask(?:s)?\b", "કામ"),
            (r"\bRAM\b", "રેમ"),
            (r"\bCPU\b", "સીપીયુ"),
            (r"\bGB\b", "જીબી"),
            (r"\bMB\b", "એમબી"),
            (r"\bWi-?Fi\b", "વાઇફાઇ"),
            (r"\bPID\b", "પ્રોસેસ આઈડી"),
            (r"\bOK\b", "ઓકે"),
            (r"\bAlpesh\b", "અલ્પેશ"),
            (r"\bSir\b", "સાહેબ"),
        ]
        for pattern, repl in loanwords:
            clean = re.sub(pattern, repl, clean, flags=re.IGNORECASE)
    else:
        clean = re.sub(r"%", " percent ", clean)
        clean = re.sub(r"&", " and ", clean)

    # 8. Remove emojis and unusual symbols (keep Gujarati and Devanagari script)
    clean = re.sub(r"[^\w\s\.\,\?\!\:\'\-—\u0A80-\u0AFF\u0900-\u097F]", " ", clean)

    # 9. Clean whitespace and filter lines
    speech_sentences = []
    for line in clean.splitlines():
        line_str = " ".join(line.split()).strip()
        if not line_str:
            continue
        # Skip technical telemetry, bullet metrics, or key-value lines
        if re.search(r"(?:વપરાશ|મેમરી|ડિસ્ક|પ્રોસેસ|રેમ|સીપીયુ|utilization|usage|cache|telemetry|ram|cpu|status|state)\s*:", line_str, flags=re.IGNORECASE):
            continue
        if re.match(r"^[a-zA-Z\u0A80-\u0AFF\s]{1,15}\s*:\s*[\d\.\%\s]+$", line_str):
            continue
        speech_sentences.append(line_str)

    joined = " ".join(speech_sentences)
    joined = re.sub(r"\s+", " ", joined).strip()

    # Limit to first ~260 characters of clean human speech to avoid robotic lengthy monologues
    if len(joined) > 280:
        parts = re.split(r"([.?!])", joined)
        accum = ""
        for i in range(0, len(parts) - 1, 2):
            sentence = parts[i] + parts[i+1]
            if len(accum) + len(sentence) < 250:
                accum += " " + sentence.strip()
            else:
                break
        if accum.strip():
            joined = accum.strip()

    return joined


class VoiceAssistant:
    """Manages audio capture, microphone transcription via Gemini, and voice synthesis output."""

    def __init__(self, config: JarvisConfig):
        self.config = config
        self.client = genai.Client(api_key=config.api_key) if config.api_key else None
        self._is_listening = False
        self._is_speaking = False
        AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def speak(self, text: str) -> None:
        """
        Speak text aloud using human-like natural Neural speech synthesis (Edge-TTS Dhwani/Neerja, gTTS, and Pygame mixer).
        Extracts conversational sentences and cleans all markdown, tables, and syntax before speaking.
        """
        if not text or not text.strip():
            return

        # Skip actual audio playback during test suite runs
        if os.getenv("PYTEST_CURRENT_TEST"):
            return

        curr_lang = getattr(self.config, "language", "gujarati").lower()
        clean_text = extract_human_conversational_text(text, lang=curr_lang)
        if not clean_text:
            return

        def _play():
            try:
                self._is_speaking = True
                
                # Determine Neural Voice model
                neural_voice = "gu-IN-DhwaniNeural"
                if curr_lang in ("en", "english"):
                    neural_voice = "en-IN-NeerjaNeural"
                elif curr_lang in ("hi", "hindi"):
                    neural_voice = "hi-IN-SwaraNeural"

                text_hash = hashlib.md5(f"{neural_voice}_{clean_text}".encode("utf-8")).hexdigest()
                cached_audio = AUDIO_CACHE_DIR / f"{text_hash}.mp3"
                tmp_audio = str(cached_audio)

                tts_success = False
                if cached_audio.exists() and cached_audio.stat().st_size > 1000:
                    tts_success = True
                else:
                    # Tier 1: Microsoft Edge Neural Voice (ultra-realistic human intonation)
                    try:
                        import asyncio
                        import edge_tts

                        async def _edge_synth():
                            comm = edge_tts.Communicate(clean_text, neural_voice)
                            await comm.save(tmp_audio)

                        asyncio.run(_edge_synth())
                        if os.path.exists(tmp_audio) and os.path.getsize(tmp_audio) > 1000:
                            tts_success = True
                    except Exception:
                        tts_success = False

                    # Tier 2: gTTS (High-reliability fallback)
                    if not tts_success:
                        try:
                            from gtts import gTTS
                            lang_code = "gu"
                            tld = "co.in"
                            if curr_lang in ("en", "english"):
                                lang_code = "en"
                                tld = "co.in"
                            elif curr_lang in ("hi", "hindi"):
                                lang_code = "hi"
                                tld = "co.in"

                            tts = gTTS(text=clean_text, lang=lang_code, tld=tld, slow=False)
                            tts.save(tmp_audio)
                            if os.path.exists(tmp_audio) and os.path.getsize(tmp_audio) > 1000:
                                tts_success = True
                        except Exception:
                            tts_success = False

                # Tier 3: Local spd-say fallback
                if not tts_success:
                    if shutil.which("spd-say"):
                        try:
                            lang_flag = "gu" if curr_lang in ("gu", "gujarati") else "en"
                            subprocess.run(["spd-say", "-l", lang_flag, "-t", "female2", "-r", "-5", clean_text[:200]],
                                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
                        except Exception:
                            pass
                    return

                # Play audio: Use Pygame mixer first (native MP3 playback, zero CLI dependencies)
                played = False
                try:
                    import pygame
                    if not pygame.mixer.get_init():
                        pygame.mixer.init()
                    pygame.mixer.music.load(tmp_audio)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.08)
                    played = True
                except Exception:
                    pass

                # Fallback to mpv, ffplay, mpg123, or ffmpeg+paplay
                if not played and shutil.which("mpv"):
                    subprocess.run(["mpv", "--really-quiet", "--no-video", tmp_audio], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    played = True
                elif not played and shutil.which("ffplay"):
                    subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", tmp_audio], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    played = True
                elif not played and shutil.which("mpg123"):
                    subprocess.run(["mpg123", "-q", tmp_audio], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    played = True
                elif not played and shutil.which("ffmpeg") and (shutil.which("paplay") or shutil.which("aplay")):
                    wav_tmp = tmp_audio.replace(".mp3", ".wav")
                    subprocess.run(["ffmpeg", "-y", "-i", tmp_audio, wav_tmp], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    subprocess.run(["paplay" if shutil.which("paplay") else "aplay", wav_tmp], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    if os.path.exists(wav_tmp):
                        os.remove(wav_tmp)

                if os.path.exists(tmp_audio) and not str(tmp_audio).startswith(str(AUDIO_CACHE_DIR)):
                    os.remove(tmp_audio)
            except Exception:
                pass
            finally:
                self._is_speaking = False

        # Run speech in thread or synchronously
        t = threading.Thread(target=_play, daemon=True)
        t.start()
        t.join()  # Wait for speech to complete so JARVIS doesn't talk over itself

    def record_microphone_audio(self, duration_seconds: int = 5, sample_rate: int = 16000,
                                require_speech: bool = False) -> Optional[bytes]:
        """
        Record audio from the microphone with clean gain and optional speech presence check.
        """
        try:
            import sounddevice as sd
            import numpy as np

            # Record
            recording = sd.rec(
                int(duration_seconds * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype='int16'
            )
            sd.wait()

            max_amp = int(np.max(np.abs(recording)))
            if require_speech and max_amp < 1800:
                # Ambient silence / no speech detected
                return None

            # Gentle normalization only when speech is present to prevent amplifying room hiss
            if max_amp > 2000 and max_amp < 14000:
                scale = min(2.5, 20000.0 / float(max_amp))
                processed = np.clip(recording.astype(np.float32) * scale, -32767, 32767).astype(np.int16)
            else:
                processed = recording

            # Encode as WAV in memory
            wav_io = io.BytesIO()
            with wave.open(wav_io, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(sample_rate)
                wf.writeframes(processed.tobytes())

            return wav_io.getvalue()
        except Exception:
            # Fallback to 'arecord'
            if shutil.which("arecord"):
                try:
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                        tmp_wav = f.name
                    subprocess.run(
                        ["arecord", "-d", str(duration_seconds), "-f", "S16_LE", "-r", str(sample_rate), "-c", "1", tmp_wav],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    with open(tmp_wav, "rb") as f:
                        data = f.read()
                    if os.path.exists(tmp_wav):
                        os.remove(tmp_wav)
                    return data
                except Exception:
                    return None
            return None

    def transcribe_audio_with_gemini(self, wav_bytes: bytes) -> str:
        """
        Transcribe audio recording directly using Gemini Multimodal Audio capability with network auto-resume.
        """
        if not self.client or not wav_bytes:
            return ""

        from core.network_resilience import execute_with_network_resume, is_network_error

        # Prioritize gemini-3.5-flash for rapid, quota-friendly STT (<2.5s response)
        candidate_models = [
            "gemini-3.5-flash",
            "gemini-3.6-flash",
            "gemini-flash-latest",
            self.config.model_name,
            "gemini-3.7-flash"
        ]
        seen = set()
        models_to_try = [m for m in candidate_models if not (m in seen or seen.add(m))]

        def _call_stt():
            last_err = None
            audio_part = types.Part.from_bytes(
                data=wav_bytes,
                mime_type="audio/wav"
            )
            prompt_instruction = (
                "Transcribe the spoken audio accurately into text in the exact language spoken "
                "(Gujarati, English, Hindi, etc.). Use Gujarati script for Gujarati speech, and English for English words. "
                "Return ONLY the transcribed text. Do not add quotes, markdown, or commentary. "
                "If silence, background hum, or inaudible, return (silence)."
            )
            for model_id in models_to_try:
                try:
                    return self.client.models.generate_content(
                        model=model_id,
                        contents=[
                            audio_part,
                            prompt_instruction
                        ],
                        config=types.GenerateContentConfig(
                            temperature=0.0
                        )
                    )
                except Exception as e:
                    last_err = e
                    if is_network_error(e) and model_id == models_to_try[-1]:
                        raise e
                    continue
            if last_err:
                raise last_err
            return None

        try:
            response = execute_with_network_resume(_call_stt)
            text = (response.text or "").strip() if response else ""
            text = text.strip("'\" \n\t")
            if "(silence)" in text.lower():
                return ""
            return text
        except Exception:
            return ""
