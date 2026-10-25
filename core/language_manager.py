"""
Multilingual Communication & Dynamic Language Switcher for JARVIS & Chamunda CEO.
Provides default Gujarati (ગુજરાતી) language support for understanding commands and responding,
with dynamic language switching to English, Hindi, and others.
"""

from typing import Any, Dict, List, Optional
from config.settings import DEFAULT_CONFIG_FILE, JarvisConfig, load_config, save_config
from tools.ironman_protocols import play_stark_sound
from tools.laptop_work_tools import send_desktop_notification


SUPPORTED_LANGUAGES = {
    "gujarati": {
        "code": "gu",
        "name": "Gujarati",
        "native_name": "ગુજરાતી",
        "greeting": "નમસ્તે સાહેબ, હું જાર્વિસ છું. આપનો શું આદેશ છે?",
        "confirmation": "ભાષા સફળતાપૂર્વક ગુજરાતીમાં સેટ થઈ ગઈ છે, સાહેબ. હવેથી હું તમારી સાથે ગુજરાતીમાં વાતચીત કરીશ.",
        "tts_lang": "gu",
        "tts_tld": "co.in"
    },
    "english": {
        "code": "en",
        "name": "English",
        "native_name": "English",
        "greeting": "At your service, Sir. How may I assist you today?",
        "confirmation": "Language successfully switched to English, Sir. All systems standing by.",
        "tts_lang": "en",
        "tts_tld": "co.uk"
    },
    "hindi": {
        "code": "hi",
        "name": "Hindi",
        "native_name": "हिन्दी",
        "greeting": "नमस्ते सर, मैं जार्विस हूँ। आज्ञा दीजिए, क्या सेवा करूँ?",
        "confirmation": "भाषा सफलतापूर्वक हिन्दी में सेट कर दी गई है, सर।",
        "tts_lang": "hi",
        "tts_tld": "co.in"
    },
    "marathi": {
        "code": "mr",
        "name": "Marathi",
        "native_name": "मराठी",
        "greeting": "नमस्कार साहेब, मी जार्विस आहे. काय आज्ञा आहे?",
        "confirmation": "भाषा यशस्वीरित्या मराठीमध्ये सेट केली आहे, साहेब.",
        "tts_lang": "mr",
        "tts_tld": "co.in"
    }
}


class LanguageManager:
    """Manages language settings, command comprehension instructions, and response translations."""

    def __init__(self, config: Optional[JarvisConfig] = None):
        self.config = config or load_config()

    def _normalize_lang(self, lang_input: str) -> str:
        """Convert input string to normalized language key."""
        clean = lang_input.strip().lower()
        if clean in ("gu", "guj", "gujarati", "ગુજરાતી"):
            return "gujarati"
        elif clean in ("en", "eng", "english"):
            return "english"
        elif clean in ("hi", "hin", "hindi", "हिन्दी"):
            return "hindi"
        elif clean in ("mr", "mar", "marathi", "मराठी"):
            return "marathi"
        return clean

    def get_current_language(self) -> Dict[str, Any]:
        """Return the currently configured language details."""
        norm = self._normalize_lang(self.config.language)
        info = SUPPORTED_LANGUAGES.get(norm, SUPPORTED_LANGUAGES["gujarati"])
        return {
            "key": norm,
            "name": info["name"],
            "native_name": info["native_name"],
            "code": info["code"]
        }

    def set_language(self, language: str, notify: bool = False) -> Dict[str, Any]:
        """Switch agent language dynamically and persist to configuration."""
        norm = self._normalize_lang(language)
        if norm not in SUPPORTED_LANGUAGES:
            supported = ", ".join([f"{v['name']} ({k})" for k, v in SUPPORTED_LANGUAGES.items()])
            return {
                "success": False,
                "message": f"અમાન્ય ભાષા વિકલ્પ (Invalid language: '{language}'). સમર્થિત ભાષાઓ (Supported languages): {supported}"
            }

        old_lang = self.config.language
        self.config.language = norm
        save_config(self.config)
        play_stark_sound("ack")

        info = SUPPORTED_LANGUAGES[norm]
        confirmation_msg = info["confirmation"]

        if notify:
            agent_name = getattr(self.config, "agent_name", "Aradhya")
            send_desktop_notification(
                f"{agent_name} Language: {info['native_name']}",
                confirmation_msg,
                details=f"Active language updated from {old_lang} to {info['name']}.",
                urgency="normal"
            )

        return {
            "success": True,
            "language": norm,
            "name": info["name"],
            "native_name": info["native_name"],
            "message": confirmation_msg
        }

    def list_supported_languages(self) -> str:
        """List all available languages and how to switch."""
        current = self.get_current_language()
        lines = [
            "### 🌐 JARVIS ઉપલબ્ધ ભાષાઓ (Available Languages):\n",
            f"- **હાલની ભાષા (Active Language):** **{current['native_name']} ({current['name']})**\n",
            "**સમર્થિત ભાષાઓ (Supported Options):**"
        ]
        for key, val in SUPPORTED_LANGUAGES.items():
            active_marker = " ★ [ચાલુ / ACTIVE]" if key == current["key"] else ""
            lines.append(f"- **{val['native_name']}** (`{key}` / `{val['code']}`){active_marker}")

        lines.append("\n**ભાષા બદલવા માટે આદેશ (Command to switch):**")
        lines.append("- `/lang gujarati` અથવા `/lang gu` (ગુજરાતી માટે)")
        lines.append("- `/lang english` અથવા `/lang en` (For English)")
        lines.append("- `/lang hindi` અથવા `/lang hi` (हिन्दी के लिए)")

        return "\n".join(lines)

    def get_system_language_instruction(self) -> str:
        """Generate precise LLM prompt directive for the active language."""
        norm = self._normalize_lang(self.config.language)
        
        if norm == "gujarati":
            return (
                "### 🌐 ભાષા અને સંચાર પ્રોટોકોલ (Language Protocol: Gujarati / ગુજરાતી):\n"
                "- **મુખ્ય ભાષા (Primary Language): ગુજરાતી (GUJARATI)**. By default, you must converse, explain, and reply in natural, polite, respectful Gujarati (ગુજરાતી).\n"
                "- **સંપૂર્ણ આદેશ સમજ (Command Understanding):** You must seamlessly understand user commands given in:\n"
                "  1. Pure Gujarati script (દા.ત., 'સ્ટોક ચેક કરો', 'નવી જોબ કાર્ડ બનાવો', 'વોલ્યુમ વધારો').\n"
                "  2. Romanized Gujarati / Gujlish in English alphabet (દા.ત., 'kem cho jarvis', 'Classic 350 nu job card banavo', 'battery voltage check karo', 'aaj no profit ketlo che').\n"
                "  3. Standard English commands (e.g., 'check inventory', 'run diagnostic sweep').\n"
                "- **પ્રતિસાદ શૈલી (Response Cadence):** Always reply in Gujarati (દા.ત., 'જી સાહેબ', 'તમારા આદેશ અનુસાર મેં...', 'ચામુંડા ઓટોમોબાઇલ રોયલ એનફિલ્ડ સર્વિસ'). Technical part names (e.g. Spark Plug, Disc Pad, Motul 15W-50), motorcycle models (Classic 350, Hunter 350, 650 Twins), file paths, and terminal commands should remain in English for absolute technical clarity, woven smoothly into Gujarati sentences.\n"
                "- **ભાષા પરિવર્તન:** જો વપરાશકર્તા સ્પષ્ટપણે અંગ્રેજી અથવા હિન્દીમાં બોલવાનું કહે, તો જ તે ભાષામાં બોલો."
            )
        elif norm == "hindi":
            return (
                "### 🌐 भाषा और संचार प्रोटोकॉल (Language Protocol: Hindi / हिन्दी):\n"
                "- **मुख्य भाषा (Primary Language): हिन्दी (HINDI)**. Default responses must be in polite, respectful Hindi ('जी सर', 'आपके आदेशानुसार...').\n"
                "- Seamlessly understand user input in Hindi script, Hinglish, or English.\n"
                "- Technical part names and commands may remain in English."
            )
        else:
            return (
                "### 🌐 Language Protocol: English:\n"
                "- **Primary Language: English**.\n"
                "- Respond in sophisticated, respectful British English cadence (Paul Bettany style).\n"
                "- Seamlessly understand commands in Gujarati, Hindi, or English."
            )


# Global singleton instance
_lang_mgr_instance: Optional[LanguageManager] = None


def get_language_manager() -> LanguageManager:
    global _lang_mgr_instance
    if _lang_mgr_instance is None:
        _lang_mgr_instance = LanguageManager()
    return _lang_mgr_instance


def get_active_language() -> str:
    """Return the active language key (e.g. 'gujarati', 'english')."""
    mgr = get_language_manager()
    return mgr.config.language
