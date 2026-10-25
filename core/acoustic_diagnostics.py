"""
Royal Enfield Acoustic Engine Sound Diagnostic AI for Chamunda Automobile.
Analyzes actual audio recordings of Royal Enfield engines using Gemini Multimodal Audio
to diagnose tappet valve clearance, cam chain slack, piston slap, or exhaust leaks.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from google import genai
from google.genai import types

from config.settings import load_config
from tools.ironman_protocols import play_stark_sound


class REAcousticDiagnosticEngine:
    """Diagnoses Royal Enfield engine mechanical health from audio signatures."""

    def __init__(self):
        self.config = load_config()
        self.client = genai.Client(api_key=self.config.api_key) if self.config.api_key else None

    def diagnose_engine_sound(self, audio_file_path: Optional[str] = None, bike_model: str = "Classic 350") -> Dict[str, Any]:
        """Analyze Royal Enfield engine sound clip and diagnose mechanical faults."""
        play_stark_sound("protocol")
        
        if not audio_file_path or not Path(audio_file_path).exists():
            msg = (
                f"### 🔊 Royal Enfield Acoustic Engine Diagnostic AI:\n"
                f"- **Model Specified:** {bike_model}\n"
                f"- **Status:** ⚠️ **No audio file detected.**\n"
                f"- **Usage:** Please provide a `.wav` or `.mp3` audio recording of the engine (e.g. `/sound /path/to/engine_idle.wav {bike_model}`) to analyze acoustic harmonics."
            )
            return {"success": False, "diagnosis": msg, "error": "No audio file provided."}

        # Analyze actual audio file using Gemini Multimodal Audio
        if self.client and Path(audio_file_path).exists():
            try:
                audio_bytes = Path(audio_file_path).read_bytes()
                mime = "audio/wav" if audio_file_path.endswith(".wav") else "audio/mpeg"
                response = self.client.models.generate_content(
                    model=self.config.model_name,
                    contents=[
                        types.Part.from_bytes(data=audio_bytes, mime_type=mime),
                        f"You are the Master Mechanic at Chamunda Automobile Parts & Service, specializing strictly in Royal Enfield motorcycles. "
                        f"Analyze this actual engine audio recording for {bike_model}. Identify exact mechanical sounds (tappet clicking, chain slap, piston slap, exhaust leak), "
                        f"state the severity, and provide factory clearance/torque specs to repair it."
                    ]
                )
                diag_result = response.text or "Acoustic diagnosis completed."
                play_stark_sound("ack")
                return {"success": True, "diagnosis": diag_result}
            except Exception as e:
                return {"success": False, "diagnosis": f"Error analyzing audio: {str(e)}", "error": str(e)}

        return {"success": False, "diagnosis": "Gemini API client unavailable.", "error": "No API client."}
