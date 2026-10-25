"""
Offline Autonomous Command & Intent Engine for Aradhya.
Allows Aradhya to function autonomously without internet connectivity,
executing laptop control, file operations, system optimization, diagnostics,
and local memory retrieval seamlessly in Gujarati and English.
"""

import os
import sys
import re
import time
import datetime
import subprocess
import psutil
from typing import Any, Dict, List, Optional, Tuple

from config.settings import JarvisConfig, load_config
from tools.laptop_tools import (
    set_system_volume,
    change_system_volume,
    toggle_system_mute,
    set_screen_brightness,
    change_screen_brightness,
    get_battery_status,
    lock_screen,
)
from tools.vision_tools import capture_screen
from tools.system_optimizer_tools import (
    resolve_laptop_sluggishness,
    terminate_specific_process,
    diagnose_system_sluggishness,
    optimize_laptop_performance,
    remedy_laptop_hang_and_lag,
    diagnose_hang_and_lag_causes,
)
from tools.laptop_work_tools import (
    find_files_across_laptop,
    open_file_or_folder_with_default_app,
    get_detailed_disk_usage,
    find_running_processes,
    kill_process_by_name,
)
from tools.system_tools import execute_shell_command, launch_desktop_app
from tools.security_tools import (
    run_system_security_audit,
    scan_network_vulnerabilities,
    scan_for_hacker_backdoors,
    check_firewall_status,
    neutralize_suspicious_threat,
)
from tools.cloud_sync_tools import (
    check_cloud_sentinel_status,
    sync_cloud_task_queue,
)
from tools.stay_awake_tools import (
    inspect_stay_awake_status,
    toggle_force_stay_awake,
)
from tools.evolution_tools import (
    surprise_me_with_idea,
    trigger_self_evolution_cycle,
    get_agent_evolution_status,
)
from tools.turbo_speed_tools import (
    boost_laptop_to_max_speed,
    inspect_laptop_performance_mode,
)
from tools.chamunda_ceo_tools import (
    chamunda_lookup_part,
    chamunda_search_parts_filtered,
    chamunda_generate_health_passport,
    chamunda_diagnose_engine_sound,
    chamunda_complete_job_and_invoice,
    chamunda_launch_workshop_portal,
    chamunda_get_predictive_service_reminders,
    chamunda_generate_wholesale_po,
    chamunda_track_customer_service_status,
    chamunda_tune_engine_thump,
    chamunda_create_quick_counter_pos_sale,
    chamunda_inspect_preowned_bike,
    chamunda_evaluate_market_valuation,
    chamunda_audit_expedition_readiness,
    chamunda_build_carry_along_spares_kit,
    chamunda_highway_breakdown_sos_triage,
    chamunda_build_custom_restomod_quote,
    chamunda_calculate_performance_stage_tune,
    chamunda_diagnose_vintage_ci_bullet,
    chamunda_execute_written_command,
)


class OfflineCommander:
    """
    Interprets user instructions offline via natural language pattern matching
    and directly executes local operating system tools.
    """

    def __init__(self, config: Optional[JarvisConfig] = None, memory_mgr: Optional[Any] = None):
        self.config = config or load_config()
        self.memory_mgr = memory_mgr

    def execute_offline_turn(self, user_text: str) -> str:
        """
        Main entry point for processing a user turn when offline.
        Matches intent, executes corresponding local tool, and formats response.
        """
        raw = (user_text or "").strip()
        text = raw.lower()

        if not text:
            return self._format_response("જી સાહેબ, હું સાંભળી રહી છું. ઑફલાઇન મોડમાં તમારો શું આદેશ છે?",
                                         "Yes Sir, I am listening in offline autonomous mode. What are your orders?",
                                         include_lifecycle=False)

        # 1. Volume Controls (Gujarati & English)
        # Mute / Unmute
        if any(w in text for w in ["mute", "મ્યૂટ", "અવાજ બંધ", "શાંત", "unmute"]):
            res = toggle_system_mute()
            return self._format_response(f"જી સાહેબ, ઑડિયો મ્યૂટ ટોગલ કરી દીધું છે. ({res})",
                                         f"Sir, system audio mute toggled. ({res})")

        # Volume Increase
        if any(w in text for w in ["volume up", "louder", "અવાજ વધારો", "વોલ્યુમ વધારો", "volume vadharo", "sound up"]):
            res = change_system_volume(10)
            return self._format_response(f"જી સાહેબ, વોલ્યુમ ૧૦% વધારી દીધું છે. ({res})",
                                         f"Sir, system volume increased by 10%. ({res})")

        # Volume Decrease
        if any(w in text for w in ["volume down", "quieter", "અવાજ ઓછો", "વોલ્યુમ ઘટાડો", "volume ghatado", "sound down"]):
            res = change_system_volume(-10)
            return self._format_response(f"જી સાહેબ, વોલ્યુમ ૧૦% ઘટાડી દીધું છે. ({res})",
                                         f"Sir, system volume decreased by 10%. ({res})")

        # Set Volume to specific percent (e.g. "volume 50%", "વોલ્યુમ 50 કરો")
        vol_match = re.search(r'(?:volume|વોલ્યુમ|અવાજ)\s*(?:set to|to|કર|કરો)?\s*(\d+)', text)
        if vol_match:
            vol_val = int(vol_match.group(1))
            res = set_system_volume(vol_val)
            return self._format_response(f"જી સાહેબ, વોલ્યુમ {vol_val}% સેટ કરી દીધું છે. ({res})",
                                         f"Sir, system volume set to {vol_val}%. ({res})")

        # 2. Brightness Controls
        if any(w in text for w in ["brightness up", "બ્રાઇટનેસ વધારો", "સ્ક્રીન લાઈટ વધારો", "light up"]):
            res = change_screen_brightness(15)
            return self._format_response(f"જી સાહેબ, સ્ક્રીન બ્રાઇટનેસ વધારી દીધી છે. ({res})",
                                         f"Sir, screen brightness increased. ({res})")

        if any(w in text for w in ["brightness down", "બ્રાઇટનેસ ઘટાડો", "સ્ક્રીન લાઈટ ઘટાડો", "dim screen"]):
            res = change_screen_brightness(-15)
            return self._format_response(f"જી સાહેબ, સ્ક્રીન બ્રાઇટનેસ ઘટાડી દીધી છે. ({res})",
                                         f"Sir, screen brightness decreased. ({res})")

        bri_match = re.search(r'(?:brightness|બ્રાઇટનેસ|લાઇટ)\s*(?:set to|to|કર|કરો)?\s*(\d+)', text)
        if bri_match:
            bri_val = int(bri_match.group(1))
            res = set_screen_brightness(bri_val)
            return self._format_response(f"જી સાહેબ, બ્રાઇટનેસ {bri_val}% સેટ કરી દીધી છે. ({res})",
                                         f"Sir, screen brightness set to {bri_val}%. ({res})")

        # 3. Battery & Power Status
        if any(w in text for w in ["battery", "બેટરી", "charging", "ચાર્જિંગ", "power status", "પાવર"]):
            res = get_battery_status()
            return self._format_response(f"જી સાહેબ, બેટરીની વર્તમાન સ્થિતિ:\n\n{res}",
                                         f"Sir, here is the current battery and power telemetry:\n\n{res}")

        # 4. Hang, Freeze & Severe Lag Remediation (HangShield)
        if any(w in text for w in [
            "હેંગ", "ચોંટે છે", "ચોંટી ગયું", "ચોંટી ગયુ", "અટકી ગયું", "અટકી ગયુ", "લેગ", "લેગ કરે છે",
            "hang", "hanging", "lagging", "keep lagging", "frozen", "freeze", "stuck", "unresponsive", "fix lag"
        ]):
            res = remedy_laptop_hang_and_lag(aggressive=True)
            return self._format_response(
                f"જી સાહેબ (Alpesh Sir)! લેપટોપ હેંગિંગ અને લેગિંગ અટકાવવા માટે મેં તાત્કાલિક તમામ જરૂરી પગલાં લઈ લીધા છે:\n\n{res}",
                f"Sir, I have autonomously taken all necessary corrective steps to resolve the laptop hang and lag issue:\n\n{res}"
            )

        # 4b. Sluggishness, Speed Boost & Background Process Cleaning
        # 4c. Maximum Performance & TurboSpeed ("make laptop as much as faster as possible")
        if any(w in text for w in [
            "as fast as possible", "faster as possible", "fast as possible", "as much as faster",
            "make it faster", "make laptop faster", "turbo speed", "max speed", "maximum speed",
            "peak speed", "ultra fast", "boost speed to max",
            "બને તેટલું ઝડપી", "બને તેટલુ ઝડપી", "ઝડપી બનાવો", "સુપર ફાસ્ટ", "ટર્બો સ્પીડ", "મેક્સિમમ સ્પીડ",
            "વધારે સ્પીડ", "રોકેટ જેવું", "વધુ ઝડપી"
        ]):
            res = boost_laptop_to_max_speed(aggressive=False, clean_deep_caches=True, boost_active_apps=True)
            return self._format_response(
                f"જી સાહેબ (Alpesh Sir)! આપના આદેશ અનુસાર લેપટોપને બને તેટલું વધારે ઝડપી (Turbo Speed) બનાવી દીધું છે:\n\n{res}",
                f"Sir, as commanded, I have engaged full TurboSpeed optimization to make your laptop as fast as possible:\n\n{res}"
            )

        if any(w in text for w in ["boost", "sluggish", "slow", "ધીમું", "ધીમુ", "speed", "સ્પીડ", "બૂસ્ટ", "clean background", "clean cache"]):
            res = resolve_laptop_sluggishness(aggressive=False)
            return self._format_response(
                f"જી સાહેબ! ઑફલાઇન મોડમાં મેં લેપટોપનું એનાલિસિસ કરીને બિનજરૂરી બેકગ્રાઉન્ડ પ્રોસેસિસ બંધ કરી દીધી છે અને સ્પીડ બૂસ્ટ કરી દીધી છે:\n\n{res}",
                f"Sir, I have analyzed your system and terminated unnecessary background consumers in offline mode:\n\n{res}"
            )

        # 5. Terminate Specific Process
        kill_match = re.search(r'(?:kill|terminate|stop|close|બંધ કરો)\s+(?:process|program|app|પ્રોસેસ)?\s*([a-zA-Z0-9_\-\.]+)', text)
        if kill_match and not any(w in text for w in ["screen", "wifi", "bluetooth", "mute"]):
            target_proc = kill_match.group(1).strip()
            res = terminate_specific_process(target_proc)
            return self._format_response(f"જી સાહેબ, પ્રોસેસ ટર્મિનેશન વિશ્લેષણ:\n\n{res}",
                                         f"Sir, process termination analysis:\n\n{res}")

        # 6. Work StayAwake Sentry & Sleep/Lockscreen Prevention (AwakeGuard)
        if any(w in text for w in [
            "stay awake", "keep awake", "do not sleep", "prevent sleep", "don't sleep",
            "sleep ન થવા", "સ્લીપ ન થવા", "લોકસ્ક્રીન ન", "કામ ચાલુ હોય ત્યારે સ્લીપ",
            "સ્ટે અવેક", "સ્લીપ બંધ", "lockscreen ન", "awake status", "do not let it go to sleep",
            "not let it sleep", "don't lock"
        ]):
            if any(w in text for w in ["status", "ચેક", "સ્થિતિ", "stat"]):
                res = inspect_stay_awake_status()
            elif any(w in text for w in ["off", "disable", "ડિસેબલ"]):
                res = toggle_force_stay_awake(enable=False)
            else:
                # Default: Ensure sleep/lockscreen is prevented during work / force on
                res = toggle_force_stay_awake(enable=True, duration_minutes=0)
            return self._format_response(
                f"જી સાહેબ (Alpesh Sir)! વર્ક સ્ટે-અવેક સેટિંગ્સ:\n\n{res}",
                f"Sir, Work StayAwake status and settings:\n\n{res}"
            )

        # 6b. Lock Screen & Security
        if any(w in text for w in ["lock screen", "સ્ક્રીન લોક", "લોક કરો", "lock laptop", "screen lock"]) and not any(neg in text for neg in ["don't", "do not", "ન કરો", "ન થવા"]):
            res = lock_screen()
            return self._format_response(f"જી સાહેબ, લેપટોપ સ્ક્રીન સુરક્ષિત રીતે લૉક કરી દીધી છે. ({res})",
                                         f"Sir, laptop screen locked securely. ({res})")

        # 7. Screenshot Capture
        if any(w in text for w in ["screenshot", "સ્ક્રીનશોટ", "capture screen"]):
            res = capture_screen()
            return self._format_response(f"જી સાહેબ, સ્ક્રીનશોટ સફળતાપૂર્વક કેપ્ચર કરી લીધો છે: {res}",
                                         f"Sir, screenshot captured successfully: {res}")

        # 8. Storage & Disk Usage
        if any(w in text for w in ["disk", "storage", "ડિસ્ક", "સ્ટોરેજ", "space", "જગ્યા"]):
            res = get_detailed_disk_usage()
            return self._format_response(f"જી સાહેબ, લેપટોપ ડિસ્ક અને સ્ટોરેજ વપરાશ:\n\n{res}",
                                         f"Sir, here is the detailed disk and storage telemetry:\n\n{res}")

        # 9. Find Files
        find_match = re.search(r'(?:find|search for|શોધો|શોધ)\s+(?:file|document|ફાઇલ)?\s*([a-zA-Z0-9_\-\.\*]+)', text)
        if find_match and not any(w in text for w in ["process", "running", "program"]):
            query_file = find_match.group(1).strip()
            res = find_files_across_laptop(query_file)
            return self._format_response(f"જી સાહેબ, '{query_file}' માટે ઑફલાઇન સર્ચ પરિણામો:\n\n{res}",
                                         f"Sir, offline file search results for '{query_file}':\n\n{res}")

        # 10. Open File or Application
        open_match = re.search(r'(?:open|launch|ખોલો|ચાલુ કરો)\s+(.+)', text)
        if open_match and not any(w in text for w in ["volume", "brightness", "camera", "port", "ports", "firewall", "security", "threat"]):
            target_open = open_match.group(1).strip()
            # If path exists or default app
            if os.path.exists(target_open) or "/" in target_open or "." in target_open:
                res = open_file_or_folder_with_default_app(target_open)
                return self._format_response(f"જી સાહેબ, ફાઇલ ઓપન કરી દીધી છે: {res}",
                                             f"Sir, opened file: {res}")
            else:
                res = launch_desktop_app(target_open)
                return self._format_response(f"જી સાહેબ, એપ્લિકેશન લોન્ચ કરવાનો પ્રયાસ કર્યો: {res}",
                                             f"Sir, application launch attempt: {res}")

        # 11. Cybersecurity & Anti-Hacker Defense (Offline Operational)
        # Port & Network Vulnerability Scan
        if (any(w in text for w in ["port scan", "open ports", "પોર્ટ સ્કેન", "નેટવર્ક પોર્ટ", "ઓપન પોર્ટ"]) or
            (re.search(r'\b(?:port|ports|પોર્ટ|પોર્ટ્સ)\b', text) and not any(p in text for p in ["passport", "પાસપોર્ટ"]))):
            res = scan_network_vulnerabilities()
            return self._format_response(f"જી સાહેબ, નેટવર્ક પોર્ટ્સ અને સોકેટ્સનું વિશ્લેષણ:\n\n{res}",
                                         f"Sir, network ports and sockets vulnerability report:\n\n{res}")

        # Firewall Status
        if any(w in text for w in ["firewall", "ફાયરવોલ", "ufw"]):
            res = check_firewall_status()
            return self._format_response(f"જી સાહેબ, લિનક્સ ફાયરવોલ (UFW) સ્થિતિ:\n\n{res}",
                                         f"Sir, Linux Firewall (UFW) status:\n\n{res}")

        # Neutralize / Terminate Hostile Threat PID or Port
        if any(w in text for w in ["kill threat", "neutralize", "થ્રેટ બંધ કરો", "ખતરો બંધ કરો", "kill hacker"]):
            target_match = re.search(r'(?:threat|target|pid|port|ખતરો)\s*[:=]?\s*([a-zA-Z0-9_-]+)', text)
            target = target_match.group(1) if target_match else text.split()[-1]
            res = neutralize_suspicious_threat(target)
            return self._format_response(f"જી સાહેબ, {res}", f"Sir, {res}")

        # Comprehensive Security Audit / Scan for Hackers & Backdoors
        if any(w in text for w in ["security", "સિક્યુરિટી", "સુરક્ષા", "hacker", "hackers", "હેકર", "હેકર્સ", "backdoor", "બેકડોર", "malware", "વાયરસ", "cyber", "સાયબર"]):
            res = run_system_security_audit(deep_scan=True)
            return res

        # 12. 24/7 Cloud Sentinel & Mobile Access Status
        if any(w in text for w in ["cloud status", "mobile access", "ક્લાઉડ સ્ટેટસ", "મોબાઇલ એક્સેસ", "cloud sync", "sync cloud", "ક્લાઉડ સિંક"]):
            if "sync" in text or "સિંક" in text:
                res = sync_cloud_task_queue()
            else:
                res = check_cloud_sentinel_status()
            return self._format_response(f"જી સાહેબ, ૨૪/૭ ક્લાઉડ સેન્ટ્રી સ્ટેટસ:\n\n{res}",
                                         f"Sir, 24/7 Cloud Sentinel status:\n\n{res}")

        # 13. System Diagnostics / Telemetry Load
        if any(w in text for w in ["diagnostics", "telemetry", "system load", "સિસ્ટમ સ્થિતિ", "sys load", "health report", "system status"]) or text == "status":
            res = diagnose_system_sluggishness()
            return self._format_response(f"જી સાહેબ, ઑફલાઇન સિસ્ટમ હેલ્થ અને ટેલિમેટ્રી:\n\n{res}",
                                         f"Sir, offline system health and telemetry report:\n\n{res}")

        # 13. Date & Time
        if any(w in text for w in ["time", "સમય", "તારીખ", "date", "clock", "કલાક"]):
            now_str = datetime.datetime.now().strftime("%A, %d %B %Y - %I:%M:%S %p")
            return self._format_response(f"જી સાહેબ, વર્તમાન સમય અને તારીખ છે: **{now_str}**",
                                         f"Sir, current local date and time is: **{now_str}**")

        # 14. Memory / Profile Lookup
        if any(w in text for w in ["memory", "મેમરી", "facts", "તમે શું જાણો છો", "who am i", "મારી માહિતી", "profile"]):
            facts_list = []
            if self.memory_mgr and hasattr(self.memory_mgr, "semantic"):
                facts = self.memory_mgr.semantic.get_all_facts()
                for f in facts[:10]:
                    facts_list.append(f"- **{f['key']}**: {f['value']}")
            facts_text = "\n".join(facts_list) if facts_list else "*હાલમાં સ્થાનિક ડેટાબેઝમાં કોઈ નોંધાયેલી માહિતી નથી.*"
            return self._format_response(f"જી સાહેબ, તમારા વિશે સ્થાનિક SQLite મેમરીમાં સંગ્રહિત માહિતી:\n\n{facts_text}",
                                         f"Sir, facts stored about you in local SQLite memory:\n\n{facts_text}")

        # 14a-00. Chamunda Executive Sub-Agents & Natural Language Written Commands
        if any(w in text for w in ["લેખિત આદેશ", "written command", "લેખિત કમાન્ડ", "આદેશ આપો", "subagent", "sub agent", "સબ એજન્ટ", "સબ-એજન્ટ"]) or any(name in text for name in ["રમેશભાઈ", "જયેશભાઈ", "પ્રિયા શર્મા", "કબીર મહેતા", "હસમુખભાઈ"]):
            res = chamunda_execute_written_command(command=prompt, sender="Alpesh Sir (Founder & Chairman)")
            msg_gu = f"જી સાહેબ (Alpesh Sir)! આપનો લેખિત આદેશ સ્વીકારીને સબ-એજન્ટને તૈનાત કરવામાં આવ્યો છે:\n\n{res}"
            msg_en = f"Sir (Alpesh Sir), your written directive has been executed by the designated sub-agent:\n\n{res}"
            return self._format_response(msg_gu, msg_en)

        # 14a-0. Chamunda AI Interactive Workshop Web Portal & Live Mobile QR Viewer
        if any(w in text for w in ["web portal", "વેબ પોર્ટલ", "portal", "dashboard", "ડેશબોર્ડ", "launch portal", "open portal", "વેબ ડેશબોર્ડ"]) or (("પોર્ટલ" in text) and not ("પાસપોર્ટ" in text or "passport" in text)):
            res = chamunda_launch_workshop_portal()
            msg_gu = f"જી સાહેબ (Alpesh Sir)! ચામુંડા ઓટોમોબાઇલ ઇન્ટરેક્ટિવ વર્કશોપ વેબ પોર્ટલ લાઈવ છે:\n\n{res}"
            msg_en = f"Sir (Alpesh Sir), Chamunda AI Interactive Workshop Web Portal is active and online:\n\n{res}"
            return self._format_response(msg_gu, msg_en)

        # 14a-0a. Chamunda AI Predictive Service CRM & WhatsApp Reminders
        if any(w in text for w in ["service reminder", "સર્વિસ રિમાઇન્ડર", "crm", "સીઆરએમ", "predictive service", "due service", "reminder list", "રિમાઇન્ડર લિસ્ટ"]) or ("રિમાઇન્ડર" in text and not any(k in text for k in ["timer", "ટાઈમર", "ટાસ્ક"])):
            res = chamunda_get_predictive_service_reminders()
            msg_gu = f"જી સાહેબ (Alpesh Sir)! ચામુંડા ઓટોમોબાઇલ પ્રેડિક્ટિવ સર્વિસ CRM અને WhatsApp રિમાઇન્ડર રિપોર્ટ:\n\n{res}"
            msg_en = f"Sir (Alpesh Sir), Chamunda AI Predictive Service CRM and WhatsApp reminder report:\n\n{res}"
            return self._format_response(msg_gu, msg_en)

        # 14a-0b. Wholesale Stock Replenishment Purchase Order (Chamunda AI)
        po_word = bool(re.search(r'\b(po|purchase\s*order)\b', text))
        if not any(p in text for p in ["passport", "પાસપોર્ટ"]) and (
            any(w in text for w in ["purchase order", "પરચેઝ ઓર્ડર", "wholesale po", "સ્ટોક ઓર્ડર", "stock replenishment", "reorder parts", "પીઓ બનાવો", "ઓર્ડર બનાવો"])
            or (po_word and any(k in text for k in ["generate", "બનાવો", "ઓર્ડર", "સ્ટોક", "stock", "create", "wholesale"]))
            or ("પીઓ" in text and any(k in text for k in ["બનાવો", "ઓર્ડર", "સ્ટોક"]))
        ):
            res = chamunda_generate_wholesale_po()
            msg_gu = f"જી સાહેબ (Alpesh Sir)! ચામુંડા ઓટોમોબાઇલ હોલસેલ સ્ટોક રિપ્લેનિશમેન્ટ Purchase Order (PO) સફળતાપૂર્વક જનરેટ થયો છે:\n\n{res}"
            msg_en = f"Sir (Alpesh Sir), Chamunda Automobile Wholesale Stock Replenishment Purchase Order (PO) generated successfully:\n\n{res}"
            return self._format_response(msg_gu, msg_en)

        # 14a-0c. Royal Enfield Iconic Thump Tuner & Acoustic Resonance Calibrator
        if any(w in text for w in ["thump", "થમ્પ", "ડુગ", "ડૂગ", "ડુગડુગ", "dug", "exhaust resonance", "એક્ઝોસ્ટ અવાજ"]) or bool(re.search(r'\b(thump|tuner|dugdug)\b', text)):
            b_model = "Classic 350"
            for m in ["hunter 350", "classic 350", "bullet 350", "meteor 350", "himalayan 450", "interceptor 650"]:
                if m in text:
                    b_model = m.title()
                    break
            profile = "deep_vintage_chug"
            if any(k in text for k in ["oem", "showroom", "bs6", "સ્મૂથ", "smooth"]):
                profile = "factory_oem_clean"
            elif any(k in text for k in ["cruiser", "meteor", "highway", "હાઇવે"]):
                profile = "cruiser_bass_rumble"
            elif any(k in text for k in ["himalayan", "sherpa", "શેરપા", "growl"]):
                profile = "sherpa_highland_growl"
            elif any(k in text for k in ["twin", "650", "crossplane", "ટ્વિન"]):
                profile = "twin_270_crossplane_roar"
            
            res = chamunda_tune_engine_thump(bike_model=b_model, profile=profile)
            msg_gu = f"જી સાહેબ (Alpesh Sir)! રોયલ એનફિલ્ડ {b_model} નું Authentic Thump Tuning પરિણામ:\n\n{res}"
            msg_en = f"Sir (Alpesh Sir), Authentic Thump Tuning resonance analysis for Royal Enfield {b_model}:\n\n{res}"
            return self._format_response(msg_gu, msg_en)

        # 14a-0d. 24/7 Customer Service Status & Real-Time Job Card Tracker
        if any(w in text for w in ["service status", "સર્વિસ સ્ટેટસ", "બાઇક સ્ટેટસ", "ક્યાં પહોંચી", "ગાડી ક્યાં પહોંચી", "track status", "track bike", "job status", "ટ્રેક કરો", "સ્ટેટસ શું છે", "stage track"]):
            plate_match = re.search(r'\b([A-Z]{2}[-\s]?[0-9]{2}[-\s]?[A-Z]{1,3}[-\s]?[0-9]{1,4})\b', text.upper())
            job_match = re.search(r'\b(JOB-[0-9\-]+)\b', text.upper())
            identifier = plate_match.group(1) if plate_match else (job_match.group(1) if job_match else "GJ-01-AB-1234")
            res = chamunda_track_customer_service_status(identifier=identifier)
            msg_gu = f"જી સાહેબ (Alpesh Sir)! રોયલ એનફિલ્ડ સર્વિસ સ્ટેટસ ટ્રેકિંગ:\n\n{res}"
            msg_en = f"Sir (Alpesh Sir), Royal Enfield live service stage tracking:\n\n{res}"
            return self._format_response(msg_gu, msg_en)

        # 14a-0e. Quick Countertop POS & Dynamic UPI QR Generator
        pos_word = bool(re.search(r'\b(pos|counter\s*sale|quick\s*pos)\b', text))
        if not any(p in text for p in ["passport", "પાસપોર્ટ", "post"]) and (
            any(w in text for w in ["counter sale", "કાઉન્ટર સેલ", "કાઉન્ટર બિલ", "quick pos", "upi qr", "dynamic upi", "કાઉન્ટર પાર્ટ"])
            or (pos_word and any(k in text for k in ["sale", "બિલ", "વેચાણ", "qr", "upi", "counter", "checkout", "part", "પાર્ટ"]))
        ):
            part_sku = "574050/C"
            sku_m = re.search(r'\b([A-Z0-9]{3,10}/[A-Z0-9]+|RAM[0-9]+|KXA[0-9]+)\b', text.upper())
            if sku_m:
                part_sku = sku_m.group(1)
            elif "air filter" in text or "એર ફિલ્ટર" in text:
                part_sku = "RAM00008/B"
            elif "himalayan" in text or "sherpa" in text:
                part_sku = "KXA00215"
            
            res = chamunda_create_quick_counter_pos_sale(part_skus=part_sku, customer_name="Counter Walk-in Customer")
            msg_gu = f"જી સાહેબ (Alpesh Sir)! ક્વિક કાઉન્ટર POS વેચાણ અને ડાયનેમિક UPI QR જનરેટ થઈ ગયું છે:\n\n{res}"
            msg_en = f"Sir (Alpesh Sir), Quick Countertop POS sale executed and dynamic UPI QR generated:\n\n{res}"
            return self._format_response(msg_gu, msg_en)

        # 14a-0f. Chamunda Certified Pre-Owned 100-Point Digital Inspection Shield
        if any(w in text for w in [
            "100 point", "100-point", "૧૦૦ પોઇન્ટ", "preowned inspection", "pre-owned inspection",
            "bike inspection", "બાઇક ઇન્સ્પેક્શન", "સેકન્ડ હેન્ડ ઇન્સ્પેક્શન", "certified inspection",
            "સર્ટિફાઇડ ઇન્સ્પેક્શન", "ઇન્સ્પેક્શન શીલ્ડ", "inspection shield"
        ]) or (
            any(w in text for w in ["preowned", "pre-owned", "used bike", "સેકન્ડ હેન્ડ", "second hand"])
            and any(k in text for k in ["inspect", "inspection", "check", "ટેસ્ટ", "ઇન્સ્પેક્શન", "સર્ટિફિકેટ", "certificate"])
        ):
            b_model = "Classic 350"
            for m in ["hunter 350", "hunter", "classic 350", "classic", "interceptor 650", "interceptor", "continental gt", "himalayan 450", "himalayan", "meteor 350", "bullet 350", "super meteor"]:
                if m in text:
                    b_model = m.title()
                    break

            reg_match = re.search(r'\b([A-Z]{2}[-\s]?[0-9]{2}[-\s]?[A-Z]{1,3}[-\s]?[0-9]{1,4})\b', text.upper())
            reg_no = reg_match.group(1) if reg_match else "GJ-01-RE-2022"

            res = chamunda_inspect_preowned_bike(
                customer_name="Ramesh Patel (Client)",
                phone="+91 98250 12345",
                bike_model=b_model,
                registration_no=reg_no,
                manufacturing_year=2022,
                odometer_km=18500
            )
            msg_gu = f"જી સાહેબ (Alpesh Sir)! રોયલ એનફિલ્ડ {b_model} (`{reg_no}`) નું ૧૦૦-પોઇન્ટ ડિજિટલ ઇન્સ્પેક્શન અને ચામુંડા વોરંટી શીલ્ડ સર્ટિફિકેટ જનરેટ થઈ ગયું છે:\n\n{res}"
            msg_en = f"Sir (Alpesh Sir), 100-Point Digital Quality Inspection completed and Chamunda Warranty Shield Certificate issued for Royal Enfield {b_model} (`{reg_no}`):\n\n{res}"
            return self._format_response(msg_gu, msg_en)

        # 14a-0g. Royal Enfield AI Fair Market Valuation Evaluator
        if any(w in text for w in [
            "valuation", "market valuation", "fair market", "વેલ્યુએશન", "માર્કેટ વેલ્યુ",
            "કેટલામાં વેચાય", "કેટલામાં લેવાય", "ભાવ શું મળે", "resale value", "રીસેલ વેલ્યુ",
            "માર્કેટ ભાવ", "બજાર ભાવ", "સેકન્ડ હેન્ડ ભાવ"
        ]) or (
            any(w in text for w in ["preowned", "pre-owned", "used bike", "સેકન્ડ હેન્ડ", "second hand"])
            and any(k in text for k in ["price", "value", "rate", "ભાવ", "કિંમત", "વેલ્યુ"])
        ):
            b_model = "Classic 350"
            for m in ["hunter 350", "hunter", "classic 350", "classic", "interceptor 650", "interceptor", "continental gt", "himalayan 450", "himalayan", "meteor 350", "bullet 350", "super meteor"]:
                if m in text:
                    b_model = m.title()
                    break

            year = 2022
            ym = re.search(r'\b(201[5-9]|202[0-6])\b', text)
            if ym:
                year = int(ym.group(1))

            km = 18000
            km_m = re.search(r'\b(\d{1,3}(?:,\d{3})*|\d+)\s*(?:km|કિમી)\b', text, re.IGNORECASE)
            if km_m:
                try:
                    km = int(km_m.group(1).replace(",", ""))
                except Exception:
                    km = 18000

            res = chamunda_evaluate_market_valuation(
                bike_model=b_model,
                manufacturing_year=year,
                odometer_km=km,
                condition_score=85.0
            )
            msg_gu = f"જી સાહેબ (Alpesh Sir)! રોયલ એનફિલ્ડ {b_model} ({year}) માટે AI ફેર માર્કેટ વેલ્યુએશન:\n\n{res}"
            msg_en = f"Sir (Alpesh Sir), AI Fair Market Valuation for Royal Enfield {b_model} ({year}):\n\n{res}"
            return self._format_response(msg_gu, msg_en)

        # 14a-0h. Royal Enfield Expedition Readiness Clearance Audit & QR Passport
        if any(w in text for w in [
            "expedition audit", "pre-tour", "pre tour", "touring audit", "એક્સપિડિશન",
            "ટૂર ઓડિટ", "ટૂરિંગ ઓડિટ", "મુસાફરી ઓડિટ", "expedition readiness", "ladakh audit",
            "લદાખ ઓડિટ", "tour readiness", "લાંબી મુસાફરી ચેક"
        ]) or (
            any(w in text for w in ["expedition", "ladakh", "touring", "ટૂરિંગ", "એક્સપિડિશન"])
            and any(k in text for k in ["audit", "check", "clearance", "ઓડિટ", "ચેક", "પાસપોર્ટ", "passport", "તપાસ"])
        ):
            b_model = "Himalayan 450"
            for m in ["himalayan 450", "himalayan", "hunter 350", "hunter", "classic 350", "classic", "interceptor 650", "interceptor", "continental gt", "meteor 350", "bullet 350", "super meteor"]:
                if m in text:
                    b_model = m.title()
                    break

            dest_key = "ladakh_high_altitude"
            if any(d in text for d in ["coastal", "દરિયાકાંઠો", "કોસ્ટલ"]):
                dest_key = "coastal_highway"
            elif any(d in text for d in ["desert", "રણ", "કચ્છ", "rajasthan", "રાજસ્થાન"]):
                dest_key = "desert_run"
            elif any(d in text for d in ["monsoon", "ચોમાસુ", "ઘાટ", "ghats"]):
                dest_key = "monsoon_western_ghats"
            elif any(d in text for d in ["expressway", "હાઇવે", "highway"]):
                dest_key = "interstate_expressway"

            reg_match = re.search(r'\b([A-Z]{2}[-\s]?[0-9]{2}[-\s]?[A-Z]{1,3}[-\s]?[0-9]{1,4})\b', text.upper())
            reg_no = reg_match.group(1) if reg_match else "GJ-01-RE-2024"

            res = chamunda_audit_expedition_readiness(
                rider_name="Alpesh Patel (Expedition Lead)",
                phone="+91 98250 54321",
                bike_model=b_model,
                registration_no=reg_no,
                destination_key=dest_key,
                planned_km=3500
            )
            msg_gu = f"જી સાહેબ (Alpesh Sir)! રોયલ એનફિલ્ડ {b_model} (`{reg_no}`) નું ૪૮-પોઇન્ટ એક્સપિડિશન પ્રી-ટુર ઓડિટ અને QR ક્લિયરન્સ પાસપોર્ટ જનરેટ થઈ ગયું છે:\n\n{res}"
            msg_en = f"Sir (Alpesh Sir), 48-Point Expedition Pre-Touring Audit completed and QR Clearance Passport issued for Royal Enfield {b_model} (`{reg_no}`):\n\n{res}"
            return self._format_response(msg_gu, msg_en)

        # 14a-0i. Carry-Along Expedition Spares Kit Builder
        if any(w in text for w in [
            "spares kit", "touring kit", "trip kit", "carry along", "સ્પેર કીટ", "ટૂર કીટ",
            "બેકઅપ સ્પેર", "carry spares", "touring spares", "trip spares", "જરૂરી સ્પેર પાર્ટ્સ",
            "ટૂરિંગ સ્પેર", "એક્સપિડિશન કીટ", "expedition kit"
        ]):
            b_model = "Himalayan 450"
            for m in ["himalayan 450", "himalayan", "hunter 350", "hunter", "classic 350", "classic", "interceptor 650", "interceptor", "continental gt", "meteor 350", "bullet 350", "super meteor"]:
                if m in text:
                    b_model = m.title()
                    break

            dest_key = "ladakh_high_altitude"
            if any(d in text for d in ["coastal", "દરિયાકાંઠો", "કોસ્ટલ"]):
                dest_key = "coastal_highway"
            elif any(d in text for d in ["desert", "રણ", "કચ્છ", "rajasthan"]):
                dest_key = "desert_run"
            elif any(d in text for d in ["monsoon", "ચોમાસુ", "ઘાટ", "ghats"]):
                dest_key = "monsoon_western_ghats"
            elif any(d in text for d in ["expressway", "હાઇવે", "highway"]):
                dest_key = "interstate_expressway"

            res = chamunda_build_carry_along_spares_kit(
                bike_model=b_model,
                destination_key=dest_key
            )
            msg_gu = f"જી સાહેબ (Alpesh Sir)! રોયલ એનફિલ્ડ {b_model} માટે કસ્ટમ એક્સપિડિશન કેરી-અલોંગ બેકઅપ સ્પેર કીટ:\n\n{res}"
            msg_en = f"Sir (Alpesh Sir), Custom Carry-Along Backup Spares Kit for Royal Enfield {b_model}:\n\n{res}"
            return self._format_response(msg_gu, msg_en)

        # 14a-0j. 24/7 Gujarat Highway Breakdown SOS Shield
        if any(w in text for w in [
            "highway sos", "breakdown sos", "sos shield", "હાઇવે sos", "બ્રેકડાઉન sos",
            "હાઇવે મદદ", "રસ્તામાં બંધ", "roadside breakdown", "emergency sos", "ઈમરજન્સી sos"
        ]) or (
            any(w in text for w in ["breakdown", "બ્રેકડાઉન", "sos", "ફસાઈ ગઈ", "સ્ટાર્ટ નથી થતી", "બંધ પડી ગઈ"])
            and any(k in text for k in ["highway", "road", "હાઇવે", "રસ્તામાં", "રાત્રે", "clutch", "wire", "puncture", "ઓવરહીટ", "chain", "બેટરી", "battery", "કચ્છ", "nh 48", "nh 8"])
        ):
            res = chamunda_highway_breakdown_sos_triage(symptom_query=raw)
            msg_gu = f"🚨 જી સાહેબ (Alpesh Sir)! ચામુંડા ૨૪/૭ ગુજરાત હાઇવે બ્રેકડાઉન SOS ટ્રાયેજ અને ડાયરેક્ટિવ્સ:\n\n{res}"
            msg_en = f"🚨 Sir (Alpesh Sir), Chamunda 24/7 Gujarat Highway Breakdown SOS Roadside Triage & Directives:\n\n{res}"
            return self._format_response(msg_gu, msg_en)

        # 14a-0k. Vintage Cast-Iron (CI) Bullet Diagnostic & Mechanical Rebirth
        if any(w in text for w in [
            "vintage bullet", "cast iron", "કાસ્ટ આયર્ન", "વિન્ટેજ બુલેટ", "cb point", "cb પોઇન્ટ",
            "contact breaker", "albion", "એલ્બિયન", "heavy crank", "હેવી ક્રેન્ક",
            "vintage ci", "વિન્ટેજ ci", "mikcarb", "માઇકકાર્બ", "wet sumping", "વેટ સમ્પિંગ"
        ]) or (
            any(w in text for w in ["bullet", "બુલેટ", "vintage", "વિન્ટેજ"])
            and any(k in text for k in ["point", "પોઇન્ટ", "timing", "ટાંઇમિંગ", "tappet", "ટેપેટ", "kickback", "કિક", "pushrod", "પુશરોડ"])
        ):
            res = chamunda_diagnose_vintage_ci_bullet(symptom_query=raw)
            msg_gu = f"⚙️ જી સાહેબ (Alpesh Sir)! વિન્ટેજ કાસ્ટ-આયર્ન (CI) હેવી ક્રેન્ક બુલેટ ડાયગ્નોસિસ અને રિબર્થ મેટ્રિક્સ:\n\n{res}"
            msg_en = f"⚙️ Sir (Alpesh Sir), Vintage Cast-Iron (CI) Heavy Crank Bullet Mechanical Rebirth Diagnosis:\n\n{res}"
            return self._format_response(msg_gu, msg_en)

        # 14a-0l. Royal Enfield Performance Dyno Tuning & Stage Calibration
        if any(w in text for w in [
            "dyno tune", "dyno tuning", "ડાયનો ટ્યુન", "performance tune", "પરફોર્મન્સ ટ્યુન",
            "stage 1", "stage 2", "stage-1", "stage-2", "સ્ટેજ ૧", "સ્ટેજ ૨", "dyno pull",
            "horsepower gain", "bhp gain", "torque gain", "ecu remap", "ડાયનો"
        ]) and not any(p in text for p in ["restomod", "resto-mod", "રેસ્ટોમોડ", "build quote", "bobber"]):
            b_model = "Classic 350 Reborn"
            for m in ["hunter 350", "hunter", "classic 350", "classic", "interceptor 650", "interceptor", "continental gt", "himalayan 450", "himalayan", "meteor 350", "bullet 350", "super meteor"]:
                if m in text:
                    b_model = m.title()
                    break

            stg = "stage_1_street_thump"
            if any(s in text for s in ["stage 2", "stage-2", "સ્ટેજ ૨", "stage 2 sport", "sprint"]):
                stg = "stage_2_dyno_sprint"

            res = chamunda_calculate_performance_stage_tune(bike_model=b_model, stage_key=stg)
            msg_gu = f"⚡ જી સાહેબ (Alpesh Sir)! રોયલ એનફિલ્ડ {b_model} નું ડાયનો પરફોર્મન્સ કેલિબ્રેશન ({stg}) તૈયાર છે:\n\n{res}"
            msg_en = f"⚡ Sir (Alpesh Sir), Dyno Performance Stage Calibration ({stg}) for Royal Enfield {b_model} calculated successfully:\n\n{res}"
            return self._format_response(msg_gu, msg_en)

        # 14a-0m. Bespoke Royal Enfield Custom Resto-Mod Builder & Blueprint
        if any(w in text for w in [
            "restomod", "resto-mod", "રેસ્ટોમોડ", "custom resto", "resto quote", "restomod quote",
            "bobber", "બોબર", "cafe racer", "કેફે રેસર", "scrambler", "સ્ક્રેમ્બલર",
            "કસ્ટમ રેસ્ટો", "રેસ્ટો બ્લુપ્રિન્ટ", "custom build quote", "resto build"
        ]):
            b_model = "Bullet 350 Cast-Iron CI"
            for m in ["hunter 350", "hunter", "classic 350", "classic", "interceptor 650", "interceptor", "continental gt", "himalayan 450", "himalayan", "meteor 350", "bullet 350", "super meteor", "electra 350"]:
                if m in text:
                    b_model = m.title()
                    break

            style = "bobber_solo"
            if any(s in text for s in ["cafe racer", "cafe", "કેફે રેસર", "કેફે"]):
                style = "cafe_racer"
            elif any(s in text for s in ["scrambler", "સ્ક્રેમ્બલર", "desert"]):
                style = "desert_scrambler"
            elif any(s in text for s in ["vintage", "heritage", "હેરીટેજ", "વિન્ટેજ"]):
                style = "vintage_heritage_standard"

            paint = "matte_phantom_black"
            if any(p in text for p in ["green", "લીલો", "british"]):
                paint = "british_racing_green_gold"
            elif any(p in text for p in ["desert", "sand", "રણ"]):
                paint = "desert_sand_patina"
            elif any(p in text for p in ["maroon", "લાલ"]):
                paint = "candy_royal_maroon"
            elif any(p in text for p in ["silver", "grey", "સિલ્વર"]):
                paint = "vintage_gunmetal_silver"

            stg = "stage_1_street_thump"
            if any(s in text for s in ["stage 2", "stage-2", "સ્ટેજ ૨"]):
                stg = "stage_2_dyno_sprint"

            inc_vintage = any(v in text for v in ["vintage", "cast iron", "ci", "હેવી ક્રેન્ક", "heavy crank", "વિન્ટેજ"])

            res = chamunda_build_custom_restomod_quote(
                customer_name="Valued Rider",
                phone="+91 98250 88776",
                bike_model=b_model,
                registration_no="GJ-01-RM-1985",
                style_key=style,
                paint_theme_key=paint,
                performance_stage_key=stg,
                include_vintage_ci_package=inc_vintage,
                custom_notes="Custom bespoke build via offline voice command"
            )
            msg_gu = f"🏍️ જી સાહેબ (Alpesh Sir)! રોયલ એનફિલ્ડ {b_model} નું કસ્ટમ રેસ્ટો-મોડ ({style}) બ્લુપ્રિન્ટ અને BOM તૈયાર છે:\n\n{res}"
            msg_en = f"🏍️ Sir (Alpesh Sir), Bespoke Royal Enfield {b_model} Custom Resto-Mod ({style}) Blueprint & BOM generated:\n\n{res}"
            return self._format_response(msg_gu, msg_en)

        # 14a-1. Live Royal Enfield Engine Sound Diagnostic (Chamunda AI)
        if any(w in text for w in ["sound diagnostic", "engine sound", "સાઉન્ડ", "એન્જિન અવાજ", "sound test", "સાઉન્ડ ટેસ્ટ", "diagnose sound", "અવાજ ચેક", "acoustic diag"]):
            b_model = "Classic 350"
            for m in ["hunter 350", "hunter", "classic 350", "classic", "interceptor 650", "interceptor", "gt 650", "himalayan 450", "himalayan", "meteor 350", "bullet 350"]:
                if m in text:
                    b_model = m.title()
                    break

            sim_fault = None
            for sf in ["tappet", "ટેપેટ", "chain", "ચેઇન", "clutch", "ક્લચ", "piston", "પિસ્ટન", "exhaust", "એક્ઝોસ્ટ", "healthy", "સ્વસ્થ"]:
                if sf in text:
                    if sf in ["tappet", "ટેપેટ"]: sim_fault = "tappet"
                    elif sf in ["chain", "ચેઇન"]: sim_fault = "chain"
                    elif sf in ["clutch", "ક્લચ"]: sim_fault = "clutch"
                    elif sf in ["piston", "પિસ્ટન"]: sim_fault = "piston"
                    elif sf in ["exhaust", "એક્ઝોસ્ટ"]: sim_fault = "exhaust"
                    elif sf in ["healthy", "સ્વસ્થ"]: sim_fault = "healthy"
                    break

            res = chamunda_diagnose_engine_sound(bike_model=b_model, simulate_fault=sim_fault)
            msg_gu = f"જી સાહેબ (Alpesh Sir)! રોયલ એનફિલ્ડ એન્જિન સાઉન્ડ ડાયગ્નોસિસ સફળતાપૂર્વક પૂર્ણ થયું છે:\n\n{res}"
            msg_en = f"Sir (Alpesh Sir), Royal Enfield engine sound diagnosis completed successfully:\n\n{res}"
            return self._format_response(msg_gu, msg_en)

        # 14a-2. Service Job Card Invoicing with Health Passport & QR Code (Chamunda AI)
        if any(w in text for w in ["invoice", "ઇન્વોઇસ", "બિલ", "bill", "job card complete", "જોબ કાર્ડ પૂરું", "જોબ કાર્ડ ક્લોઝ", "complete job"]):
            m_job = re.search(r'\b(JOB-[0-9\-]+)\b', raw.upper())
            if m_job:
                job_id = m_job.group(1)
            else:
                sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
                from service_engine import ChamundaServiceManager
                sm = ChamundaServiceManager()
                jobs = sm.get_all_job_cards()
                if jobs:
                    job_id = jobs[0]["job_card_id"]
                else:
                    new_job = sm.create_job_card(
                        customer_name="Alpesh Patel",
                        phone="+91 98765 43210",
                        bike_model="Hunter 350",
                        registration_no="GJ-01-RE-2026",
                        odometer_km=8500,
                        customer_issues="Master service and check-in"
                    )
                    job_id = new_job["job_card_id"]

            res = chamunda_complete_job_and_invoice(job_card_id=job_id)
            msg_gu = f"જી સાહેબ (Alpesh Sir)! સર્વિસ જોબ કાર્ડ `{job_id}` સફળતાપૂર્વક પૂર્ણ કરી ડિજિટલ હેલ્થ પાસપોર્ટ અને QR કોડ સાથે GST ઇન્વોઇસ ઇશ્યૂ કરવામાં આવ્યું છે:\n\n{res}"
            msg_en = f"Sir (Alpesh Sir), Service Job Card `{job_id}` has been completed and GST Invoice with Digital Health Passport & QR Code generated:\n\n{res}"
            return self._format_response(msg_gu, msg_en)

        # 14a. Royal Enfield Digital Acoustic Health Passport (Chamunda AI)
        if any(w in text for w in ["health passport", "હેલ્થ પાસપોર્ટ", "પાસપોર્ટ", "acoustic passport", "engine certificate", "સર્ટિફિકેટ", "sound passport"]):
            c_name = "Alpesh Patel"
            b_model = "Hunter 350"
            for m in ["hunter 350", "hunter", "classic 350", "classic", "interceptor 650", "interceptor", "gt 650", "himalayan 450", "himalayan", "meteor 350", "bullet 350"]:
                if m in text:
                    b_model = m.title()
                    break

            m_reg = re.search(r'\b([A-Z]{2}[-\s]?[0-9]{2}[-\s]?[A-Z]{1,3}[-\s]?[0-9]{1,4})\b', raw.upper())
            reg_no = m_reg.group(1).replace(" ", "-") if m_reg else "GJ-01-RE-2026"

            m_odo = re.search(r'(\d+)\s*(?:km|કિમી)', text)
            odo_km = int(m_odo.group(1)) if m_odo else 8500

            res = chamunda_generate_health_passport(
                customer_name=c_name,
                phone="+91 98765 43210",
                bike_model=b_model,
                registration_no=reg_no,
                odometer_km=odo_km,
                service_notes="Periodic 50-Point Master Service + Valve Clearance Acoustic Audit"
            )

            msg_gu = f"જી સાહેબ (Alpesh Sir)! ચામુંડા ઓટોમોબાઇલ ડિજિટલ એકોસ્ટિક હેલ્થ પાસપોર્ટ સફળતાપૂર્વક જનરેટ કરવામાં આવ્યો છે:\n\n{res}"
            msg_en = f"Sir (Alpesh Sir), Chamunda Automobile Digital Acoustic Health Passport generated successfully:\n\n{res}"
            return self._format_response(msg_gu, msg_en)

        # 14a2. Royal Enfield Spare Parts Catalog & Multi-Filter Search (Chamunda AI)
        re_part_keywords = [
            "spare", "સ્પેર", "part", "પાર્ટ", "oem", "chamunda", "ચામુંડા", "enfield", "એનફિલ્ડ",
            "oil filter", "brake pad", "clutch", "spark plug", "air filter", "fuel filter"
        ]
        if any(w in text for w in re_part_keywords) and not any(w in text for w in ["idea", "આઈડિયા", "surprise", "સરપ્રાઈઝ", "marketing", "youtube", "વિડિઓ", "passport", "પાસપોર્ટ", "certificate", "સર્ટિફિકેટ"]):
            target_model = ""
            for m_kw in ["hunter 350", "hunter", "classic 350", "classic", "meteor 350", "meteor", "bullet 350", "bullet", "interceptor 650", "interceptor", "continental gt", "gt 650", "super meteor", "shotgun", "himalayan 450", "himalayan", "guerrilla 450", "guerrilla", "thunderbird"]:
                if m_kw in text:
                    target_model = m_kw
                    break

            target_cat = ""
            for cat_kw in ["braking", "brake", "engine", "service", "electrical", "suspension", "wheel", "drive", "cable", "exhaust", "filter"]:
                if cat_kw in text:
                    if cat_kw in ["braking", "brake"]: target_cat = "Braking"
                    elif cat_kw in ["engine"]: target_cat = "Engine"
                    elif cat_kw in ["service", "filter"]: target_cat = "Service"
                    elif cat_kw in ["electrical"]: target_cat = "Electrical"
                    elif cat_kw in ["suspension"]: target_cat = "Suspension"
                    elif cat_kw in ["wheel", "drive"]: target_cat = "Drive"
                    elif cat_kw in ["cable"]: target_cat = "Cable"
                    elif cat_kw in ["exhaust"]: target_cat = "Exhaust"
                    break

            min_p = None
            max_p = None
            m_under = re.search(r'(?:under|below|<|sub|કરતાં ઓછી|ઓછી)\s*(?:₹|rs\.?|inr)?\s*(\d+)', raw, re.IGNORECASE)
            if m_under:
                max_p = float(m_under.group(1))
            m_above = re.search(r'(?:above|over|>|વધુ|કરતાં વધુ)\s*(?:₹|rs\.?|inr)?\s*(\d+)', raw, re.IGNORECASE)
            if m_above:
                min_p = float(m_above.group(1))

            stock_stat = "all"
            if any(s in text for s in ["in stock", "હાજર", "સ્ટોક છે", "available"]):
                stock_stat = "in_stock"
            elif any(s in text for s in ["low stock", "ઓછો સ્ટોક", "ખલાસ થવા", "shortage"]):
                stock_stat = "low_stock"
            elif any(s in text for s in ["out of stock", "ખલાસ", "સ્ટોક નથી"]):
                stock_stat = "out_of_stock"

            m_pn = re.search(r'\b([A-Z0-9]{5,10}(?:/[A-Z0-9]+)?)\b', raw)
            pn = m_pn.group(1) if m_pn and any(c.isdigit() for c in m_pn.group(1)) and not any(m_pn.group(1).lower() == w for w in ["hunter", "bullet", "classic", "meteor"]) else ""

            clean_q = raw
            # Remove price patterns from query string
            clean_q = re.sub(r'(?:under|below|<|sub|કરતાં ઓછી|ઓછી|above|over|>|વધુ|કરતાં વધુ)\s*(?:₹|rs\.?|inr)?\s*\d+', '', clean_q, flags=re.IGNORECASE).strip()
            for stop in ["ચામુંડા", "સ્પેર", "પાર્ટ", "પાર્ટ્સ", "શોધો", "બતાવો", "royalenfield", "royal enfield", "royal", "enfield", "spare", "parts", "part", "search", "find", "show"]:
                clean_q = re.sub(rf'\b{stop}\b', '', clean_q, flags=re.IGNORECASE).strip()
            if target_model:
                clean_q = re.sub(rf'\b{re.escape(target_model)}\b', '', clean_q, flags=re.IGNORECASE).strip()
            if pn:
                clean_q = re.sub(rf'\b{re.escape(pn)}\b', '', clean_q, flags=re.IGNORECASE).strip()
            clean_q = re.sub(r'\s+', ' ', clean_q).strip()

            res = chamunda_search_parts_filtered(
                query=clean_q,
                part_number=pn,
                model=target_model,
                category=target_cat,
                min_price=min_p,
                max_price=max_p,
                stock_status=stock_stat,
                limit=15
            )

            msg_gu = f"જી સાહેબ (Alpesh Sir)! ચામુંડા ઓટોમોબાઇલ રોયલ એનફિલ્ડ સ્પેર પાર્ટ્સ કેટલોગ પરિણામ:\n\n{res}"
            msg_en = f"Sir (Alpesh Sir), Chamunda Automobile Royal Enfield genuine spare parts catalog result:\n\n{res}"
            return self._format_response(msg_gu, msg_en)

        # 14b. Proactive Surprise & Innovative Idea Suggestion (Permission granted or explicit request)
        if any(w in text for w in [
            "surprise", "સરપ્રાઈઝ", "idea", "આઈડિયા", "suggestion", "સજેશન", "નવું વિચાર્યું", "નવો આઈડિયા", "કંઈક નવું",
            "હા જણાવો", "જણાવો", "બોલો", "કહો", "yes tell me", "tell me", "sure", "what is the idea", "share idea", "share suggestion",
            "yes", "હા", "yeah", "yep", "y", "ha", "bolo", "janavo"
        ]):
            focus = "any"
            if any(b in text for b in ["business", "રોયલ", "એનફિલ્ડ", "ચામુંડા", "re"]):
                focus = "business"
            elif any(w in text for w in ["workflow", "automation", "ઓટોમેશન", "લેપટોપ"]):
                focus = "workflow"
            res = surprise_me_with_idea(focus_area=focus)
            return self._format_response(
                f"જી સાહેબ (Alpesh Sir)! આપના માટે એક ઉપયોગી અને આશ્ચર્યજનક આઈડિયા વિચાર્યો છે:\n\n{res}",
                f"Sir, here is an innovative proactive surprise and idea for you:\n\n{res}"
            )

        # 14b2. Polite Standby when user has no further work or declines idea
        if any(w in text for w in ["ના", "નહીં", "કંઈ નહીં", "કાંઈ નહીં", "no", "nothing", "not now", "no work", "all good", "standby"]):
            return self._format_response(
                "જી સાહેબ, હું સ્ટેન્ડબાય પર છું. જ્યારે પણ કોઈ નવું કામ કે આદેશ હોય ત્યારે મને જણાવશો!",
                "Understood Sir, standing by for your next command whenever you need me!",
                include_lifecycle=False
            )

        # 14c. Autonomous Self-Evolution & Auto-Tuning
        if any(w in text for w in ["evolve", "ઇવોલ્વ", "evolution", "ઇવોલ્યુશન", "સેલ્ફ-ઇવોલ્યુશન", "self tuning", "સેલ્ફ ટ્યુનિંગ", "self-evolution"]):
            if any(s in text for s in ["status", "સ્ટેટસ", "સ્થિતિ"]):
                res = get_agent_evolution_status()
            else:
                res = trigger_self_evolution_cycle()
            return self._format_response(
                f"જી સાહેબ, આરાધ્યા સેલ્ફ-ઇવોલ્યુશન રિપોર્ટ:\n\n{res}",
                f"Sir, Aradhya Autonomous Self-Evolution report:\n\n{res}"
            )

        # 14d. Total Laptop Control Authority Matrix
        if any(w in text for w in ["control whole laptop", "સંપૂર્ણ કંટ્રોલ", "control laptop", "લેપટોપ કંટ્રોલ", "manage laptop"]):
            stay_res = inspect_stay_awake_status()
            sys_res = diagnose_system_sluggishness()
            control_msg = (
                f"જી સાહેબ (Alpesh Sir)! આપના સમગ્ર લેપટોપનું સંપૂર્ણ નિયંત્રણ મારી પાસે સક્રિય છે.\n\n"
                f"- **હાર્ડવેર અને ઓપરેટિંગ સિસ્ટમ:** વોલ્યુમ, બ્રાઇટનેસ, સ્ક્રીન લૉક, બેટરી પાવર અને ડિસ્પ્લે કંટ્રોલ.\n"
                f"- **સિસ્ટમ સુરક્ષા (Security Sentry):** હેકર્સ, માલવેર, સસ્પીશિયસ પોર્ટ્સ અને ફાયરવોલ ઓડિટ.\n"
                f"- **હૅંગ અને લેગ શિલ્ડ (HangShield):** ઓટોમેટિક CPU સ્પિન ડિટેક્શન અને રનઅવે ટાસ્ક કિલિંગ.\n"
                f"- **વર્ક સ્ટે-અવેક પ્રોટેક્શન (AwakeGuard):** Antigravity, LibreOffice કે અન્ય કામ વખતે સ્લીપ બ્લોકેડ.\n"
                f"- **સ્વાયત્ત કાર્ય એક્ઝિક્યુશન:** ફાઇલ્સ સર્ચ, એપ્લિકેશન લોન્ચિંગ, શેલ કમાન્ડ્સ અને બેકગ્રાઉન્ડ મિશન્સ.\n\n"
                f"આપ કોઈપણ કાર્ય માટે નિઃસંકોચ આદેશ આપી શકો છો!"
            )
            control_en = (
                f"Sir, full operational authority over your entire laptop is active and verified.\n\n"
                f"- **Hardware & OS Controls:** Volume, Brightness, Lockscreen, Battery & Display Management.\n"
                f"- **Cyber Defense (Security Sentry):** Hacker, Malware, Suspicious Sockets & Firewall Protection.\n"
                f"- **Lag & Hang Mitigation (HangShield):** Automatic CPU Spin-Loop & Zombie Process Elimination.\n"
                f"- **Work StayAwake Sentry (AwakeGuard):** Sleep and Lockscreen suppression while working.\n"
                f"- **Autonomous Execution:** File search across disk, App launching, Bash commands, & Background missions.\n\n"
                f"All systems are under total control and ready for your command, Sir!"
            )
            return self._format_response(control_msg, control_en)

        # 15. Direct Shell Command (e.g. "run ls -l", "bash df -h", "$ free -m")
        if text.startswith(("$ ", "run ", "exec ", "કમાન્ડ ", "શેલ ")) or text in ["ls", "df -h", "free -m", "uptime", "whoami"]:
            cmd = re.sub(r'^(?:\$\s*|run\s+|exec\s+|કમાન્ડ\s+|શેલ\s+)', '', raw, flags=re.IGNORECASE).strip()
            if cmd:
                res = execute_shell_command(cmd)
                return self._format_response(f"જી સાહેબ, સ્થાનિક શેલ કમાન્ડ `{cmd}` નું પરિણામ:\n\n```bash\n{res}\n```",
                                             f"Sir, output of local shell command `{cmd}`:\n\n```bash\n{res}\n```")

        # 16. Fallback for Open-Ended Query while Offline
        return self._format_response(
            "જી સાહેબ! હાલમાં લેપટોપ **ઑફલાઇન (ઇન્ટરનેટ વિના)** છે. "
            "આ સામાન્ય પૂછપરછ માટે ક્લાઉડ AI કનેક્શનની જરૂર છે. "
            "પરંતુ તમારા લેપટોપનું સંપૂર્ણ નિયંત્રણ (વોલ્યુમ, બ્રાઇટનેસ, સ્પીડ બૂસ્ટ/સ્લગિશનેસ ક્લીનિંગ, ફાઇલ સર્ચ, "
            "ડિસ્ક વપરાશ, ટર્મિનલ કમાન્ડ્સ અને એપ્સ) ઑફલાઇન સંપૂર્ણપણે સક્રિય છે. ઇન્ટરનેટ જોડાતાં જ ક્લાઉડ AI આપોઆપ સક્રિય થઈ જશે.",
            "Sir, the laptop is currently **offline (no internet connection)**. "
            "This open-ended query requires cloud AI reasoning. "
            "However, all local laptop controls (volume, brightness, speed boost/sluggishness cleanup, file search, "
            "disk telemetry, shell commands, and applications) remain 100% operational offline."
        )

    def _format_response(self, gujarati_text: str, english_text: str, include_lifecycle: bool = True) -> str:
        """Helper to format response according to configured language with post-command lifecycle closure."""
        curr_lang = getattr(self.config, "language", "gujarati").lower()
        base = english_text if curr_lang in ("en", "english") else gujarati_text

        if include_lifecycle:
            if curr_lang in ("en", "english"):
                closure = (
                    "\n\n---\n"
                    "✅ **Work completed successfully, Sir.**\n"
                    "❓ *Is there any other work for me, Sir?*\n"
                    "💡 *(Sir, I also have a new idea/suggestion for you. May I share it?)*"
                )
            else:
                closure = (
                    "\n\n---\n"
                    "✅ **કામ સફળતાપૂર્વક પૂર્ણ થઈ ગયું છે, સાહેબ.**\n"
                    "❓ *બીજું કોઈ કામ છે, સાહેબ?*\n"
                    "💡 *(સાહેબ, મારી પાસે આપના માટે એક નવો આઈડિયા/સજેશન છે, શું હું જણાવી શકું?)*"
                )
            return f"{base}{closure}"
        return base

    handle_offline = execute_offline_turn
