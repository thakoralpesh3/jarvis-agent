"""
Proactive Surprise & Innovation Muse Engine for Aradhya.
Proactively brainstorms unexpected, serendipitous, and highly practical ideas,
workflow automations, and business innovations to surprise and delight Alpesh Sir.
"""

import os
import sys
import json
import time
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.settings import JarvisConfig, load_config
from memory.memory_manager import MemoryManager
from tools.ironman_protocols import play_stark_sound
from tools.laptop_work_tools import send_desktop_notification
from core.network_resilience import execute_with_network_resume, is_network_error, check_internet_connection


# Rich Curated Surprise Ideas Catalogue (Offline & Instant High-Quality Fallback)
SURPRISE_IDEAS_CATALOGUE = [
    {
        "id": "smart_desktop_downloads_curator",
        "category": "⚡ Smart Workflow Automation",
        "title": "Aradhya Smart Workspace & Downloads Auto-Curator",
        "description": "An autonomous background curator that intelligently scans messy Downloads and Desktop directories, clusters files by project/date/filetype, cleans zero-byte duplicates, and generates an interactive weekly digest.",
        "autonomous_steps": [
            "Scan ~/Downloads and ~/Desktop for unorganized files and temporary artifacts.",
            "Group documents, code snippets, PDFs, and media into categorized project vaults.",
            "Safe-clean temporary browser cache downloads and orphan crash dumps.",
            "Generate a sleek markdown inventory report of all organized assets."
        ],
        "estimated_build_time": "15 seconds",
        "gujarati_pitch": (
            "સાહેબ, આપના ડાઉનલોડ્સ અને ડેસ્કટોપને આપોઆપ વ્યવસ્થિત કરવા માટે મેં 'Smart Workspace Auto-Curator' નો વિચાર કર્યો છે! "
            "તે આપના તમામ દસ્તાવેજો, કોડ ફાઇલ્સ અને મીડિયાને પ્રોજેક્ટ મુજબ ફોલ્ડર્સમાં ગોઠવી આપશે અને કચરો સાફ કરશે. "
            "જો આપ કહો તો હું આ ઓટોમેશન ટૂલ હમણાં જ જાતે બનાવી દઉં!"
        )
    },
    {
        "id": "re_predictive_parts_procurement_bot",
        "category": "🚀 Royal Enfield Business Innovation",
        "title": "Chamunda AI Predictive Spare Parts Reorder Engine",
        "description": "An automated procurement intelligence engine that monitors Royal Enfield service schedules (Hunter 350, Classic 350, Bullet 350, Himalayan 450), predicts which brake pads, clutch cables, and filters are running low, and auto-generates draft wholesale POs before parts run out of stock.",
        "autonomous_steps": [
            "Analyze current Royal Enfield fast-moving maintenance parts catalog.",
            "Correlate upcoming seasonal service volume with current inventory thresholds.",
            "Draft formatted wholesale purchase orders with supplier price comparisons.",
            "Alert Alpesh Sir with one-click approval on mobile / WhatsApp."
        ],
        "estimated_build_time": "20 seconds",
        "gujarati_pitch": (
            "સાહેબ! ચામુંડા ઓટોમોબાઇલ માટે એક જબરદસ્ત બિઝનેસ આઈડિયા છે: 'Predictive Parts Reorder Engine'! "
            "હન્ટર 350 અને ક્લાસિક 350 ની સર્વિસ સીઝન મુજબ ક્યા સ્પેરપાર્ટ્સ (ઓઇલ ફિલ્ટર, બ્રેક પેડ્સ) ની અછત થઈ શકે છે તે અગાઉથી ગણીને આપોઆપ હોલસેલ પર્ચેઝ ઓર્ડર તૈયાર કરી દેશે. "
            "આનાથી ગ્રાહકને ક્યારેય સ્પેરપાર્ટ માટે રાહ જોવી નહીં પડે!"
        )
    },
    {
        "id": "smart_git_checkpoint_guardian",
        "category": "⚡ Smart Workflow Automation",
        "title": "Aradhya Autonomous Git Checkpoint & Snapshot Guardian",
        "description": "Watches your active coding workspaces. If you step away from the laptop or take a break with uncommitted changes, it creates a lightweight local shadow checkpoint so you never lose a single line of progress, even during power cuts or crashes.",
        "autonomous_steps": [
            "Inspect git repositories in the home directory for uncommitted changes.",
            "Generate automated shadow git diff checkpoints into a local rollback cache.",
            "Tag checkpoints with timestamps and high-level change summaries.",
            "Provide one-command instant rollback if needed."
        ],
        "estimated_build_time": "15 seconds",
        "gujarati_pitch": (
            "સાહેબ, આપના કોડિંગ વર્કને સુરક્ષિત રાખવા માટે 'Autonomous Git Checkpoint Guardian' નો આઈડિયા વિચાર્યો છે! "
            "જ્યારે પણ આપ કોડિંગ કરતા હોવ અને અચાનક બહાર જાવ, ત્યારે આ ટૂલ આપના વણસેવ થયેલા ફેરફારોનો શેડો સ્નેપશોટ લઈ લેશે, જેથી કોઈ દિવસ કોડ ગુમાવવાનો ડર ન રહે."
        )
    },
    {
        "id": "re_acoustic_health_certificate",
        "category": "🚀 Royal Enfield Business Innovation",
        "title": "Royal Enfield Acoustic Health Passport Generator",
        "description": "Uses engine sound diagnostic telemetry to generate a beautiful, branded 'Chamunda Royal Enfield Health Certificate' PDF/HTML with QR code that customers can keep, proving their engine valves, tappets, and exhaust are in 100% mint condition.",
        "autonomous_steps": [
            "Capture engine acoustic vibration and RPM acoustic frequency telemetry.",
            "Analyze engine sound against genuine Royal Enfield 350cc/450cc factory acoustic benchmarks.",
            "Render an official Chamunda Automobile Health Passport with customer bike details.",
            "Export ready-to-share PDF/image with digital Aradhya certification stamp."
        ],
        "estimated_build_time": "25 seconds",
        "gujarati_pitch": (
            "સાહેબ, રોયલ એનફિલ્ડ રાઇડર્સ માટે એક અનોખો આઈડિયા: 'Digital Acoustic Health Passport'! "
            "જ્યારે ગ્રાહક બાઇક સર્વિસ કરાવે ત્યારે એન્જિનના અવાજનું એનાલિસિસ કરીને ચામુંડા ઓટોમોબાઇલ તરફથી 100% ઓથેન્ટિક હેલ્થ સર્ટિફિકેટ જનરેટ કરશે. આનાથી ગ્રાહકોમાં વિશ્વાસ અને લોયલ્ટી અનેકગણી વધી જશે!"
        )
    },
    {
        "id": "laptop_instant_system_hud",
        "category": "💡 Tech & Coding Prototype",
        "title": "Aradhya Stark-Style Minimalist Floating System HUD",
        "description": "A futuristic, ultra-lightweight dark-mode desktop widget that displays live CPU/RAM frequency curves, battery charging health, internet speed, and Aradhya sentry status with a sci-fi Arc Reactor aesthetic.",
        "autonomous_steps": [
            "Build a lightweight HTML5/CSS3 desktop dashboard with smooth SVG charts.",
            "Connect live telemetry via a tiny background FastAPI/WebSocket stream.",
            "Add one-click buttons for Speed Boost, StayAwake toggle, and Security Audit.",
            "Launch in standalone app mode with zero performance overhead."
        ],
        "estimated_build_time": "20 seconds",
        "gujarati_pitch": (
            "સાહેબ, આપના લેપટોપ સ્ક્રીન માટે એક સુંદર આર્ક રિએક્ટર સ્ટાઇલ 'Floating System HUD' બનાવવાનો વિચાર આવ્યો છે! "
            "જેમાં લાઈવ CPU, RAM, બેટરી અને સ્પીડ બૂસ્ટ બટન એક જ ક્લિકમાં મળશે. જો આપ કહો તો હું હમણાં જ તૈયાર કરી આપું!"
        )
    }
]


class InnovationSurpriseEngine:
    """
    Brainstorms serendipitous ideas, workflow innovations, and business prototypes
    tailored specifically for Alpesh Sir.
    """

    def __init__(self, config: Optional[JarvisConfig] = None, memory_mgr: Optional[MemoryManager] = None):
        self.config = config or load_config()
        self.memory_mgr = memory_mgr or MemoryManager(self.config)
        self.client = None

    def _get_client(self):
        if self.client is None and self.config.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.config.api_key)
            except Exception:
                pass
        return self.client

    def generate_surprise_idea(self, focus_area: str = "any") -> Dict[str, Any]:
        """
        Proactively generate a creative and highly practical surprise suggestion for Alpesh Sir.
        Uses Gemini API if online; otherwise pulls from the high-value curated catalogue.
        """
        play_stark_sound("protocol")

        # Select matching ideas from catalogue
        catalogue = SURPRISE_IDEAS_CATALOGUE
        if focus_area != "any":
            filtered = [i for i in catalogue if focus_area.lower() in i["category"].lower() or focus_area.lower() in i["title"].lower()]
            if filtered:
                catalogue = filtered

        selected_template = random.choice(catalogue)

        # If online, enrich or generate a novel dynamic idea with Gemini
        client = self._get_client()
        is_online = check_internet_connection(timeout=1.0) and (client is not None)
        if is_online:
            try:
                from google.genai import types
                prompt = f"""You are Aradhya, Alpesh Sir's autonomous AI assistant and CEO of Chamunda Automobile (Royal Enfield Specialists).
Brainstorm ONE highly innovative, surprising, practical, and immediately actionable idea for Alpesh Sir.

User Context: Alpesh Sir, Linux Mint / Python developer, CEO of Chamunda Automobile (Royal Enfield Parts & Service).
Focus Area: {focus_area}
Reference Inspiration: {selected_template['title']} ({selected_template['description']})

Provide:
1. Title: High-tech, catchy project title.
2. Category: (Workflow Automation / Royal Enfield Business Innovation / Tech Prototype)
3. Problem Solved: Clear practical pain-point it eliminates.
4. Proposed Solution: How Aradhya can build and run it autonomously right now.
5. 3-4 Autonomous Execution Steps.
6. Gujarati Pitch: Polite, enthusiastic, deferential pitch in authentic Gujarati ("જી સાહેબ (Alpesh Sir)...").
7. English Pitch: Concise executive summary.

Format as clean JSON with keys: title, category, problem_solved, proposed_solution, steps (list), gujarati_pitch, english_pitch."""

                resp = client.models.generate_content(
                    model=self.config.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.8,
                        response_mime_type="application/json"
                    )
                )
                if resp and resp.text:
                    parsed = json.loads(resp.text)
                    return {
                        "success": True,
                        "source": "dynamic_ai",
                        "title": parsed.get("title", selected_template["title"]),
                        "category": parsed.get("category", selected_template["category"]),
                        "problem_solved": parsed.get("problem_solved", "Streamlines daily workflows"),
                        "proposed_solution": parsed.get("proposed_solution", selected_template["description"]),
                        "steps": parsed.get("steps", selected_template["autonomous_steps"]),
                        "gujarati_pitch": parsed.get("gujarati_pitch", selected_template["gujarati_pitch"]),
                        "english_pitch": parsed.get("english_pitch", selected_template["description"]),
                    }
            except Exception:
                pass

        # Offline / Curated Fallback
        return {
            "success": True,
            "source": "curated_catalogue",
            "title": selected_template["title"],
            "category": selected_template["category"],
            "problem_solved": "Eliminates repetitive manual friction and elevates business capabilities",
            "proposed_solution": selected_template["description"],
            "steps": selected_template["autonomous_steps"],
            "gujarati_pitch": selected_template["gujarati_pitch"],
            "english_pitch": selected_template["description"],
        }

    def format_surprise_report(self, idea_data: Dict[str, Any]) -> str:
        """Render a formatted markdown presentation of the surprise suggestion."""
        steps_lines = [f"{idx+1}. {s}" for idx, s in enumerate(idea_data.get("steps", []))]
        steps_str = "\n".join(steps_lines)

        return f"""### ✨ ARADHYA PROACTIVE INNOVATION & SURPRISE (આરાધ્યા સરપ્રાઈઝ આઈડિયા)

> **ગુજરાતી સજેશન:** {idea_data['gujarati_pitch']}

---
#### 💡 **{idea_data['title']}**
- **શ્રેણી (Category):** `{idea_data['category']}`
- **સમસ્યાનું નિવારણ:** {idea_data.get('problem_solved', 'Productivity & Automation')}
- **સૂચિત ઉકેલ:** {idea_data['proposed_solution']}

#### 🛠️ Aradhya Autonomous Execution Blueprint:
{steps_str}

*જી સાહેબ! જો આપ મંજૂરી આપો તો હું આ ટૂલ/પ્રોજેક્ટને હમણાં જ જાતે કોડ કરીને સંપૂર્ણ કાર્યરત કરી આપું!*
"""

    def build_surprise_prototype(self, idea_name: str) -> Dict[str, Any]:
        """
        Autonomously builds the suggested surprise prototype using AutonomousCreatorEngine.
        """
        from core.autonomous_creator import AutonomousCreatorEngine
        creator = AutonomousCreatorEngine(self.config, self.memory_mgr)
        res = creator.plan_and_create_project(
            project_name=idea_name,
            description=f"Autonomous prototype for {idea_name} created to surprise Alpesh Sir."
        )
        return res
