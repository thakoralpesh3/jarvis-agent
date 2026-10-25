"""
Dynamic Model Discovery, Version Tracking & Auto-Upgrade Engine for JARVIS.
Automatically queries Google GenAI API to discover newly released Gemini models
(e.g., automatically upgrading from Gemini 3.7 Flash to Gemini 3.8 Flash when released),
updates local configuration, and switches active models dynamically.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from google import genai

from config.settings import DEFAULT_CONFIG_FILE, JarvisConfig, load_config, save_config
from tools.ironman_protocols import play_stark_sound
from tools.laptop_work_tools import send_desktop_notification


class ModelManager:
    """Manages AI model discovery, version comparison, and auto-upgrade."""

    def __init__(self, config: Optional[JarvisConfig] = None):
        self.config = config or load_config()
        self.api_key = self.config.api_key or os.getenv("GEMINI_API_KEY", "")
        self._client: Optional[genai.Client] = None

    @property
    def client(self) -> Optional[genai.Client]:
        if self._client is None and self.api_key:
            try:
                self._client = genai.Client(api_key=self.api_key)
            except Exception:
                self._client = None
        return self._client

    def _parse_version(self, model_name: str) -> Tuple[float, str]:
        """
        Extract numeric version from model string (e.g., 'gemini-3.8-flash' -> (3.8, 'flash')).
        """
        clean = model_name.replace("models/", "")
        match = re.search(r"gemini-(\d+(?:\.\d+)?)", clean)
        version_num = float(match.group(1)) if match else 0.0
        tier = "argon" if "argon" in clean else ("flash" if "flash" in clean else ("pro" if "pro" in clean else "other"))
        return (version_num, tier)

    def discover_available_models(self) -> List[str]:
        """Query Google GenAI API to get list of accessible models."""
        if not self.client:
            # Fallback static ranked list if client unavailable
            return [
                "gemini-4-argon",
                "gemini-3.8-flash",
                "gemini-3.7-flash",
                "gemini-3.5-flash",
                "gemini-2.5-flash",
                "gemini-flash-latest",
                "gemini-3.1-pro-preview",
                "gemini-2.5-pro",
                "gemini-pro-latest"
            ]

        try:
            models = self.client.models.list()
            gemini_models = []
            for m in models:
                name = m.name.replace("models/", "")
                # Only include standard conversational / text / multimodal generation models
                if "gemini" in name and not any(x in name for x in ["tts", "image", "transcribe", "robotics", "computer-use", "customtools"]):
                    gemini_models.append(name)
            return sorted(gemini_models)
        except Exception as e:
            return [self.config.model_name]

    def get_latest_flash_model(self) -> str:
        """Find the newest available Gemini Flash model."""
        models = self.discover_available_models()
        flash_models = [m for m in models if "flash" in m and not "lite" in m and not "live" in m]
        
        # Sort by version number descending
        sorted_flash = sorted(
            flash_models,
            key=lambda x: (self._parse_version(x)[0], "latest" in x),
            reverse=True
        )
        return sorted_flash[0] if sorted_flash else self.config.model_name

    def get_latest_pro_model(self) -> str:
        """Find the newest available Gemini Pro model."""
        models = self.discover_available_models()
        pro_models = [m for m in models if "pro" in m]
        sorted_pro = sorted(
            pro_models,
            key=lambda x: (self._parse_version(x)[0], "latest" in x),
            reverse=True
        )
        return sorted_pro[0] if sorted_pro else self.config.pro_model_name

    def auto_upgrade_model(self, notify: bool = False) -> Dict[str, Any]:
        """
        Check if a newer Gemini model version is available than the current config.
        If available, automatically upgrade config and persist to ~/.jarvis/config.yaml.
        """
        current_model = self.config.model_name
        latest_flash = self.get_latest_flash_model()
        latest_pro = self.get_latest_pro_model()

        current_ver, _ = self._parse_version(current_model)
        latest_ver, _ = self._parse_version(latest_flash)

        upgraded = False
        old_model = current_model

        # Upgrade Flash if newer version discovered or if switching from older tier
        if latest_ver > current_ver or ("latest" in latest_flash and "latest" not in current_model):
            self.config.model_name = latest_flash
            upgraded = True

        # Check Pro as well
        current_pro_ver, _ = self._parse_version(self.config.pro_model_name)
        latest_pro_ver, _ = self._parse_version(latest_pro)
        if latest_pro_ver > current_pro_ver:
            self.config.pro_model_name = latest_pro
            upgraded = True

        if upgraded:
            save_config(self.config)
            play_stark_sound("protocol")
            
            summary = (
                f"🚀 **AI Engine Auto-Upgraded to Latest Model!**\n\n"
                f"- **Previous Model:** `{old_model}`\n"
                f"- **Active Upgraded Model:** **`{self.config.model_name}`**\n"
                f"- **Advanced Pro Model:** `{self.config.pro_model_name}`\n"
                f"- **Status:** Configuration saved to `{DEFAULT_CONFIG_FILE}`."
            )
            
            if notify:
                agent_name = getattr(self.config, "agent_name", "Aradhya")
                send_desktop_notification(
                    f"{agent_name} AI Engine Auto-Upgraded",
                    f"Now powered by {self.config.model_name} (Latest available model).",
                    details=summary,
                    urgency="normal"
                )
                
            return {
                "upgraded": True,
                "old_model": old_model,
                "new_model": self.config.model_name,
                "pro_model": self.config.pro_model_name,
                "message": summary
            }

        agent_name = getattr(self.config, "agent_name", "Aradhya")
        return {
            "upgraded": False,
            "current_model": current_model,
            "latest_available": latest_flash,
            "message": f"{agent_name} is already running on the latest available model: `{current_model}`."
        }

    def set_model(self, model_name: str, notify: bool = False) -> Dict[str, Any]:
        """Manually switch active AI model to a specific version."""
        clean_name = model_name.replace("models/", "").strip()
        available = self.discover_available_models()
        
        old_model = self.config.model_name
        self.config.model_name = clean_name
        save_config(self.config)
        play_stark_sound("ack")

        msg = f"Active AI model updated from `{old_model}` to **`{clean_name}`**."
        if notify:
            send_desktop_notification(
                "AI Model Switched",
                f"Active model set to {clean_name}",
                details=msg,
                urgency="normal"
            )
        return {
            "success": True,
            "old_model": old_model,
            "new_model": clean_name,
            "message": msg
        }

    def get_status_report(self) -> str:
        """Generate a complete status report of active and available models."""
        available = self.discover_available_models()
        latest_flash = self.get_latest_flash_model()
        latest_pro = self.get_latest_pro_model()
        
        lines = [
            "### 🧠 JARVIS AI Model Version Telemetry & Discovery:",
            f"- **Active Primary Model:** **`{self.config.model_name}`**",
            f"- **Active Pro Model:** **`{self.config.pro_model_name}`**",
            f"- **Latest Discovered Flash:** `{latest_flash}`",
            f"- **Latest Discovered Pro:** `{latest_pro}`",
            f"- **Auto-Upgrade Status:** {'✅ Optimal (Running latest version)' if self.config.model_name == latest_flash else '⚡ Upgrade Available: ' + latest_flash}",
            "\n**Available Models from Google GenAI API:**"
        ]
        for m in available[:12]:
            marker = " ★ (Active)" if m == self.config.model_name else ""
            lines.append(f"  • `{m}`{marker}")

        return "\n".join(lines)


# Global singleton
_model_manager_instance: Optional[ModelManager] = None


def get_model_manager() -> ModelManager:
    global _model_manager_instance
    if _model_manager_instance is None:
        _model_manager_instance = ModelManager()
    return _model_manager_instance


def get_active_model_name() -> str:
    """Get the currently active model name across all JARVIS modules."""
    mgr = get_model_manager()
    return mgr.config.model_name


def get_active_pro_model_name() -> str:
    """Get the currently active Pro model name across all JARVIS modules."""
    mgr = get_model_manager()
    return mgr.config.pro_model_name
