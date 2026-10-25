"""
Configuration settings for JARVIS Self-Learning Agent.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
import yaml

DEFAULT_CONFIG_DIR = Path.home() / ".jarvis"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.yaml"
DEFAULT_DB_FILE = DEFAULT_CONFIG_DIR / "memory.db"
DEFAULT_DYNAMIC_TOOLS_DIR = DEFAULT_CONFIG_DIR / "dynamic_tools"


@dataclass
class JarvisConfig:
    # Model Configuration
    model_name: str = "gemini-4-argon"
    pro_model_name: str = "gemini-4-argon"
    embedding_model_name: str = "text-embedding-004"
    api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))

    # Paths & Storage
    base_dir: Path = DEFAULT_CONFIG_DIR
    db_path: Path = DEFAULT_DB_FILE
    dynamic_tools_dir: Path = DEFAULT_DYNAMIC_TOOLS_DIR
    pid_file: Path = DEFAULT_CONFIG_DIR / "jarvis.pid"
    log_file: Path = DEFAULT_CONFIG_DIR / "daemon.log"

    # Agent Persona & Behavior
    agent_name: str = "Aradhya"
    user_name: str = field(default_factory=lambda: os.getenv("USER", "Sir"))
    language: str = "gujarati"  # Default language: Gujarati
    autonomous_mode: bool = True
    safe_commands_only: bool = False
    
    # Continuous Learning Settings
    auto_reflection: bool = True
    auto_preference_learning: bool = True
    max_relevant_lessons: int = 5
    max_relevant_facts: int = 10
    
    # UI & Audio (Default mode is PURELY TEXT until explicitly commanded to switch to voice)
    enable_voice_response: bool = False  # Text mode by default
    voice_commands_enabled: bool = False  # Text mode by default
    voice_name: str = "Puck"
    allow_unsolicited_notifications: bool = False  # Quiet mode: only show notifications when explicitly commanded!

    def __post_init__(self):
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.dynamic_tools_dir.mkdir(parents=True, exist_ok=True)


def load_config(config_path: Path | str | None = None) -> JarvisConfig:
    """Load configuration from YAML file or return defaults."""
    target_path = Path(config_path) if config_path else DEFAULT_CONFIG_FILE

    if target_path.exists():
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                
            model_name = data.get("model_name", "gemini-3.8-flash")
            pro_model_name = data.get("pro_model_name", "gemini-3.1-pro-preview")

            cfg = JarvisConfig(
                model_name=model_name,
                pro_model_name=pro_model_name,
                embedding_model_name=data.get("embedding_model_name", "text-embedding-004"),
                api_key=data.get("api_key", os.getenv("GEMINI_API_KEY", "")),
                base_dir=Path(data.get("base_dir", DEFAULT_CONFIG_DIR)),
                db_path=Path(data.get("db_path", DEFAULT_DB_FILE)),
                dynamic_tools_dir=Path(data.get("dynamic_tools_dir", DEFAULT_DYNAMIC_TOOLS_DIR)),
                agent_name=data.get("agent_name", "Aradhya"),
                user_name=data.get("user_name", os.getenv("USER", "Sir")),
                language=data.get("language", "gujarati"),
                autonomous_mode=data.get("autonomous_mode", True),
                safe_commands_only=data.get("safe_commands_only", False),
                auto_reflection=data.get("auto_reflection", True),
                auto_preference_learning=data.get("auto_preference_learning", True),
                max_relevant_lessons=data.get("max_relevant_lessons", 5),
                max_relevant_facts=data.get("max_relevant_facts", 10),
                enable_voice_response=data.get("enable_voice_response", False),
                voice_commands_enabled=data.get("voice_commands_enabled", False),
                voice_name=data.get("voice_name", "Puck"),
                allow_unsolicited_notifications=data.get("allow_unsolicited_notifications", False),
            )
            return cfg
        except Exception:
            return JarvisConfig()

    return JarvisConfig()


def save_config(config: JarvisConfig, config_path: Path | str | None = None) -> None:
    """Save configuration to YAML file."""
    target_path = Path(config_path) if config_path else DEFAULT_CONFIG_FILE
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Preserve existing API key if not specified in new config
    api_key_to_save = config.api_key
    if not api_key_to_save and target_path.exists():
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                old_data = yaml.safe_load(f) or {}
                api_key_to_save = old_data.get("api_key", "")
        except Exception:
            pass

    data = {
        "model_name": config.model_name,
        "pro_model_name": config.pro_model_name,
        "embedding_model_name": config.embedding_model_name,
        "api_key": api_key_to_save,
        "base_dir": str(config.base_dir),
        "db_path": str(config.db_path),
        "dynamic_tools_dir": str(config.dynamic_tools_dir),
        "agent_name": config.agent_name,
        "user_name": config.user_name,
        "language": config.language,
        "autonomous_mode": config.autonomous_mode,
        "safe_commands_only": config.safe_commands_only,
        "auto_reflection": config.auto_reflection,
        "auto_preference_learning": config.auto_preference_learning,
        "max_relevant_lessons": config.max_relevant_lessons,
        "max_relevant_facts": config.max_relevant_facts,
        "enable_voice_response": config.enable_voice_response,
        "voice_commands_enabled": config.voice_commands_enabled,
        "voice_name": config.voice_name,
        "allow_unsolicited_notifications": config.allow_unsolicited_notifications,
    }
    with open(target_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False)
