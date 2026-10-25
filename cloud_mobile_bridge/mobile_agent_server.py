"""
24/7 Cloud Mobile Bridge & Standby Sentinel for Aradhya.
Allows Alpesh Sir to access Aradhya from any mobile phone, tablet, or web browser
24 hours a day, 7 days a week, even when his physical laptop is completely powered OFF.
Provides FastAPI Web Portal, REST API, Cloud Task Mailbox, and Telegram Bot worker.
"""

import os
import sys
import json
import time
import uuid
import threading
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from google import genai
from google.genai import types

# Add parent paths for tools and enterprise modules
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")

try:
    from inventory_engine import ChamundaInventoryManager
    from service_engine import ChamundaServiceManager
    from billing_engine import ChamundaBillingManager
except ImportError:
    ChamundaInventoryManager = None
    ChamundaServiceManager = None
    ChamundaBillingManager = None

TELEGRAM_API_BASE = "https://api.telegram.org/bot"

# Storage for cloud mailbox & heartbeat
DATA_DIR = Path.home() / ".jarvis" / "cloud_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
QUEUE_FILE = DATA_DIR / "cloud_tasks.json"
HEARTBEAT_FILE = DATA_DIR / "laptop_heartbeat.json"


class ChatRequest(BaseModel):
    message: str


class HeartbeatRequest(BaseModel):
    hostname: Optional[str] = "laptop"
    battery_percent: Optional[int] = None
    power_plugged: Optional[bool] = None
    cpu_percent: Optional[float] = None
    ram_percent: Optional[float] = None
    agent_status: Optional[str] = "nominal"


class TaskCompleteRequest(BaseModel):
    task_id: str
    result: Any
    success: bool = True


class CommandResponse(dict):
    """Convenience dict wrapper that also supports direct string checks and formatting."""
    def __contains__(self, item: Any) -> bool:
        if isinstance(item, str) and item.lower() in self.get("reply", "").lower():
            return True
        return super().__contains__(item)

    def __str__(self) -> str:
        return self.get("reply", "")

    def lower(self) -> str:
        return self.get("reply", "").lower()


class CloudMobileAgent:
    """
    24/7 Cloud Host Agent and Standby Sentinel for Aradhya.
    Accessible from mobile phones via Web UI, REST API, or Telegram Bot.
    Operates autonomously even when the user's laptop is powered off.
    """

    def __init__(self, gemini_api_key: Optional[str] = None, telegram_bot_token: Optional[str] = None):
        self.api_key = gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        self.bot_token = telegram_bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.inv_mgr = ChamundaInventoryManager() if ChamundaInventoryManager else None
        self.srv_mgr = ChamundaServiceManager() if ChamundaServiceManager else None
        self.bill_mgr = ChamundaBillingManager() if ChamundaBillingManager else None

    # -------------------------------------------------------------------------
    # 1. Laptop Heartbeat & State Telemetry
    # -------------------------------------------------------------------------
    def is_laptop_online(self) -> bool:
        """Returns True if local laptop sent a heartbeat within the last 180 seconds."""
        if not HEARTBEAT_FILE.exists():
            return False
        try:
            data = json.loads(HEARTBEAT_FILE.read_text(encoding="utf-8"))
            last_ping = data.get("timestamp", 0)
            return (time.time() - last_ping) < 180
        except Exception:
            return False

    def record_heartbeat(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Record heartbeat received from physical laptop."""
        heartbeat_data = {
            "timestamp": time.time(),
            "time_str": time.strftime("%Y-%m-%d %H:%M:%S"),
            "info": info
        }
        try:
            HEARTBEAT_FILE.write_text(json.dumps(heartbeat_data, indent=2), encoding="utf-8")
        except Exception:
            pass
        return {"status": "ok", "laptop_online": True, "pending_tasks": len(self.get_pending_tasks())}

    def get_laptop_telemetry(self) -> Dict[str, Any]:
        """Get latest recorded telemetry about physical laptop."""
        is_online = self.is_laptop_online()
        details = {}
        if HEARTBEAT_FILE.exists():
            try:
                data = json.loads(HEARTBEAT_FILE.read_text(encoding="utf-8"))
                details = data.get("info", {})
                details["last_seen"] = data.get("time_str", "Unknown")
            except Exception:
                pass

        return {
            "is_online": is_online,
            "status_label": "ONLINE (Local Actuation Active)" if is_online else "OFFLINE / ASLEEP (Cloud Sentinel Active)",
            "details": details
        }

    # -------------------------------------------------------------------------
    # 2. Cloud Task Mailbox & Queue
    # -------------------------------------------------------------------------
    def _read_tasks(self) -> List[Dict[str, Any]]:
        if not QUEUE_FILE.exists():
            return []
        try:
            return json.loads(QUEUE_FILE.read_text(encoding="utf-8") or "[]")
        except Exception:
            return []

    def _write_tasks(self, tasks: List[Dict[str, Any]]) -> None:
        try:
            QUEUE_FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")
        except Exception:
            pass

    def queue_laptop_task(self, command: str, source: str = "cloud_web") -> Dict[str, Any]:
        """Enqueue a directive intended for the physical laptop to execute once it boots/wakes."""
        tasks = self._read_tasks()
        task_id = f"cloud_task_{int(time.time())}_{uuid.uuid4().hex[:4]}"
        entry = {
            "id": task_id,
            "command": command,
            "source": source,
            "status": "pending_laptop_wake",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "completed_at": None,
            "result": None
        }
        tasks.append(entry)
        self._write_tasks(tasks)
        return entry

    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Fetch all directives queued for the laptop that have not yet been executed."""
        tasks = self._read_tasks()
        return [t for t in tasks if t.get("status") == "pending_laptop_wake"]

    def complete_task(self, task_id: str, result: Any, success: bool = True) -> bool:
        """Mark a queued task as completed by the local laptop."""
        tasks = self._read_tasks()
        updated = False
        for t in tasks:
            if t.get("id") == task_id:
                t["status"] = "completed" if success else "failed"
                t["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                t["result"] = result
                updated = True
                break
        if updated:
            self._write_tasks(tasks)
        return updated

    # -------------------------------------------------------------------------
    # 3. Command Processing & Gemini Cloud Reasoning
    # -------------------------------------------------------------------------
    def process_command(self, text: str, source: str = "web") -> Dict[str, Any]:
        """
        Handle incoming text commands from mobile phone or web portal.
        Determines whether instruction is a cloud conversation or an offline laptop directive.
        """
        raw = (text or "").strip()
        t_clean = raw.lower()

        if not raw:
            return CommandResponse({
                "reply": "નમસ્તે અલ્પેશ સાહેબ! હું ૨૪/૭ ક્લાઉડ સેન્ટ્રી આરાધ્યા છું. આજે મારા માટે શું આદેશ છે?",
                "task_queued": False,
                "laptop_online": self.is_laptop_online()
            })

        # Check if the user is asking about laptop status
        if any(w in t_clean for w in ["laptop status", "લેપટોપ સ્ટેટસ", "લેપટોપ ચાલુ છે", "is laptop on", "લેપટોપ બંધ છે"]):
            telem = self.get_laptop_telemetry()
            if telem["is_online"]:
                rep = "જી સાહેબ! આપનું લેપટોપ હાલમાં **ઓનલાઇન (Online)** છે અને સંપૂર્ણપણે સક્રિય છે. સ્થાનિક આરાધ્યા તમામ ટાસ્ક તાત્કાલિક પૂર્ણ કરવા તૈયાર છે."
            else:
                rep = "જી સાહેબ! આપનું લેપટોપ હાલમાં **બંધ / સ્લીપ (Offline / Asleep)** મોડમાં છે. પરંતુ હું ક્લાઉડ સેન્ટ્રી તરીકે ૨૪/૭ હાજર છું. જો આપ કોઈ કામ સોંપશો તો હું તેને સુરક્ષિત રીતે ક્લાઉડ કતારમાં નોંધી લઈશ અને લેપટોપ ચાલુ થતાં જ તે પૂર્ણ થઈ જશે."
            return CommandResponse({"reply": rep, "task_queued": False, "laptop_online": telem["is_online"]})

        # Check if command is an explicit laptop action while laptop is offline
        laptop_action_keywords = [
            "speed", "boost", "સ્પીડ", "બૂસ્ટ", "હેંગ", "sluggish",
            "ઓપન", "open", "ડાઉનલોડ", "download", "ફાઇલ", "file",
            "સ્ક્રીનશોટ", "screenshot", "સ્ક્રીન લોક", "lock screen", "લોક કરો",
            "સિક્યુરિટી", "security", "પોર્ટ", "port", "backdoor", "બેકડોર",
            "રન", "run", "exec", "kill", "બંધ કરો", "કમાન્ડ", "command", "પ્રોસેસ", "process"
        ]
        is_laptop_directive = any(w in t_clean for w in laptop_action_keywords) or t_clean.startswith(("run ", "exec ", "$ ", "/work ", "/bg "))

        if is_laptop_directive and not self.is_laptop_online():
            task = self.queue_laptop_task(raw, source=source)
            rep = (
                f"જી સાહેબ! આપનું લેપટોપ હાલમાં **બંધ (Offline / Asleep)** છે.\n\n"
                f"મેં આપનો આદેશ ક્લાઉડ કતાર (Task Mailbox: `{task['id']}`) માં સુરક્ષિત રીતે સેવ કરી દીધો છે:\n"
                f"> **આદેશ:** `{raw}`\n\n"
                f"જેવું આપનું લેપટોપ ચાલુ થશે, સ્થાનિક આરાધ્યા આ કાર્ય આપોઆપ પૂર્ણ કરીને રિપોર્ટ સબમિટ કરશે."
            )
            return CommandResponse({"reply": rep, "task_queued": True, "task_id": task["id"], "laptop_online": False})

        # Chamunda Genuine Business Data Queries (No Fake Data)
        if t_clean in ("/ceo", "/revenue", "/business", "ceo", "revenue"):
            if self.inv_mgr and self.srv_mgr:
                val = self.inv_mgr.get_total_inventory_valuation()
                jobs = self.srv_mgr.get_all_job_cards()
                low = self.inv_mgr.get_low_stock_alerts()
                return CommandResponse({
                    "reply": (
                        f"👑 *CHAMUNDA AUTOMOBILE • ૨૪/૭ ક્લાઉડ બિઝનેસ ઓવરવ્યૂ*\n\n"
                        f"📦 *Total Stock:* {val['total_units_in_stock']} Units ({val['total_distinct_skus']} SKUs)\n"
                        f"💰 *ઇન્વેન્ટરી MRP વેલ્યુ:* ₹{val['mrp_valuation_inr']:,}\n"
                        f"📈 *અંદાજિત ગ્રોસ નફો:* ₹{val['expected_gross_profit_inr']:,}\n"
                        f"🏍️ *સક્રિય જોબ કાર્ડ્સ:* {len(jobs)} in bay\n"
                        f"⚠️ *રી-ઓર્ડર ચેતવણી:* {len(low)} items\n\n"
                        f"_આરાધ્યા ક્લાઉડ સેન્ટ્રી ૨૪/૭ આપની સેવામાં હાજર છે, સાહેબ._"
                    ),
                    "task_queued": False,
                    "laptop_online": self.is_laptop_online()
                })

        # Spares lookup
        if t_clean.startswith(("/parts", "/part", "પાર્ટ્સ")):
            query = raw.split(" ", 1)[1].strip() if " " in raw else ""
            if self.inv_mgr:
                matches = self.inv_mgr.search_parts(query)
                if not matches:
                    return CommandResponse({"reply": f"❌ '{query}' માટે કોઈ રોયલ એનફિલ્ડ સ્પેર પાર્ટ્સ મળ્યા નથી.", "task_queued": False, "laptop_online": self.is_laptop_online()})
                res = [f"🏍️ *Royal Enfield Spares for '{query}':*\n"]
                for p in matches[:5]:
                    res.append(f"• *{p['name']}* (`{p['part_id']}`)\n  Stock: *{p['stock']}* | MRP: *₹{p['mrp']}*")
                return CommandResponse({"reply": "\n".join(res), "task_queued": False, "laptop_online": self.is_laptop_online()})

        # Bike diagnostics lookup
        if t_clean.startswith(("/diag", "/re-diag", "ડાયગ્નોસ")):
            sym = raw.split(" ", 1)[1].strip() if " " in raw else "tappet noise"
            if self.srv_mgr:
                diag = self.srv_mgr.diagnose_fault(sym)
                return CommandResponse({
                    "reply": (
                        f"🔧 *Royal Enfield Diagnostic Report:*\n\n"
                        f"🎯 *Cause:* {diag['root_cause']}\n"
                        f"🛠️ *Directive:* Adjust valve clearance and tappet screws to factory specs.\n"
                        f"💵 *Labor:* ₹{diag['estimated_labor_inr']} | ⏱️ {diag['turnaround_time']}\n"
                        f"📦 *Spares:* {', '.join(diag['parts_needed'])}"
                    ),
                    "task_queued": False,
                    "laptop_online": self.is_laptop_online()
                })

        # General Aradhya Reasoning via Gemini (Cloud Intelligence)
        if self.client:
            laptop_state_str = "ONLINE" if self.is_laptop_online() else "POWERED OFF / ASLEEP"
            prompt = f"""You are Aradhya, the supreme autonomous AI super-intelligence system and personal executive assistant to Alpesh Sir (your Creator and Chairman).
You are running 24/7 on the Cloud Standby Sentinel, accessible directly from Alpesh Sir's mobile phone or web browser.
Current Laptop State: {laptop_state_str}.
Even though the physical laptop may be currently turned off, you are 100% active in the cloud to answer questions, brainstorm, write code, provide strategic analysis, and accept commands.

Directives:
1. Always maintain the Aradhya persona: highly capable, proactive, dignified, polite deference ("Right away, Sir", "At your service, Alpesh Sir", "જી સાહેબ", "હું હમણાં જ કરું છું").
2. Default language: natural, polite Gujarati unless the user speaks in English.
3. If the user asks about the laptop, inform them gracefully about its current state.

User Message: {raw}

Aradhya Executive Response:"""

            try:
                active_model = os.getenv("MODEL_NAME", "gemini-3.8-flash")
                resp = self.client.models.generate_content(
                    model=active_model,
                    contents=prompt
                )
                rep_text = resp.text or "જી સાહેબ, હું સાંભળી રહી છું."
                return CommandResponse({"reply": rep_text, "task_queued": False, "laptop_online": self.is_laptop_online()})
            except Exception as e:
                return CommandResponse({"reply": f"ક્લાઉડ સેન્ટ્રી એરર: {str(e)}", "task_queued": False, "laptop_online": self.is_laptop_online()})

        return CommandResponse({
            "reply": "જી સાહેબ, કૃપા કરીને ક્લાઉડ એન્વાયર્નમેન્ટમાં GEMINI_API_KEY કન્ફિગર કરો.",
            "task_queued": False,
            "laptop_online": self.is_laptop_online()
        })

    # -------------------------------------------------------------------------
    # 4. Telegram Bot Worker
    # -------------------------------------------------------------------------
    def _telegram_api_call(self, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.bot_token:
            return {"ok": False, "error": "TELEGRAM_BOT_TOKEN not configured"}
        url = f"{TELEGRAM_API_BASE}{self.bot_token}/{method}"
        try:
            req_data = json.dumps(data).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=req_data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def send_telegram_message(self, chat_id: int | str, text: str, parse_mode: str = "Markdown") -> Dict[str, Any]:
        return self._telegram_api_call("sendMessage", {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        })

    def run_telegram_polling(self) -> None:
        if not self.bot_token:
            return
        offset = 0
        while True:
            try:
                res = self._telegram_api_call("getUpdates", {"offset": offset, "timeout": 20})
                if res.get("ok") and res.get("result"):
                    for update in res["result"]:
                        offset = update["update_id"] + 1
                        msg = update.get("message") or update.get("edited_message")
                        if not msg:
                            continue
                        chat_id = msg["chat"]["id"]
                        text = msg.get("text", "")
                        if "voice" in msg:
                            self.send_telegram_message(chat_id, "🎙️ _આપનો વોઇસ કમાન્ડ ક્લાઉડમાં પ્રોસેસ થઈ રહ્યો છે, સાહેબ..._")
                            text = "User sent a voice memo. Please provide executive status."

                        if text:
                            res_cmd = self.process_command(text, source="telegram")
                            self.send_telegram_message(chat_id, res_cmd["reply"])
                time.sleep(1)
            except Exception:
                time.sleep(4)


# =============================================================================
# FastAPI Application & Embedded Mobile Web Portal
# =============================================================================
app = FastAPI(title="Aradhya 24/7 Cloud Sentinel & Mobile Access")
agent_instance = CloudMobileAgent()


EMBEDDED_HTML_PORTAL = """<!DOCTYPE html>
<html lang="gu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aradhya 24/7 Cloud Sentinel</title>
    <style>
        :root {
            --bg-color: #0d1117;
            --panel-bg: #161b22;
            --cyan-glow: #00e5ff;
            --text-color: #e6edf3;
            --border-color: #30363d;
            --green: #2ea043;
            --yellow: #d29922;
            --red: #f85149;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        header {
            background: var(--panel-bg);
            border-bottom: 1px solid var(--border-color);
            padding: 12px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: bold;
            font-size: 1.1rem;
            color: var(--cyan-glow);
        }
        .reactor-circle {
            width: 14px;
            height: 14px;
            border-radius: 50%;
            background: var(--cyan-glow);
            box-shadow: 0 0 10px var(--cyan-glow);
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
        .status-badge {
            font-size: 0.8rem;
            padding: 4px 10px;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            background: rgba(0, 0, 0, 0.4);
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
        }
        .dot-green { background: var(--green); box-shadow: 0 0 6px var(--green); }
        .dot-yellow { background: var(--yellow); box-shadow: 0 0 6px var(--yellow); }
        #chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .message {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 14px;
            line-height: 1.5;
            font-size: 0.95rem;
            word-wrap: break-word;
        }
        .user-msg {
            align-self: flex-end;
            background: #1f6feb;
            color: white;
            border-bottom-right-radius: 2px;
        }
        .aradhya-msg {
            align-self: flex-start;
            background: var(--panel-bg);
            border: 1px solid var(--border-color);
            border-bottom-left-radius: 2px;
        }
        .quick-chips {
            display: flex;
            gap: 8px;
            padding: 8px 16px;
            overflow-x: auto;
            background: rgba(22, 27, 34, 0.5);
            border-top: 1px solid var(--border-color);
        }
        .chip {
            background: #21262d;
            color: var(--text-color);
            border: 1px solid var(--border-color);
            padding: 6px 12px;
            border-radius: 16px;
            font-size: 0.8rem;
            cursor: pointer;
            white-space: nowrap;
        }
        .chip:hover { border-color: var(--cyan-glow); color: var(--cyan-glow); }
        #input-area {
            background: var(--panel-bg);
            border-top: 1px solid var(--border-color);
            padding: 12px 16px;
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            background: #0d1117;
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 10px 16px;
            color: var(--text-color);
            outline: none;
            font-size: 0.95rem;
        }
        input[type="text"]:focus { border-color: var(--cyan-glow); }
        button {
            background: var(--cyan-glow);
            color: #000;
            border: none;
            border-radius: 20px;
            padding: 10px 20px;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover { opacity: 0.9; }
    </style>
</head>
<body>
    <header>
        <div class="logo">
            <div class="reactor-circle"></div>
            <span>AROHI 24/7 CLOUD SENTINEL</span>
        </div>
        <div id="status-display" class="status-badge">
            <span class="status-dot dot-yellow"></span>
            <span id="status-text">Checking...</span>
        </div>
    </header>

    <div id="chat-container">
        <div class="message aradhya-msg">
            નમસ્તે અલ્પેશ સાહેબ! 🙏<br>
            હું <strong>આરાધ્યા (Aradhya) ૨૪/૭ ક્લાઉડ સેન્ટ્રી</strong> છું. આપનું લેપટોપ બંધ (Off) હોય ત્યારે પણ હું આપના મોબાઇલ ફોન પરથી ઉપલબ્ધ છું. આપ મને કોઈ પણ પ્રશ્ન પૂછી શકો છો અથવા લેપટોપ માટે આદેશ આપી શકો છો.
        </div>
    </div>

    <div class="quick-chips">
        <div class="chip" onclick="sendQuick('લેપટોપ સ્ટેટસ શું છે?')">💻 લેપટોપ સ્ટેટસ</div>
        <div class="chip" onclick="sendQuick('સિક્યુરિટી સ્કેન ચલાવો')">🛡️ સિક્યુરિટી સ્કેન</div>
        <div class="chip" onclick="sendQuick('લેપટોપ સ્પીડ બૂસ્ટ ચલાવો')">🚀 સ્પીડ બૂસ્ટ</div>
        <div class="chip" onclick="sendQuick('/ceo')">👑 બિઝનેસ ઓવરવ્યૂ</div>
    </div>

    <div id="input-area">
        <input type="text" id="user-input" placeholder="આરાધ્યાને આદેશ આપો (ગુજરાતી અથવા English)..." onkeydown="if(event.key==='Enter') sendMessage()">
        <button onclick="sendMessage()">મોકલો</button>
    </div>

    <script>
        async function updateStatus() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                const badge = document.getElementById('status-display');
                const text = document.getElementById('status-text');
                if (data.laptop_online) {
                    badge.innerHTML = '<span class="status-dot dot-green"></span> <span>લેપટોપ: ઓનલાઇન 🟢</span>';
                } else {
                    badge.innerHTML = '<span class="status-dot dot-yellow"></span> <span>લેપટોપ: ઑફ 🌙 (ક્લાઉડ સેન્ટ્રી સક્રિય)</span>';
                }
            } catch(e) {
                console.error(e);
            }
        }
        setInterval(updateStatus, 10000);
        updateStatus();

        async function sendMessage() {
            const input = document.getElementById('user-input');
            const msg = input.value.trim();
            if (!msg) return;
            input.value = '';

            const container = document.getElementById('chat-container');
            container.innerHTML += `<div class="message user-msg">${escapeHtml(msg)}</div>`;
            container.scrollTop = container.scrollHeight;

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: msg})
                });
                const data = await res.json();
                container.innerHTML += `<div class="message aradhya-msg">${formatText(data.reply)}</div>`;
                container.scrollTop = container.scrollHeight;
                updateStatus();
            } catch(e) {
                container.innerHTML += `<div class="message aradhya-msg">Error communicating with Aradhya Cloud Sentinel.</div>`;
            }
        }

        function sendQuick(txt) {
            document.getElementById('user-input').value = txt;
            sendMessage();
        }

        function escapeHtml(t) {
            return t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        }

        function formatText(t) {
            return t.replace(/\\n/g, '<br>').replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
        }
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def serve_mobile_portal():
    """Serves the 24/7 mobile web portal for Aradhya."""
    return HTMLResponse(content=EMBEDDED_HTML_PORTAL)


@app.post("/api/chat")
def handle_chat_endpoint(req: ChatRequest):
    """Chat endpoint used by mobile web portal or external apps."""
    return agent_instance.process_command(req.message, source="web_portal")


@app.post("/api/heartbeat")
def handle_heartbeat_endpoint(req: HeartbeatRequest):
    """Heartbeat endpoint pinged by local laptop daemon."""
    return agent_instance.record_heartbeat(req.model_dump())


@app.get("/api/status")
def handle_status_endpoint():
    """Health check and telemetry endpoint."""
    telem = agent_instance.get_laptop_telemetry()
    return {
        "agent_name": "Aradhya",
        "cloud_sentinel_online": True,
        "laptop_online": telem["is_online"],
        "laptop_status": telem["status_label"],
        "pending_tasks_count": len(agent_instance.get_pending_tasks()),
        "laptop_telemetry": telem["details"]
    }


@app.post("/api/tasks/queue")
def handle_queue_task_endpoint(req: ChatRequest):
    """Manually queue a directive for the physical laptop."""
    task = agent_instance.queue_laptop_task(req.message, source="api")
    return {"status": "queued", "task": task}


@app.get("/api/tasks/pending")
def handle_pending_tasks_endpoint():
    """Endpoint for local laptop to fetch pending tasks queued while it was off."""
    return {"tasks": agent_instance.get_pending_tasks()}


@app.post("/api/tasks/complete")
def handle_complete_task_endpoint(req: TaskCompleteRequest):
    """Endpoint for local laptop to report task completion."""
    success = agent_instance.complete_task(req.task_id, req.result, success=req.success)
    return {"status": "updated", "success": success}


def start_background_threads():
    """Start telegram polling worker in background if token is provided."""
    if agent_instance.bot_token:
        t = threading.Thread(target=agent_instance.run_telegram_polling, daemon=True)
        t.start()


if __name__ == "__main__":
    start_background_threads()
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
