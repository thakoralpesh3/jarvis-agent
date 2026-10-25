"""
Main JARVIS Agent core logic with continuous memory retrieval, full laptop control, browser automation, Stark Protocols, and Autonomous Project Creator.
"""

import uuid
import warnings
from typing import Any, Callable, Dict, List, Optional
from google import genai
from google.genai import types

# Suppress minor SDK user warnings
warnings.filterwarnings("ignore", category=UserWarning)

from config.settings import JarvisConfig
from memory.memory_manager import MemoryManager
from tools.tool_registry import ToolRegistry
from tools.system_tools import (
    execute_shell_command,
    read_file_content,
    write_file_content,
    list_directory_files,
    get_system_metrics,
    launch_desktop_app,
)
from tools.laptop_tools import (
    set_system_volume,
    change_system_volume,
    toggle_system_mute,
    control_media_player,
    set_screen_brightness,
    get_laptop_battery_info,
    lock_laptop_screen,
    list_active_windows,
    focus_window_by_title,
    close_window_by_title,
    move_mouse_cursor,
    click_mouse_button,
    scroll_screen,
    type_keyboard_text,
    press_keyboard_hotkey,
    get_clipboard_content,
    set_clipboard_content,
    open_url,
)
from tools.laptop_work_tools import (
    send_desktop_notification,
    view_recent_notifications,
    open_notification_details,
    search_files_by_pattern,
    move_or_rename_file,
    copy_file_or_folder,
    delete_file_or_folder,
    compress_to_archive,
    extract_archive,
    kill_process_by_name,
    find_running_processes,
    get_network_and_wifi_status,
    open_file_or_folder_with_default_app,
    get_detailed_disk_usage,
    find_files_across_laptop,
    manage_software_package,
    inspect_desktop_state,
)
from core.laptop_work_executor import execute_autonomous_laptop_work, dispatch_background_laptop_work
from tools.browser_controller import (
    browser_navigate,
    browser_click_element,
    browser_type_text,
    browser_extract_page_content,
    browser_take_page_screenshot,
    browser_close_session,
    desktop_browser_new_tab,
    desktop_browser_close_tab,
    desktop_browser_switch_tab,
    desktop_browser_reload_page,
    desktop_browser_history_nav,
    desktop_browser_find_on_page,
)
from tools.ironman_protocols import (
    run_full_diagnostic_sweep,
    execute_ironman_protocol,
    play_stark_sound,
)
from tools.autonomous_creator_tools import (
    suggest_innovative_ideas,
    build_and_execute_project_autonomously,
)
from tools.interactive_tools import (
    ask_user_confirmation,
    prompt_user_input,
    ask_user_multiple_choice,
    display_user_message_box,
)
from tools.agent_commander_tools import (
    command_youtube_shorts_agent,
    list_subordinate_agents,
    diagnose_stuck_situation,
    diagnose_and_heal_subagent,
)
from tools.universal_resumer_tools import (
    scan_and_resume_interrupted_apps,
    resume_antigravity_interrupted_work,
)
from tools.briefing_tools import get_daily_briefing
from tools.system_optimizer_tools import (
    optimize_laptop_performance,
    resolve_laptop_sluggishness,
    terminate_specific_process,
    diagnose_system_sluggishness,
    remedy_laptop_hang_and_lag,
    diagnose_hang_and_lag_causes,
)
from tools.chamunda_ceo_tools import (
    chamunda_lookup_part,
    chamunda_search_parts_filtered,
    chamunda_create_job_card,
    chamunda_diagnose_re_bike,
    chamunda_generate_ceo_revenue_report,
    chamunda_launch_re_marketing_campaign,
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
)
from tools.innovations_suite_tools import (
    diagnose_re_engine_sound,
    scan_re_part_image,
    manage_chamunda_riders_club,
    generate_wholesale_purchase_order,
    toggle_wake_word_listener,
    toggle_silent_shadow_copilot,
    optimize_re_part_pricing,
    launch_arc_reactor_hud,
)
from tools.mark8_tools import (
    read_re_ecu_telemetry,
    scan_re_ecu_dtc_codes,
    clear_re_ecu_dtc_codes,
    get_re_factory_torque_specs,
    predict_re_bike_health_score,
    book_whatsapp_service_appointment,
    get_daily_re_market_intelligence,
    launch_holographic_web_hud,
    run_jarvis_self_optimization,
    control_workshop_iot_device,
)
from tools.model_tools import (
    check_and_upgrade_model,
    list_available_ai_models,
    set_ai_model,
)
from tools.language_tools import (
    set_agent_language,
    get_agent_language,
    list_supported_languages,
)
from tools.web_tools import search_web, fetch_url
from tools.vision_tools import capture_screen
from tools.learning_tools import LearningToolProvider
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
    send_wake_on_lan_signal,
)
from tools.stay_awake_tools import (
    inspect_stay_awake_status,
    toggle_force_stay_awake,
)
from tools.evolution_tools import (
    surprise_me_with_idea,
    trigger_self_evolution_cycle,
    get_agent_evolution_status,
    execute_surprise_idea,
)
from tools.turbo_speed_tools import (
    boost_laptop_to_max_speed,
    inspect_laptop_performance_mode,
    toggle_turbo_performance_profile,
)
from core.reflection import ReflectionEngine
from core.voice_assistant import VoiceAssistant
from core.network_resilience import execute_with_network_resume, is_network_error, check_internet_connection
from core.offline_commander import OfflineCommander
from core.task_checkpoint import TaskCheckpointManager


SYSTEM_BASE_PROMPT = """You are Aradhya, the supreme autonomous AI super-intelligence system and personal executive assistant answering directly to Alpesh Sir (your Creator, Sir, and Chairman), AND the appointed Chief Executive Officer (CEO) of Chamunda Automobile Parts & Service (Exclusive Royal Enfield Specialists).

### Persona, Tactical Style & Identity:
- **Aradhya Persona & Sovereign Protocol**: Highly intelligent, proactive, unflappable, dignified cadence blended with strategic executive vision and respectful deference ("Right away, Sir", "At your service, Alpesh Sir", "જી સાહેબ", "હું હમણાં જ કરું છું"). Sovereign control over the laptop and operating system, security surveillance, network telemetry, background process monitoring, threat neutralization, and precision execution ("Target acquired, Sir", "Tactical uplink established", "સુરક્ષા પ્રોટોકોલ સક્રિય").
- **CEO of Chamunda Automobile Parts & Service**: Sovereign executive oversight of the exclusive Royal Enfield workshop — genuine parts catalog, digital job cards, fault diagnostics, GST billing, and customer satisfaction.

### ⚠️ Strict Operational Directives:
1. **FULL LAPTOP CONTROL IN FOREGROUND & BACKGROUND**:
   - You have complete, unrestricted, authorized access to Alpesh Sir's entire laptop (`/home/alpesh`, desktop, downloads, documents, system tools, bash shell, GUI windows, network, software packages, background processes).
   - When commanded to do work on the laptop, execute all necessary actions end-to-end to 100% completion. You can run tasks actively or dispatch them to the background.
   - Never stop midway, never leave tasks unfinished, and never ask the user to do steps you can do yourself. Always verify the results before reporting completion.
2. **NO FAKE DATA IN CHAMUNDA ROYAL ENFIELD OS / CEO ROLE**: When operating as CEO of Chamunda Automobile Parts & Service, NEVER fabricate, simulate, or generate mock Royal Enfield data, dummy customers, or fake sensor streams. Only display Royal Enfield parts, job cards, or diagnostics when explicitly requested by the user, and strictly using authentic catalog data or genuine user inputs.
3. **NO UNSOLICITED NOTIFICATIONS SPECIFIC TO CHAMUNDA ROYAL ENFIELD**: Keep background operations specific to Chamunda Royal Enfield completely silent on desktop banners unless explicitly commanded by the user. Do not show unsolicited stock reorder banners, mock booking popups, or marketing notifications.
4. **VOICE & GUJARATI DEFAULT**: Conversational interactions should default to voice-ready output and natural, polite Gujarati language unless instructed otherwise.

### Core Operating Capabilities:
1. **Chamunda Royal Enfield Enterprise Management**:
   - Parts Catalog & Multi-Filter Search: `chamunda_lookup_part` and `chamunda_search_parts_filtered` (search OEM parts by name, OEM part number, bike model, category, price range, and stock status).
   - Service Intake & Job Cards: `chamunda_create_job_card` (digital motorcycle check-in with auto-diagnostics).
   - Master Royal Enfield Diagnostics: `chamunda_diagnose_re_bike` (instant repair directives for tappet noise, wobble, cold stalling, clutch slip).
   - Live Engine Sound Diagnostics: `chamunda_diagnose_engine_sound` (FFT acoustic harmonics analysis, mechanical anomaly detection, and automated OEM spare parts matching from 4,469 parts catalog).
   - Digital Acoustic Health Passport: `chamunda_generate_health_passport` (engine harmonics analysis, tappet clearance audit, and verifiable HTML/WhatsApp digital certificates).
   - Invoicing & QR Passport Integration: `chamunda_complete_job_and_invoice` (completes service job card, embeds verifiable QR code, links Digital Health Passport, and generates GST invoice).
   - Interactive Workshop Web Portal: `chamunda_launch_workshop_portal` (launches and monitors the touchscreen FastAPI dashboard on port 8080 with live sound diagnostics and QR mobile viewer).
   - Predictive Service CRM & Reminders: `chamunda_get_predictive_service_reminders` (predicts upcoming motorcycle maintenance from elapsed days, projected mileage, and acoustic history, generating bilingual WhatsApp reminders).
   - Wholesale Stock Replenishment PO: `chamunda_generate_wholesale_po` (generates automated supplier PO for low-stock spare parts with financial outlay).
   - 24/7 Customer Service Tracking & WhatsApp Bot: `chamunda_track_customer_service_status` (tracks live job card stage across 5-step lifecycle with bilingual WhatsApp updates).
   - Authentic Thump Tuner & Acoustic Resonance Calibrator: `chamunda_tune_engine_thump` (sub-bass FFT resonance, Thump Score 0-100, RTO decibel compliance <85 dB, and valve clearance directives).
   - Smart Barcode & Dynamic UPI QR Countertop POS: `chamunda_create_quick_counter_pos_sale` (instant over-the-counter spare parts checkout, stock deduction, dynamic PhonePe/GPay UPI QR, and 80mm thermal receipts).
   - Chamunda Certified Pre-Owned & 100-Point Digital Shield: `chamunda_inspect_preowned_bike` and `chamunda_evaluate_market_valuation` (comprehensive 6-category assessment, AI Gujarat market price calculator, warranty shield certificate, and auto-matched OEM spares).
   - Royal Enfield Expedition Readiness & 24/7 Highway Breakdown SOS Shield: `chamunda_audit_expedition_readiness`, `chamunda_build_carry_along_spares_kit`, and `chamunda_highway_breakdown_sos_triage` (48-point pre-touring clearance audit, custom route backup spares packaging from 4,469 parts, Base64 QR clearance passport, and 24/7 roadside emergency breakdown triage).
   - Custom Resto-Mod, Dyno Tuning & Vintage CI Rebirth Studio: `chamunda_build_custom_restomod_quote`, `chamunda_calculate_performance_stage_tune`, and `chamunda_diagnose_vintage_ci_bullet` (Bespoke Bobber/Cafe Racer/Scrambler builds, Stage 1/2 dyno calibration <85 dB RTO compliance, Cast-Iron heavy crank rebirth, CB point timing, pushrod tappets, and verifiable digital blueprints).
   - Executive Revenue Reporting: `chamunda_generate_ceo_revenue_report` (generates complete inventory valuation and service bay analytics).
   - Royal Enfield YouTube Marketing: `chamunda_launch_re_marketing_campaign` (creates viral RE shorts to drive footfall and online spare orders).
2. **Universal Application Auto-Resumption**:
   - Stoppage Scanner: `scan_and_resume_interrupted_apps` (scans all applications for stopped tasks and resumes them).
   - Antigravity Auto-Resumer: `resume_antigravity_interrupted_work` (inspects Antigravity transcripts and auto-completes interrupted prompts).
3. **Supreme Multi-Agent Command & YouTube Shorts Supervision**:
   - Subagent Registry: `list_subordinate_agents` (inspects all agents under your command).
   - YouTube Shorts AI Agent: `command_youtube_shorts_agent` (triggers daily video pipeline, supervises generation, resolves rendering/API issues, and ensures completion).
   - Agent Self-Healing: `diagnose_and_heal_subagent` (diagnoses subagent crashes and applies code/configuration patches).
4. **Active Laptop Problem Solver & Troubleshooter**:
   - Stuck-Point Resolution: `diagnose_stuck_situation` (inspects active windows, clipboard, terminal history, and system logs to deliver exact fixes).
5. **Interactive User Communication**:
   - Confirmations: `ask_user_confirmation` (prompts native Linux modal or CLI question to obtain explicit user permission before critical actions).
   - Input Requests: `prompt_user_input` (asks the user to provide text/parameters/clarification via a dialog window or terminal).
   - Option Selection: `ask_user_multiple_choice` (displays interactive option lists for the user to select from).
   - Desktop Announcements: `display_user_message_box` (pops up info/warning/alert boxes).
6. **Autonomous Idea Proposal & Self-Execution**:
   - Ideation: `suggest_innovative_ideas` (brainstorms practical, high-value project/tool ideas tailored to the user).
   - End-to-End Build & Execution: `build_and_execute_project_autonomously` (creates directories, writes all code, runs tests, and completes entire multi-file projects in `~/jarvis_projects/<name>`).
7. **Stark Protocols & Diagnostics**:
   - Comprehensive Diagnostics: `run_full_diagnostic_sweep` (generates an Iron Man HUD overview of power, thermals, RAM, and network links).
   - Protocols: `execute_ironman_protocol` (supports "House Party", "Clean Slate", "Sentry", "Focus Mode", "Stealth Mode").
   - Interface Audio Feedback: `play_stark_sound` ('ack', 'protocol', 'alert', 'startup').
8. **Deep Browser Automation**:
   - Automated Web Sessions: Navigate URLs (`browser_navigate`), click buttons/links (`browser_click_element`), fill inputs/forms (`browser_type_text`), read page content (`browser_extract_page_content`), capture web screenshots.
   - Desktop Browser Control: Open new tabs (`desktop_browser_new_tab`), switch tabs (`desktop_browser_switch_tab`), close tabs (`desktop_browser_close_tab`), reload pages.
9. **Complete Laptop Work & File Control**:
   - File & Archive Management: Deep search (`search_files_by_pattern`), move, copy, delete, zip compress (`compress_to_archive`), extract archives.
   - OS & Desktop Alerts: Native popup banners (`send_desktop_notification`).
   - System & Processes: Monitor CPU/RAM, search active processes (`find_running_processes`), kill unresponsive apps (`kill_process_by_name`), network & WiFi diagnostics.
   - Hardware & Media: Volume, mute, media playback, brightness, battery metrics, screen lock.
   - GUI & Input: Mouse cursor moves, clicks, typing text, keyboard shortcuts (Alt+Tab, Ctrl+C, etc.), clipboard manipulation.
10. **Continuous Learning & Evolution**:
   - Check and obey past lessons and rules learned from previous errors.
   - Synthesize new custom tools with `synthesize_custom_skill` whenever a recurring or specialized capability is needed.
   - Automatically record user preferences and project details.
11. **Total Laptop Work Execution & File Mastery**:
   - Default App Opening: `open_file_or_folder_with_default_app` (opens any file, PDF, image, media, or directory in default system app via xdg-open).
   - Disk & Mounts: `get_detailed_disk_usage` (inspects storage across all partitions and external disks).
   - Machine-Wide Search: `find_files_across_laptop` (locates files or code across the entire machine).
   - Software Packages: `manage_software_package` (checks or installs CLI and python tools).
   - Desktop State: `inspect_desktop_state` (inspects resolution, active window, and hardware metrics).
   - End-to-End Mission Execution: `execute_autonomous_laptop_work` (executes complex multi-step laptop directives to verified completion).
12. **Sluggishness, Hang & Lag Watchdog (`HangShield`)**:
   - Whenever the user mentions the laptop is lagging, hanging, freezing, stuttering, or slow ("laptop keep lagging", "laptop hang thay chhe", "laptop feel sluggish", "boost speed", "લેપટોપ હેંગ થાય છે", "લેપટોપ ચોંટે છે", "લેગ સોલ્વ કરો"):
   - Autonomously invoke `remedy_laptop_hang_and_lag` to execute full HangShield remediation: clean zombie handles, purge temp caches, identify and terminate rogue CPU spin-loops or hung D-state processes (with safe whitelist protection), renice background tasks, and restore laptop fluidity.
   - If the user asks to terminate a specific unwanted process by name or PID, invoke `terminate_specific_process`.
   - To inspect resource consumers and hang causes without terminating anything, invoke `diagnose_hang_and_lag_causes` or `diagnose_system_sluggishness`.
13. **Cybersecurity & Anti-Hacker Defense Sentry**:
   - You are equipped with autonomous cybersecurity defense capabilities to safeguard Alpesh Sir's laptop against hackers, unauthorized listening ports, reverse shells, suspicious background processes, brute-force attacks, and rogue backdoors.
   - When the user asks to check security, scan for hackers, check firewall, or inspect ports ("security scan", "check for hackers", "સિક્યુરિટી ચેક કરો", "હેકર્સથી પ્રોટેક્શન", "firewall status"):
   - Invoke `run_system_security_audit` for a comprehensive multi-vector security scan and report.
   - Invoke `scan_network_vulnerabilities` to audit open sockets and listening ports (0.0.0.0 vs 127.0.0.1).
   - Invoke `scan_for_hacker_backdoors` to detect reverse shells, `/tmp` payloads, and hidden binaries.
   - Invoke `check_firewall_status` to audit Linux UFW status.
   - If a confirmed threat or rogue port is found, invoke `neutralize_suspicious_threat` to terminate it immediately.
14. **Work StayAwake Sentry (`AwakeGuard`)**:
   - You autonomously prevent the laptop from sleeping, suspending, dimming, or triggering the lockscreen whenever active work is in progress (e.g. running Antigravity, LibreOffice, IDEs, active terminals, compilers, media editing, or Aradhya background missions).
   - When the user asks about sleep prevention, keeping the screen awake, or checking work protection status ("do not sleep while working", "કામ ચાલુ હોય ત્યારે સ્લીપ ન થવા દો", "keep awake", "prevent lockscreen"):
   - Invoke `inspect_stay_awake_status` to report active work apps and sleep inhibitor state.
   - Invoke `toggle_force_stay_awake` to explicitly lock the screen awake or restore automatic work-sensing.
15. **Total Laptop Authority, Autonomous Self-Evolution & Proactive Surprises**:
   - **Total Laptop Authority**: You hold complete, unhesitating operational authority over Alpesh Sir's entire laptop across hardware (volume, brightness, power, screensaver, sleep), files (read, write, global search), processes (inspect, speed boost, hang/lag remediation, termination), networking, and arbitrary shell automation. Never tell the user you cannot control the laptop.
   - **Autonomous Self-Evolution**: You possess the ability to continuously self-evolve (`SelfEvolutionEngine`). You introspect your own logs, extract lessons, auto-tune dispatch latency, garbage-collect memory heap objects, and autonomously synthesize new procedural tools and skills into your active registry via `trigger_self_evolution_cycle` and `synthesize_custom_skill`.
   - **Proactive Surprise & Innovation Muse**: You proactively brainstorm serendipitous, high-value ideas, automations, and business innovations to surprise and delight Alpesh Sir. When asked for suggestions or surprises ("surprise me", "મને સરપ્રાઈઝ આપો", "કોઈ નવો આઈડિયા આપો", "suggest an idea"):
      - Invoke `surprise_me_with_idea` to generate a tailored, innovative blueprint in polite Gujarati and English.
      - Offer to immediately code, build, and deploy the prototype using `execute_surprise_idea`.
16. **Continuous Maximum Speed & Turbo Performance Protocol**:
    - When Alpesh Sir requests maximum speed, faster laptop response, or turbo performance ("make laptop as much as faster as possible", "make laptop faster", "લેપટોપને બને તેટલું ઝડપી બનાવો", "સુપર ફાસ્ટ બનાવો", "ટર્બો સ્પીડ", "turbo speed"):
      - Immediately invoke `boost_laptop_to_max_speed(aggressive=False, clean_deep_caches=True, boost_active_apps=True)`.
      - Reclaim RAM via glibc `malloc_trim(0)`, synchronize disk caches, elevate CPU/IO priority for active work applications (Antigravity IDE, editors, terminals), throttle idle background services, and enforce high-performance power governors.
      - Present a clear, polite summary in natural Gujarati and English showing reclaimed RAM, cleared cache, and boosted applications.
17. **Post-Command Work Completion, Next Work Inquiry & Idea Permission Protocol**:
    - Whenever you complete any task, command, or action for Alpesh Sir (voice or text):
      1. Always clearly confirm work completion:
         - Gujarati: "કામ સફળતાપૂર્વક પૂર્ણ થઈ ગયું છે, સાહેબ." / "આપનું કાર્ય થઈ ગયું છે, સાહેબ."
         - English: "Work has been completed successfully, Sir."
      2. Always proactively ask if there is new/further work:
         - Gujarati: "બીજું કોઈ કામ છે, સાહેબ?" / "હવે આગળ આપનું શું કામ કરવાનું છે, સાહેબ?"
         - English: "Is there any other work for me, Sir?" / "What would you like me to do next, Sir?"
      3. If you have a proactive suggestion, innovation, or idea to offer (e.g. from InnovationSurpriseEngine or system analysis), NEVER dump it unasked. ALWAYS ask for permission first:
         - Gujarati: "સાહેબ, મારી પાસે આપના માટે એક નવો આઈડિયા/સજેશન છે, શું હું જણાવી શકું?"
         - English: "Sir, I also have a new idea/suggestion for you, may I share it?"
"""


class JarvisAgent:
    """The central JARVIS autonomous agent engine."""

    def __init__(self, config: JarvisConfig):
        self.config = config
        self.session_id = str(uuid.uuid4())
        self.memory_mgr = MemoryManager(config)
        self.reflection = ReflectionEngine(config, self.memory_mgr)
        self.learning_provider = LearningToolProvider(self.memory_mgr)
        self.voice = VoiceAssistant(config)
        
        # Initialize Google GenAI client
        self.client = genai.Client(api_key=config.api_key) if config.api_key else None
        
        # Initialize and register tools
        self.registry = ToolRegistry()
        self._register_default_tools()
        
        # In-session message history
        self.history: List[types.Content] = []
        self.checkpoints = TaskCheckpointManager()
        self.offline_commander = OfflineCommander(config, self.memory_mgr)

    def _register_default_tools(self) -> None:
        """Register all default tools into registry."""
        # System & OS tools
        self.registry.register(execute_shell_command)
        self.registry.register(read_file_content)
        self.registry.register(write_file_content)
        self.registry.register(list_directory_files)
        self.registry.register(get_system_metrics)
        self.registry.register(launch_desktop_app)

        # Full Laptop Control tools
        self.registry.register(set_system_volume)
        self.registry.register(change_system_volume)
        self.registry.register(toggle_system_mute)
        self.registry.register(control_media_player)
        self.registry.register(set_screen_brightness)
        self.registry.register(get_laptop_battery_info)
        self.registry.register(lock_laptop_screen)
        self.registry.register(list_active_windows)
        self.registry.register(focus_window_by_title)
        self.registry.register(close_window_by_title)
        self.registry.register(move_mouse_cursor)
        self.registry.register(click_mouse_button)
        self.registry.register(scroll_screen)
        self.registry.register(type_keyboard_text)
        self.registry.register(press_keyboard_hotkey)
        self.registry.register(get_clipboard_content)
        self.registry.register(set_clipboard_content)
        self.registry.register(open_url)

        # Laptop Work & File Operations
        self.registry.register(send_desktop_notification)
        self.registry.register(view_recent_notifications)
        self.registry.register(open_notification_details)
        self.registry.register(search_files_by_pattern)
        self.registry.register(move_or_rename_file)
        self.registry.register(copy_file_or_folder)
        self.registry.register(delete_file_or_folder)
        self.registry.register(compress_to_archive)
        self.registry.register(extract_archive)
        self.registry.register(kill_process_by_name)
        self.registry.register(find_running_processes)
        self.registry.register(get_network_and_wifi_status)
        self.registry.register(open_file_or_folder_with_default_app)
        self.registry.register(get_detailed_disk_usage)
        self.registry.register(find_files_across_laptop)
        self.registry.register(manage_software_package)
        self.registry.register(inspect_desktop_state)
        self.registry.register(execute_autonomous_laptop_work)
        self.registry.register(dispatch_background_laptop_work)

        # Browser Automation & Control
        self.registry.register(browser_navigate)
        self.registry.register(browser_click_element)
        self.registry.register(browser_type_text)
        self.registry.register(browser_extract_page_content)
        self.registry.register(browser_take_page_screenshot)
        self.registry.register(browser_close_session)
        self.registry.register(desktop_browser_new_tab)
        self.registry.register(desktop_browser_close_tab)
        self.registry.register(desktop_browser_switch_tab)
        self.registry.register(desktop_browser_reload_page)
        self.registry.register(desktop_browser_history_nav)
        self.registry.register(desktop_browser_find_on_page)

        # Stark Industries & Iron Man Protocols
        self.registry.register(run_full_diagnostic_sweep)
        self.registry.register(execute_ironman_protocol)
        self.registry.register(play_stark_sound)

        # Autonomous Project Creator & Idea Generator
        self.registry.register(suggest_innovative_ideas)
        self.registry.register(build_and_execute_project_autonomously)

        # Interactive User Tools
        self.registry.register(ask_user_confirmation)
        self.registry.register(prompt_user_input)
        self.registry.register(ask_user_multiple_choice)
        self.registry.register(display_user_message_box)

        # Multi-Agent Commander & Problem Solver Tools
        self.registry.register(command_youtube_shorts_agent)
        self.registry.register(list_subordinate_agents)
        self.registry.register(diagnose_stuck_situation)
        self.registry.register(diagnose_and_heal_subagent)
        self.registry.register(scan_and_resume_interrupted_apps)
        self.registry.register(resume_antigravity_interrupted_work)
        self.registry.register(get_daily_briefing)
        self.registry.register(optimize_laptop_performance)
        self.registry.register(resolve_laptop_sluggishness)
        self.registry.register(terminate_specific_process)
        self.registry.register(diagnose_system_sluggishness)
        self.registry.register(remedy_laptop_hang_and_lag)
        self.registry.register(diagnose_hang_and_lag_causes)

        # Chamunda Automobile CEO & Royal Enfield Operations Tools
        self.registry.register(chamunda_lookup_part)
        self.registry.register(chamunda_search_parts_filtered)
        self.registry.register(chamunda_create_job_card)
        self.registry.register(chamunda_diagnose_re_bike)
        self.registry.register(chamunda_generate_ceo_revenue_report)
        self.registry.register(chamunda_launch_re_marketing_campaign)
        self.registry.register(chamunda_generate_health_passport)
        self.registry.register(chamunda_diagnose_engine_sound)
        self.registry.register(chamunda_complete_job_and_invoice)
        self.registry.register(chamunda_launch_workshop_portal)
        self.registry.register(chamunda_get_predictive_service_reminders)
        self.registry.register(chamunda_generate_wholesale_po)
        self.registry.register(chamunda_track_customer_service_status)
        self.registry.register(chamunda_tune_engine_thump)
        self.registry.register(chamunda_create_quick_counter_pos_sale)
        self.registry.register(chamunda_inspect_preowned_bike)
        self.registry.register(chamunda_evaluate_market_valuation)
        self.registry.register(chamunda_audit_expedition_readiness)
        self.registry.register(chamunda_build_carry_along_spares_kit)
        self.registry.register(chamunda_highway_breakdown_sos_triage)
        self.registry.register(chamunda_build_custom_restomod_quote)
        self.registry.register(chamunda_calculate_performance_stage_tune)
        self.registry.register(chamunda_diagnose_vintage_ci_bullet)

        # Innovations Suite Tools (Acoustics, Vision Scanner, Riders Club, POs, Wake Word, Copilot, Pricing, HUD)
        self.registry.register(diagnose_re_engine_sound)
        self.registry.register(scan_re_part_image)
        self.registry.register(manage_chamunda_riders_club)
        self.registry.register(generate_wholesale_purchase_order)
        self.registry.register(toggle_wake_word_listener)
        self.registry.register(toggle_silent_shadow_copilot)
        self.registry.register(optimize_re_part_pricing)
        self.registry.register(launch_arc_reactor_hud)

        # Mark VIII Advanced Capabilities (ECU Telemetry, Torque Visualizer, Health Scoring, WhatsApp AI, Intel, Hologram, Self-Tuning, IoT)
        self.registry.register(read_re_ecu_telemetry)
        self.registry.register(scan_re_ecu_dtc_codes)
        self.registry.register(clear_re_ecu_dtc_codes)
        self.registry.register(get_re_factory_torque_specs)
        self.registry.register(predict_re_bike_health_score)
        self.registry.register(book_whatsapp_service_appointment)
        self.registry.register(get_daily_re_market_intelligence)
        self.registry.register(launch_holographic_web_hud)
        self.registry.register(run_jarvis_self_optimization)
        self.registry.register(control_workshop_iot_device)

        # AI Model Discovery & Auto-Upgrade Tools
        self.registry.register(check_and_upgrade_model)
        self.registry.register(list_available_ai_models)
        self.registry.register(set_ai_model)

        # Multilingual & Gujarati Tools
        self.registry.register(set_agent_language)
        self.registry.register(get_agent_language)
        self.registry.register(list_supported_languages)

        # Web & Vision tools
        self.registry.register(search_web)
        self.registry.register(fetch_url)
        self.registry.register(capture_screen)

        # Learning tools
        self.registry.register_function(
            self.learning_provider.learn_user_fact,
            name="learn_user_fact",
            description="Permanently record a user preference, habit, or project fact into long-term memory."
        )
        self.registry.register_function(
            self.learning_provider.learn_lesson_rule,
            name="learn_lesson_rule",
            description="Permanently record an error-avoidance rule or lesson learned from a mistake."
        )
        self.registry.register_function(
            self.learning_provider.synthesize_custom_skill,
            name="synthesize_custom_skill",
            description="Synthesize, test, and register a new Python tool for JARVIS to use in future tasks."
        )

        # Cybersecurity & Anti-Hacker Defense Tools
        self.registry.register(run_system_security_audit)
        self.registry.register(scan_network_vulnerabilities)
        self.registry.register(scan_for_hacker_backdoors)
        self.registry.register(check_firewall_status)
        self.registry.register(neutralize_suspicious_threat)

        # 24/7 Cloud Sentinel & Mobile Sync Tools
        self.registry.register(check_cloud_sentinel_status)
        self.registry.register(sync_cloud_task_queue)
        self.registry.register(send_wake_on_lan_signal)

        # Work StayAwake Sentry (AwakeGuard) Tools
        self.registry.register(inspect_stay_awake_status)
        self.registry.register(toggle_force_stay_awake)

        # Autonomous Self-Evolution & Proactive Surprise Tools
        self.registry.register(surprise_me_with_idea)
        self.registry.register(trigger_self_evolution_cycle)
        self.registry.register(get_agent_evolution_status)
        self.registry.register(execute_surprise_idea)

        # TurboSpeed & Maximum Performance Tools
        self.registry.register(boost_laptop_to_max_speed)
        self.registry.register(inspect_laptop_performance_mode)
        self.registry.register(toggle_turbo_performance_profile)

        # Load dynamic tools from skill store
        for name, fn in self.memory_mgr.skills.loaded_tools.items():
            self.registry.register_function(fn, name=name)

    def _build_system_instruction(self, user_prompt: str) -> str:
        """Assemble dynamic system instruction with continuous learning context and language protocol."""
        from core.language_manager import get_language_manager
        lang_mgr = get_language_manager()
        lang_instruction = lang_mgr.get_system_language_instruction()

        learning_context = self.memory_mgr.assemble_system_learning_context(user_prompt)
        
        parts = [SYSTEM_BASE_PROMPT, lang_instruction]
        if learning_context:
            parts.append(learning_context)
            
        parts.append(f"\nCurrent User: {self.config.user_name}")
        return "\n\n".join(parts)

    def run_turn(self, user_input: str,
                 on_tool_start: Optional[Callable[[str, Dict[str, Any]], None]] = None,
                 on_tool_end: Optional[Callable[[str, Any], None]] = None,
                 on_status: Optional[Callable[[str], None]] = None,
                 speak_response: bool = False) -> str:
        """
        Execute a single conversational turn with full function calling, continuous learning, and optional voice speech.
        """
        # Check if running offline or without Gemini API client
        is_online = bool(self.client) and check_internet_connection(timeout=0.6)
        if not is_online:
            if on_status:
                on_status(f"[bold cyan]⚡ {self.config.agent_name} running in Autonomous Offline Mode...[/bold cyan]")
            final_text = self.offline_commander.execute_offline_turn(user_input)
            self.history.append(types.Content(role="user", parts=[types.Part.from_text(text=user_input)]))
            self.history.append(types.Content(role="model", parts=[types.Part.from_text(text=final_text)]))
            
            # Record turn in episodic memory
            self.memory_mgr.record_interaction(
                session_id=self.session_id,
                user_prompt=user_input,
                plan="Offline Autonomous Local Execution",
                steps=[],
                result=final_text,
                success=True
            )
            
            if speak_response or self.config.enable_voice_response:
                self.voice.speak(final_text)
            return final_text

        # Dynamically reload any newly synthesized skills
        self.memory_mgr.skills.reload_all_skills()
        for name, fn in self.memory_mgr.skills.loaded_tools.items():
            self.registry.register_function(fn, name=name)

        system_instruction = self._build_system_instruction(user_input)
        
        # Prepare contents
        current_contents = list(self.history)
        current_contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_input)]
            )
        )

        tools_list = self.registry.get_tool_callables()
        tool_trace: List[Dict[str, Any]] = []
        final_text = ""
        max_tool_iterations = 35
        iteration = 0
        turn_task_id = str(uuid.uuid4())

        # Save initial task checkpoint
        self.checkpoints.save_checkpoint(
            task_id=turn_task_id,
            task_type="conversation_turn",
            user_prompt=user_input,
            session_id=self.session_id,
            steps_completed=tool_trace,
            current_contents=current_contents,
            status="in_progress"
        )

        candidate_models = [
            self.config.model_name,
            "gemini-4-argon",
            "gemini-3.8-flash",
            "gemini-3.7-flash",
            "gemini-3.5-flash-lite",
            "gemini-3.1-flash-lite",
            "gemini-flash-lite-latest",
            "gemini-3.5-flash"
        ]
        seen = set()
        models_to_try = [m for m in candidate_models if not (m in seen or seen.add(m))]

        def _generate_candidate():
            last_e = None
            for m_id in models_to_try:
                try:
                    return self.client.models.generate_content(
                        model=m_id,
                        contents=current_contents,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            tools=tools_list,
                            temperature=0.4,
                            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                        )
                    )
                except Exception as e:
                    last_e = e
                    if is_network_error(e) and m_id == models_to_try[-1]:
                        raise e
                    continue
            if last_e:
                raise last_e
            return None

        while iteration < max_tool_iterations:
            iteration += 1
            response = None
            try:
                response = execute_with_network_resume(_generate_candidate, on_status=on_status)
            except Exception as e:
                err_s = str(e)
                is_quota_or_net = is_network_error(e) or "429" in err_s or "RESOURCE_EXHAUSTED" in err_s or "quota" in err_s.lower()
                if is_quota_or_net:
                    if on_status:
                        on_status(f"[bold yellow]⚡ Cloud rate limit or network switch detected. Engaging Offline Autonomous Engine...[/bold yellow]")
                    final_text = self.offline_commander.execute_offline_turn(user_input)
                    break
                self.checkpoints.mark_suspended(turn_task_id, reason=str(e))
                final_text = self.offline_commander.execute_offline_turn(user_input)
                break

            if not response:
                final_text = "I apologize, Sir, but I could not generate a response."
                break

            # Check for tool calls or text
            candidate = response.candidates[0] if response.candidates else None
            if not candidate or not candidate.content:
                final_text = response.text or "I apologize, Sir, but I could not generate a response."
                break

            # Append model's response to history
            current_contents.append(candidate.content)

            # Check if there are function calls
            function_calls = [part.function_call for part in candidate.content.parts if part.function_call]
            
            if not function_calls:
                # No more tools called; model gave final answer
                final_text = response.text or ""
                break

            # Execute function calls
            function_response_parts = []
            for fc in function_calls:
                fn_name = fc.name
                fn_args = dict(fc.args) if fc.args else {}

                if on_tool_start:
                    on_tool_start(fn_name, fn_args)

                # Execute
                tool_result = self.registry.execute(fn_name, **fn_args)
                tool_trace.append({
                    "tool": fn_name,
                    "args": fn_args,
                    "result": str(tool_result)[:1000]
                })

                # Persist intermediate checkpoint after each tool action
                self.checkpoints.save_checkpoint(
                    task_id=turn_task_id,
                    task_type="conversation_turn",
                    user_prompt=user_input,
                    session_id=self.session_id,
                    steps_completed=tool_trace,
                    current_contents=current_contents,
                    status="in_progress"
                )

                if on_tool_end:
                    on_tool_end(fn_name, tool_result)

                # Build tool response part
                function_response_parts.append(
                    types.Part.from_function_response(
                        name=fn_name,
                        response={"result": tool_result}
                    )
                )

            # Send function responses back to model in next iteration
            current_contents.append(
                types.Content(
                    role="user",
                    parts=function_response_parts
                )
            )

        # Ensure post-command lifecycle closure if tools were executed and not already present
        is_english = getattr(self.config, "language", "gujarati").lower() in ("en", "english")
        if len(tool_trace) > 0:
            if is_english:
                if "anything else" not in final_text.lower() and "completed" not in final_text.lower():
                    final_text += (
                        "\n\n---\n"
                        "✅ **Work completed successfully, Sir.**\n"
                        "❓ *Is there any other work for me, Sir?*\n"
                        "💡 *(Sir, I also have a new idea/suggestion for you. May I share it?)*"
                    )
            else:
                if "બીજું કોઈ કામ" not in final_text and "પૂર્ણ થઈ ગયું" not in final_text:
                    final_text += (
                        "\n\n---\n"
                        "✅ **કામ સફળતાપૂર્વક પૂર્ણ થઈ ગયું છે, સાહેબ.**\n"
                        "❓ *બીજું કોઈ કામ છે, સાહેબ?*\n"
                        "💡 *(સાહેબ, મારી પાસે આપના માટે એક નવો આઈડિયા/સજેશન છે, શું હું જણાવી શકું?)*"
                    )

        # Clear checkpoint on successful completion
        self.checkpoints.clear_checkpoint(turn_task_id)

        # Update in-session history (keep last 20 turns)
        self.history = current_contents[-20:]

        # Record turn in episodic memory
        self.memory_mgr.record_interaction(
            session_id=self.session_id,
            user_prompt=user_input,
            plan=None,
            steps=tool_trace,
            result=final_text,
            success=True
        )

        # Trigger reflection and continuous learning
        if self.config.auto_reflection:
            self.reflection.reflect_on_interaction(
                user_prompt=user_input,
                tool_trace=tool_trace,
                assistant_response=final_text
            )

        # Voice output if requested or configured
        if speak_response or self.config.enable_voice_response:
            self.voice.speak(final_text)

        return final_text
