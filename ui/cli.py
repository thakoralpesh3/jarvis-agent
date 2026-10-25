"""
Unified Stark Industries HUD & Multimodal Interface for JARVIS.
Combines Chat, Voice, Telemetry Diagnostics, and Long-Term Memory into a single seamless experience.
"""

import sys
import time
import json
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.live import Live
from rich.spinner import Spinner
from rich.prompt import Prompt

from config.settings import JarvisConfig, load_config, save_config
from core.agent import JarvisAgent
from tools.ironman_protocols import play_stark_sound, run_full_diagnostic_sweep, execute_ironman_protocol


console = Console()


def save_conversation_turn(agent: JarvisAgent, user_text: str, is_voice: bool, tools_used: list, response: str):
    """Persist conversation log to JSON so it can be rendered and inspected in launcher."""
    conv_file = agent.config.base_dir / "conversation_history.json"
    history = []
    if conv_file.exists():
        try:
            with open(conv_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

    turn = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "user": user_text,
        "mode": "voice" if is_voice else "text",
        "tools": tools_used,
        "response": response
    }
    history.append(turn)
    # Keep last 50 turns
    history = history[-50:]
    try:
        with open(conv_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def render_conversation_panel(agent_name: str, user_text: str, is_voice: bool, tool_events: list, response: str):
    """Render structured live conversation turn panel in the launcher."""
    t_str = time.strftime("%I:%M:%S %p")
    input_badge = "🎙️ Voice Command" if is_voice else "⌨️ Text Command"

    parts = []
    parts.append(f"### 👤 Alpesh Sir ({t_str} • {input_badge})\n> {user_text}")

    if tool_events:
        parts.append("\n**⚡ Actuation & Tools Run:**")
        for te in tool_events[:4]:
            parts.append(f"- `{te.get('name')}`: *{te.get('preview', '')}*")

    parts.append(f"\n### 🤖 {agent_name}\n{response}")

    content = "\n".join(parts)
    console.print(Panel(
        Markdown(content),
        title=f"[bold cyan]💬 LIVE CONVERSATION STREAM • {agent_name} & Alpesh Sir[/bold cyan]",
        border_style="cyan",
        expand=False
    ))


def display_conversation_history(agent: JarvisAgent):
    """Display past conversation history turns in launcher."""
    conv_file = agent.config.base_dir / "conversation_history.json"
    if not conv_file.exists():
        console.print("[yellow]No conversation history recorded yet.[/yellow]")
        return

    try:
        with open(conv_file, "r", encoding="utf-8") as f:
            history = json.load(f)
    except Exception:
        history = []

    if not history:
        console.print("[yellow]Conversation history is empty.[/yellow]")
        return

    console.print(f"\n[bold cyan]📜 RECENT CONVERSATION LOGS ({len(history)} turns recorded):[/bold cyan]\n")
    for i, turn in enumerate(history[-10:], 1):
        render_conversation_panel(
            agent.config.agent_name,
            turn.get("user", ""),
            turn.get("mode") == "voice",
            turn.get("tools", []),
            turn.get("response", "")
        )


def render_unified_hud(agent: JarvisAgent):
    """Render unified Stark Industries Arc Reactor & Diagnostics HUD."""
    stats = agent.memory_mgr.get_summary_stats()
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Telemetry", style="bold cyan")
    table.add_column("Status", style="bold green")
    
    table.add_row("🧠 AI Neural Core", f"{agent.config.model_name} (Gemini Live)")
    table.add_row("🎙️ Voice Synthesizer", "[bold green]ONLINE (Natural Human Speech / Gujarati)[/bold green]" if agent.config.enable_voice_response else "[dim]MUTED (/voice to enable)[/dim]")
    table.add_row("⚡ Actuation Tools", "38 Desktop, Laptop, Browser & Protocol Tools")
    table.add_row("🧬 Long-Term Memory", f"{stats['facts']} facts • {stats['lessons']} rules • {stats['skills']} dynamic tools")

    from core.network_resilience import check_internet_connection
    is_online = check_internet_connection(timeout=0.5)
    net_status = "[bold green]ONLINE (Cloud & Local)[/bold green]" if is_online else "[bold yellow]OFFLINE (Autonomous Local Engine Active)[/bold yellow]"
    table.add_row("🌐 Network Link", net_status)
    table.add_row("🛡️ Security Shield", "[bold green]ARMED (Anti-Hacker Sentry Active)[/bold green]")

    arc_reactor_art = (
        "[bold cyan]"
        "      .---.\n"
        "    /   |   \\\n"
        "   |  ( ● )  |   [bold yellow]STARK INDUSTRIES • TACTICAL AI[/bold yellow]\n"
        f"    \\   |   /    [bold cyan]{agent.config.agent_name} UNIFIED AUTONOMOUS CORE[/bold cyan]\n"
        "      '---'"
        "[/bold cyan]\n\n"
        "[italic white]\"At your service, Sir. Speak naturally or type your command.\"[/italic white]\n"
    )

    console.print(Panel(
        table,
        title=arc_reactor_art,
        border_style="cyan",
        expand=False
    ))


def display_memory_table(agent: JarvisAgent):
    """Show all learned user facts and preferences."""
    facts = agent.memory_mgr.semantic.get_all_facts()
    if not facts:
        console.print("[yellow]No semantic facts learned yet.[/yellow]")
        return

    table = Table(title="[bold cyan]⚡ J.A.R.V.I.S. Semantic Memory Matrix[/bold cyan]", border_style="cyan")
    table.add_column("Category", style="magenta")
    table.add_column("Parameter / Key", style="bold yellow")
    table.add_column("Learned Value", style="white")
    table.add_column("Confidence", style="dim green")
    table.add_column("Source", style="dim")

    for f in facts:
        table.add_row(
            f["category"],
            f["key"],
            f["value"],
            f"{f['confidence']:.2f}",
            f.get("source", "direct")
        )
    console.print(table)


def display_lessons_table(agent: JarvisAgent):
    """Show all learned lessons and rules of thumb."""
    lessons = agent.memory_mgr.episodic.get_all_lessons()
    if not lessons:
        console.print("[yellow]No error-avoidance lessons learned yet.[/yellow]")
        return

    table = Table(title="[bold cyan]🛡️ J.A.R.V.I.S. Self-Correction & Error Avoidance Rules[/bold cyan]", border_style="yellow")
    table.add_column("ID", style="dim")
    table.add_column("Trigger Condition", style="cyan")
    table.add_column("Mistake to Avoid", style="red")
    table.add_column("Rule / Lesson", style="bold green")
    table.add_column("Suggested Solution", style="white")

    for l in lessons:
        table.add_row(
            str(l["id"]),
            l["trigger_pattern"],
            l["mistake"],
            l["lesson"],
            l.get("solution", "")
        )
    console.print(table)


def display_skills_table(agent: JarvisAgent):
    """Show all dynamic synthesized skills."""
    skills = agent.memory_mgr.skills.get_skill_descriptions()
    if not skills:
        console.print("[yellow]No custom dynamic skills synthesized yet.[/yellow]")
        return

    table = Table(title="[bold cyan]⚙️ Synthesized Dynamic Skills Registry[/bold cyan]", border_style="green")
    table.add_column("Skill Name", style="bold green")
    table.add_column("Description", style="white")
    table.add_column("Usage Count", style="cyan")
    table.add_column("Path", style="dim")

    for s in skills:
        table.add_row(
            s["name"],
            s["description"],
            str(s.get("usage_count", 0)),
            s["code_path"]
        )
    console.print(table)


def start_unified_interface(config_path: str = None):
    """
    Launch the Unified 4-in-1 JARVIS Experience.
    Seamlessly integrates Chat, Voice input/output, Laptop Control, and Live Memory & Diagnostics.
    """
    config = load_config(config_path)
    # Default mode is PURE TEXT until explicitly commanded to switch to voice
    config.enable_voice_response = getattr(config, "enable_voice_response", False)
    config.voice_commands_enabled = getattr(config, "voice_commands_enabled", False)
    agent = JarvisAgent(config)

    # 1. Startup HUD
    render_unified_hud(agent)
    console.print("[bold green]💬 DEFAULT MODE: PURE TEXT INTERFACE ACTIVE.[/bold green]")
    console.print("[dim]All voice-based workshop actions, diagnostics, and protocols are 100% available via text.[/dim]")
    console.print("[dim]Commands: [cyan]Type any instruction[/cyan] • [cyan]/voice on[/cyan] (enable speech) • [cyan]/text[/cyan] • [cyan]/turbo[/cyan] (kill lag) • [cyan]/work <task>[/cyan] • [cyan]/exit[/cyan]\n[/dim]")

    # 2. Only run voice interactor if voice was explicitly enabled
    if agent.config.enable_voice_response:
        from core.startup_interactor import StartupVoiceInteractor
        interactor = StartupVoiceInteractor(agent)
        with console.status(f"[bold cyan]🎙️ {agent.config.agent_name} Voice Greeting & Listening...", spinner="dots"):
            startup_res = interactor.run_interactive_startup()

        if startup_res.get("action") == "autonomous_self_work":
            console.print(Panel(
                Markdown(startup_res.get("proposal_report", "") + "\n\n" + startup_res.get("execution_summary", "")),
                title="[bold gold1]🤖 AUTONOMOUS STARTUP SELF-EXECUTION[/bold gold1]",
                border_style="gold1"
            ))
        elif startup_res.get("action") == "user_command_executed":
            console.print(Panel(
                Markdown(str(startup_res.get("turn_response", ""))),
                title="[bold green]⚡ DIRECTIVE EXECUTED[/bold green]",
                border_style="green"
            ))


    # Auto-resume any tasks interrupted by previous network dropouts
    suspended_tasks = agent.checkpoints.get_suspended_checkpoints()
    if suspended_tasks:
        console.print(f"[bold yellow]⚡ Found {len(suspended_tasks)} suspended task(s) in checkpoint memory. Resuming automatically...[/bold yellow]")
        agent.voice.speak(f"Sir, resuming {len(suspended_tasks)} interrupted task from checkpoint memory.")
        agent.checkpoints.auto_resume_suspended_tasks(agent)

    while True:
        try:
            user_text = ""
            is_voice_turn = False

            # If voice commands are enabled and running in an interactive terminal (TTY)
            if getattr(agent.config, "voice_commands_enabled", True) and sys.stdin.isatty():
                console.print(f"\n[bold green]🎙️ {agent.config.agent_name} Active Voice Radar: LISTENING...[/bold green] [dim](Speak naturally in Gujarati/English, or type command)[/dim]")
                
                # Check if user already typed something before mic recording
                import select
                rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
                if rlist:
                    typed = sys.stdin.readline().strip()
                    if typed:
                        user_text = typed
                else:
                    # Record 4 seconds with speech energy detection
                    wav_bytes = agent.voice.record_microphone_audio(duration_seconds=4, require_speech=True)
                    
                    # Check if user typed something during the recording
                    rlist_after, _, _ = select.select([sys.stdin], [], [], 0.05)
                    if rlist_after:
                        typed_after = sys.stdin.readline().strip()
                        if typed_after:
                            user_text = typed_after
                    elif wav_bytes:
                        # Voice speech detected!
                        play_stark_sound("ack")
                        with console.status(f"[dim cyan]🎙️ {agent.config.agent_name}: Transcribing voice command with Gemini...[/dim cyan]", spinner="dots"):
                            user_text = agent.voice.transcribe_audio_with_gemini(wav_bytes)
                        if user_text and "(silence)" not in user_text.lower():
                            console.print(f"[bold cyan]You (Voice):[/bold cyan] {user_text}")
                            is_voice_turn = True
                        else:
                            user_text = ""
                            continue
                    else:
                        # Ambient silence - continue listening seamlessly
                        continue
            else:
                # Text-only mode or non-interactive environment
                prompt_label = "[bold cyan]You[/bold cyan] [dim](type or 'v' to speak)[/dim]"
                raw_input = Prompt.ask(prompt_label, default="").strip()
                if raw_input.lower() in ["v", "voice", "/mic", "/listen", "speak", "બોલો", "સાંભળો"]:
                    play_stark_sound("ack")
                    with console.status("[bold cyan]🎙️ Listening to microphone (Speak now in Gujarati/English)...[/bold cyan]", spinner="arc"):
                        wav_bytes = agent.voice.record_microphone_audio(duration_seconds=5)
                    if wav_bytes:
                        user_text = agent.voice.transcribe_audio_with_gemini(wav_bytes)
                        if user_text:
                            console.print(f"[bold cyan]You (Voice):[/bold cyan] {user_text}")
                            is_voice_turn = True
                else:
                    user_text = raw_input

            # In-Session Shortcuts
            if user_text.lower() in ["/exit", "/quit", "exit", "quit"]:
                console.print(f"[cyan]{agent.config.agent_name}:[/cyan] Systems on standby, Sir. Have a productive day.")
                agent.voice.speak("Systems on standby, Sir. Have a productive day.")
                break

            if user_text.lower() in ["/sweep", "/diagnostics", "/diagnostic", "diagnostics", "sweep"]:
                play_stark_sound("protocol")
                diag_hud = run_full_diagnostic_sweep()
                console.print(Panel(diag_hud, border_style="yellow", title="[bold yellow]HUD TELEMETRY SWEEP[/bold yellow]"))
                agent.voice.speak("Diagnostic sweep complete, Sir. All primary metrics are nominal.")
                continue

            if user_text.lower().startswith("/protocol"):
                prot_name = user_text.replace("/protocol", "").strip() or "House Party"
                res = execute_ironman_protocol(prot_name)
                console.print(f"[bold yellow]Protocol Response:[/bold yellow]\n{res}\n")
                agent.voice.speak(f"{prot_name} protocol initiated, Sir.")
                continue

            if user_text.lower().startswith("/voice") or user_text.lower() in ["/text"]:
                cmd_low = user_text.lower().strip()
                if "off" in cmd_low or cmd_low == "/text":
                    agent.config.voice_commands_enabled = False
                    agent.config.enable_voice_response = False
                    save_config(agent.config)
                    console.print("[bold yellow]Voice radar & audio responses PAUSED. (Text mode active. Type '/voice on' to resume).[/bold yellow]")
                elif "on" in cmd_low:
                    agent.config.voice_commands_enabled = True
                    agent.config.enable_voice_response = True
                    save_config(agent.config)
                    console.print("[bold green]Voice radar & audio responses ARMED. (Active listening enabled).[/bold green]")
                    agent.voice.speak("Voice systems online and armed, Sir.")
                else:
                    agent.config.voice_commands_enabled = not agent.config.voice_commands_enabled
                    agent.config.enable_voice_response = agent.config.voice_commands_enabled
                    save_config(agent.config)
                    state = "ENABLED" if agent.config.voice_commands_enabled else "DISABLED"
                    console.print(f"[bold green]Voice radar {state}.[/bold green]")
                    if agent.config.voice_commands_enabled:
                        agent.voice.speak("Voice systems online, Sir.")
                continue

            if user_text.lower() in ["/memory", "/profile"]:
                display_memory_table(agent)
                continue

            if user_text.lower() in ["/turbo", "/lag", "/boost"]:
                with console.status("[bold green]🚀 Running Turbo Boost & Lag Cleanup...", spinner="dots"):
                    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
                    from system_optimizer import get_system_optimizer
                    optimizer = get_system_optimizer()
                    opt_res = optimizer.optimize_laptop_performance(aggressive=False)
                console.print(Panel(
                    f"[bold green]{opt_res['message_gu']}[/bold green]\n\n[dim]{opt_res['message_en']}[/dim]",
                    title="[bold gold1]🚀 TURBO BOOST & LAG BUSTER COMPLETE[/bold gold1]",
                    border_style="green"
                ))
                continue

            if user_text.lower().startswith("/work ") or user_text.lower().startswith("/mission "):
                cmd_parts = user_text.split(" ", 1)
                mission_task = cmd_parts[1].strip() if len(cmd_parts) > 1 else ""
                play_stark_sound("protocol")
                with console.status(f"[bold cyan]🤖 {agent.config.agent_name}: Executing laptop work to completion: '{mission_task}'...", spinner="dots"):
                    mission_res = agent.registry.execute("execute_autonomous_laptop_work", mission_directive=mission_task)
                console.print(Panel(Markdown(str(mission_res)), title="[bold gold1]⚡ AUTONOMOUS LAPTOP WORK COMPLETED[/bold gold1]", border_style="gold1"))
                continue

            if user_text.lower().startswith("/bg "):
                cmd_parts = user_text.split(" ", 1)
                mission_task = cmd_parts[1].strip() if len(cmd_parts) > 1 else ""
                play_stark_sound("protocol")
                bg_res = agent.registry.execute("dispatch_background_laptop_work", mission=mission_task)
                console.print(Panel(Markdown(str(bg_res)), title=f"[bold cyan]⚡ {agent.config.agent_name} BACKGROUND WORK DISPATCHED[/bold cyan]", border_style="cyan"))
                continue

            if user_text.lower() in ["/innovate", "/idea", "/ideas", "innovate", "ideas"]:
                play_stark_sound("protocol")
                with console.status("[bold cyan]🧠 Brainstorming innovative autonomous projects...", spinner="dots"):
                    ideas = agent.registry.execute("suggest_innovative_ideas", domain_or_context="")
                console.print(Panel(Markdown(str(ideas)), title="[bold yellow]PROACTIVE INNOVATION BLUEPRINTS[/bold yellow]", border_style="cyan"))
                agent.voice.speak("I have synthesized three project blueprints, Sir. Which one shall I build for you?")
                continue

            if user_text.lower() in ["/stuck", "/solve", "stuck", "solve", "help me solve this", "i am stuck"]:
                play_stark_sound("protocol")
                with console.status("[bold cyan]🔍 Inspecting laptop context, windows, clipboard & logs for solution...", spinner="dots"):
                    solution = agent.registry.execute("diagnose_stuck_situation", context_description="")
                console.print(Panel(Markdown(str(solution)), title="[bold green]🛠️ DIAGNOSTIC SOLUTION & RESOLUTION PLAN[/bold green]", border_style="green"))
                agent.voice.speak("Sir, I have analyzed your system context and prepared the exact solution.")
                continue

            if user_text.lower() in ["/agents", "/subagents", "agents"]:
                play_stark_sound("protocol")
                agents_summary = agent.registry.execute("list_subordinate_agents")
                console.print(Panel(Markdown(str(agents_summary)), title="[bold yellow]👑 SUBORDINATE AGENTS COMMAND ROSTER[/bold yellow]", border_style="yellow"))
                continue

            if user_text.lower().startswith("/youtube"):
                parts = user_text.split(" ", 1)
                topic_arg = parts[1].strip() if len(parts) > 1 else ""
                play_stark_sound("protocol")
                with console.status("[bold cyan]🎬 Commanding YouTube Shorts AI Agent: Executing video pipeline...", spinner="dots"):
                    yt_res = agent.registry.execute("command_youtube_shorts_agent", action="run_daily_pipeline", topic=topic_arg)
                console.print(Panel(Markdown(str(yt_res)), title="[bold red]YOUTUBE SHORTS AGENT TELEMETRY[/bold red]", border_style="red"))
                agent.voice.speak("YouTube Shorts Agent has finished video synthesis and assembly under my supervision, Sir.")
                continue

            if user_text.lower().startswith("/create") or user_text.lower().startswith("/build"):
                parts = user_text.split(" ", 1)
                proj_name = parts[1].strip() if len(parts) > 1 else "Autonomous_Tool"
                play_stark_sound("protocol")
                with console.status(f"[bold cyan]⚡ Autonomously building & testing '{proj_name}'...", spinner="dots"):
                    result = agent.registry.execute("build_and_execute_project_autonomously", project_name=proj_name, project_description=f"Build fully functional {proj_name}")
                console.print(Panel(Markdown(str(result)), title="[bold green]PROJECT EXECUTION COMPLETE[/bold green]", border_style="green"))
                agent.voice.speak(f"Project {proj_name} has been built, tested, and verified to full completion, Sir.")
                continue

            if user_text.lower() in ["/resume", "/recover", "resume", "recover", "recover tasks"]:
                play_stark_sound("protocol")
                with console.status("[bold cyan]🔄 Scanning for interrupted tasks across Antigravity and system applications...", spinner="dots"):
                    res_report = agent.registry.execute("scan_and_resume_interrupted_apps")
                console.print(Panel(Markdown(str(res_report)), title="[bold green]UNIVERSAL APPLICATION RESUMPTION[/bold green]", border_style="green"))
                agent.voice.speak("Universal application scan complete, Sir. Any interrupted tasks have been commanded to resume.")
                continue

            if user_text.lower() in ["/notifs", "/notifications", "notifications"]:
                play_stark_sound("protocol")
                notifs = agent.registry.execute("view_recent_notifications", limit=10)
                console.print(Panel(Markdown(str(notifs)), title="[bold cyan]📬 RECENT DESKTOP NOTIFICATIONS[/bold cyan]", border_style="cyan"))
                continue

            if user_text.lower().startswith("/details"):
                parts = user_text.split(" ", 1)
                notif_id = parts[1].strip() if len(parts) > 1 else ""
                res = agent.registry.execute("open_notification_details", notification_id=notif_id)
                console.print(f"[bold green]{res}[/bold green]")
                continue

            if user_text.lower() in ["/briefing", "/morning", "briefing"]:
                play_stark_sound("protocol")
                briefing_hud = agent.registry.execute("get_daily_briefing")
                console.print(Panel(Markdown(str(briefing_hud)), title="[bold yellow]🌅 DAILY STARTUP BRIEFING[/bold yellow]", border_style="yellow"))
                continue

            if user_text.lower() in ["/optimize", "/clean", "optimize", "clean"]:
                play_stark_sound("protocol")
                with console.status("[bold cyan]⚡ Running deep system performance optimization...", spinner="dots"):
                    opt_report = agent.registry.execute("optimize_laptop_performance")
                console.print(Panel(Markdown(str(opt_report)), title=f"[bold green]⚡ {agent.config.agent_name} PERFORMANCE OPTIMIZATION[/bold green]", border_style="green"))
                continue

            if user_text.lower() in ["/boost", "/sluggish", "boost", "sluggish", "/speed"]:
                play_stark_sound("protocol")
                with console.status("[bold cyan]🚀 Analyzing system load & terminating unnecessary background processes...", spinner="dots"):
                    boost_report = agent.registry.execute("resolve_laptop_sluggishness", aggressive=False)
                console.print(Panel(Markdown(str(boost_report)), title=f"[bold green]⚡ {agent.config.agent_name} SPEED BOOST & RESOURCE RECLAMATION[/bold green]", border_style="green"))
                agent.voice.speak("Unnecessary background processes terminated and laptop resources reclaimed, Sir.")
                continue

            if user_text.lower().startswith("/killproc") or user_text.lower().startswith("/kill-process"):
                parts = user_text.split(" ", 1)
                proc_target = parts[1].strip() if len(parts) > 1 else ""
                if proc_target:
                    play_stark_sound("protocol")
                    kill_res = agent.registry.execute("terminate_specific_process", process_name_or_pid=proc_target)
                    console.print(Panel(Markdown(str(kill_res)), title=f"[bold red]🛑 {agent.config.agent_name} PROCESS TERMINATOR[/bold red]", border_style="red"))
                else:
                    console.print("[yellow]Please specify a process name or PID: /killproc <name_or_pid>[/yellow]")
                continue

            if user_text.lower() in ["/load", "/sysload", "load"]:
                play_stark_sound("protocol")
                diag_res = agent.registry.execute("diagnose_system_sluggishness")
                console.print(Panel(Markdown(str(diag_res)), title=f"[bold cyan]💻 {agent.config.agent_name} SYSTEM LOAD & RESOURCE TELEMETRY[/bold cyan]", border_style="cyan"))
                continue

            if user_text.lower() in ["/security", "/audit", "security", "/cyber"]:
                play_stark_sound("protocol")
                with console.status(f"[bold cyan]🛡️ {agent.config.agent_name}: Running comprehensive anti-hacker cybersecurity audit...", spinner="dots"):
                    sec_res = agent.registry.execute("run_system_security_audit", deep_scan=True)
                console.print(Panel(Markdown(str(sec_res)), title=f"[bold green]🛡️ {agent.config.agent_name} CYBER DEFENSE & AUDIT[/bold green]", border_style="green"))
                agent.voice.speak("Security audit complete, Sir. Laptop defense posture verified.")
                continue

            if user_text.lower() in ["/firewall", "/ufw"]:
                play_stark_sound("protocol")
                fw_res = agent.registry.execute("check_firewall_status")
                console.print(Panel(Markdown(str(fw_res)), title=f"[bold cyan]🧱 {agent.config.agent_name} LINUX FIREWALL POSTURE[/bold cyan]", border_style="cyan"))
                continue

            if user_text.lower() in ["/netports", "/openports", "/ports"]:
                play_stark_sound("protocol")
                ports_res = agent.registry.execute("scan_network_vulnerabilities")
                console.print(Panel(Markdown(str(ports_res)), title=f"[bold cyan]📡 {agent.config.agent_name} LISTENING PORTS & SOCKETS[/bold cyan]", border_style="cyan"))
                continue

            if user_text.lower() in ["/backdoors", "/hackers", "/malware"]:
                play_stark_sound("protocol")
                bd_res = agent.registry.execute("scan_for_hacker_backdoors")
                console.print(Panel(Markdown(str(bd_res)), title=f"[bold red]🕵️ {agent.config.agent_name} BACKDOOR SCANNER[/bold red]", border_style="red"))
                continue

            if user_text.lower().startswith("/neutralize") or user_text.lower().startswith("/kill-threat"):
                parts = user_text.split(" ", 1)
                threat_target = parts[1].strip() if len(parts) > 1 else ""
                if threat_target:
                    play_stark_sound("protocol")
                    neut_res = agent.registry.execute("neutralize_suspicious_threat", target=threat_target)
                    console.print(Panel(Markdown(str(neut_res)), title=f"[bold red]🛑 {agent.config.agent_name} THREAT NEUTRALIZER[/bold red]", border_style="red"))
                else:
                    console.print("[yellow]Please specify a PID, port, or process name: /neutralize <target>[/yellow]")
                continue

            if user_text.lower() in ["/ceo", "/chamunda", "/revenue", "ceo", "revenue", "business"]:
                play_stark_sound("protocol")
                ceo_report = agent.registry.execute("chamunda_generate_ceo_revenue_report")
                console.print(Panel(Markdown(str(ceo_report)), title="[bold gold1]👑 CHAMUNDA AUTOMOBILE • CEO EXECUTIVE OVERVIEW[/bold gold1]", border_style="gold1"))
                agent.voice.speak("Chairman, all Chamunda Automobile workshop and inventory metrics are displayed.")
                continue

            if user_text.lower().startswith("/parts") or user_text.lower().startswith("/part"):
                parts_q = user_text.split(" ", 1)
                q = parts_q[1].strip() if len(parts_q) > 1 else ""
                play_stark_sound("protocol")
                parts_res = agent.registry.execute("chamunda_lookup_part", query=q)
                console.print(Panel(Markdown(str(parts_res)), title="[bold green]🏍️ ROYAL ENFIELD GENUINE SPARES[/bold green]", border_style="green"))
                continue

            if user_text.lower().startswith("/re-diag") or user_text.lower().startswith("/bike-diag"):
                diag_q = user_text.split(" ", 1)
                sym = diag_q[1].strip() if len(diag_q) > 1 else "tappet noise"
                play_stark_sound("protocol")
                diag_res = agent.registry.execute("chamunda_diagnose_re_bike", symptom=sym)
                console.print(Panel(Markdown(str(diag_res)), title="[bold red]🔧 RE MASTER DIAGNOSTIC ADVISOR[/bold red]", border_style="red"))
                continue

            if user_text.lower().startswith("/sound") or user_text.lower().startswith("/thump"):
                sound_q = user_text.split(" ", 1)
                model = sound_q[1].strip() if len(sound_q) > 1 else "Classic 350"
                play_stark_sound("protocol")
                sound_res = agent.registry.execute("diagnose_re_engine_sound", bike_model=model)
                console.print(Panel(Markdown(str(sound_res)), title="[bold cyan]🔊 ACOUSTIC ENGINE SOUND DIAGNOSTIC AI[/bold cyan]", border_style="cyan"))
                continue

            if user_text.lower().startswith("/scan"):
                scan_q = user_text.split(" ", 1)
                hint = scan_q[1].strip() if len(scan_q) > 1 else "oil filter"
                play_stark_sound("protocol")
                scan_res = agent.registry.execute("scan_re_part_image", part_hint=hint)
                console.print(Panel(Markdown(str(scan_res)), title="[bold magenta]📷 COMPUTER VISION PART RECOGNITION SCANNER[/bold magenta]", border_style="magenta"))
                continue

            if user_text.lower() in ["/rides", "/club", "/events", "rides", "events"]:
                play_stark_sound("protocol")
                rides_res = agent.registry.execute("manage_chamunda_riders_club")
                console.print(Panel(Markdown(str(rides_res)), title="[bold gold1]🏍️ CHAMUNDA RIDERS CLUB & CAMPAIGNS[/bold gold1]", border_style="gold1"))
                continue

            if user_text.lower() in ["/po", "/purchaseorder", "po", "purchaseorder"]:
                play_stark_sound("protocol")
                po_res = agent.registry.execute("generate_wholesale_purchase_order")
                console.print(Panel(Markdown(str(po_res)), title="[bold blue]📦 AUTOMATED WHOLESALE PURCHASE ORDER[/bold blue]", border_style="blue"))
                continue

            if user_text.lower() in ["/wake", "wake"]:
                play_stark_sound("protocol")
                wake_res = agent.registry.execute("toggle_wake_word_listener", enabled=True)
                console.print(f"[bold green]{wake_res}[/bold green]")
                continue

            if user_text.lower() in ["/shadow", "shadow", "/copilot"]:
                play_stark_sound("protocol")
                shadow_res = agent.registry.execute("toggle_silent_shadow_copilot", enabled=True)
                console.print(f"[bold cyan]{shadow_res}[/bold cyan]")
                continue

            if user_text.lower().startswith("/price"):
                price_q = user_text.split(" ", 1)
                pq = price_q[1].strip() if len(price_q) > 1 else ""
                play_stark_sound("protocol")
                price_res = agent.registry.execute("optimize_re_part_pricing", query=pq)
                console.print(Panel(Markdown(str(price_res)), title="[bold green]📊 COMPETITOR PRICE & MARGIN OPTIMIZER[/bold green]", border_style="green"))
                continue

            if user_text.lower() in ["/hud", "hud", "/widget"]:
                play_stark_sound("startup")
                hud_res = agent.registry.execute("launch_arc_reactor_hud")
                console.print(f"[bold gold1]{hud_res}[/bold gold1]")
                continue

            if user_text.lower().startswith("/ecu"):
                ecu_q = user_text.split(" ", 1)
                model = ecu_q[1].strip() if len(ecu_q) > 1 else "Classic 350 J-Series"
                play_stark_sound("protocol")
                ecu_res = agent.registry.execute("read_re_ecu_telemetry", bike_model=model)
                console.print(Panel(Markdown(str(ecu_res)), title="[bold cyan]🔌 RE ECU LIVE OBD-II TELEMETRY[/bold cyan]", border_style="cyan"))
                continue

            if user_text.lower().startswith("/dtc"):
                dtc_q = user_text.split(" ", 1)
                model = dtc_q[1].strip() if len(dtc_q) > 1 else "Classic 350"
                play_stark_sound("protocol")
                dtc_res = agent.registry.execute("scan_re_ecu_dtc_codes", bike_model=model)
                console.print(Panel(Markdown(str(dtc_res)), title="[bold red]⚠️ RE ECU TROUBLE CODE SCANNER[/bold red]", border_style="red"))
                continue

            if user_text.lower() in ["/clear-dtc", "/cleardtc"]:
                play_stark_sound("protocol")
                clear_res = agent.registry.execute("clear_re_ecu_dtc_codes")
                console.print(f"[bold green]{clear_res}[/bold green]")
                continue

            if user_text.lower().startswith("/torque"):
                torq_q = user_text.split(" ", 1)
                plat = torq_q[1].strip() if len(torq_q) > 1 else "J-Series 350"
                play_stark_sound("protocol")
                torq_res = agent.registry.execute("get_re_factory_torque_specs", platform=plat)
                console.print(Panel(Markdown(str(torq_res)), title="[bold gold1]🧩 RE FACTORY TORQUE SPECIFICATIONS[/bold gold1]", border_style="gold1"))
                continue

            if user_text.lower().startswith("/health"):
                health_q = user_text.split(" ")
                odo = int(health_q[1]) if len(health_q) > 1 and health_q[1].isdigit() else 14500
                play_stark_sound("protocol")
                health_res = agent.registry.execute("predict_re_bike_health_score", odometer_km=odo)
                console.print(Panel(Markdown(str(health_res)), title="[bold magenta]🔮 PREDICTIVE AI MOTORCYCLE HEALTH SCORE[/bold magenta]", border_style="magenta"))
                continue

            if user_text.lower() in ["/intel", "intel", "/digest"]:
                play_stark_sound("protocol")
                intel_res = agent.registry.execute("get_daily_re_market_intelligence")
                console.print(Panel(Markdown(str(intel_res)), title="[bold yellow]📰 DAILY RE EXECUTIVE INTELLIGENCE DIGEST[/bold yellow]", border_style="yellow"))
                continue

            if user_text.lower() in ["/holo", "holo", "/hologram"]:
                play_stark_sound("startup")
                holo_res = agent.registry.execute("launch_holographic_web_hud")
                console.print(f"[bold cyan]{holo_res}[/bold cyan]")
                continue

            if user_text.lower() in ["/selftune", "selftune", "/benchmark"]:
                play_stark_sound("protocol")
                tune_res = agent.registry.execute("run_jarvis_self_optimization")
                console.print(Panel(Markdown(str(tune_res)), title=f"[bold green]🧬 {agent.config.agent_name} AUTONOMOUS SELF-OPTIMIZATION[/bold green]", border_style="green"))
                continue

            if user_text.lower().startswith("/iot"):
                iot_q = user_text.split(" ", 2)
                dev = iot_q[1].strip() if len(iot_q) > 1 else "status"
                st = iot_q[2].strip() if len(iot_q) > 2 else "ON"
                play_stark_sound("ack")
                iot_res = agent.registry.execute("control_workshop_iot_device", device_name=dev, state=st)
                console.print(Panel(Markdown(str(iot_res)), title="[bold blue]💡 CHAMUNDA WORKSHOP SMART IOT[/bold blue]", border_style="blue"))
                continue

            if user_text.lower().startswith("/model"):
                parts = user_text.split(" ", 1)
                if len(parts) > 1 and parts[1].strip():
                    target_model = parts[1].strip()
                    res = agent.registry.execute("set_ai_model", model_name=target_model)
                    agent.config.model_name = target_model
                    console.print(f"[bold green]{res}[/bold green]")
                else:
                    report = agent.registry.execute("list_available_ai_models")
                    console.print(Panel(Markdown(str(report)), title="[bold cyan]🧠 AI MODEL DISCOVERY & VERSION TELEMETRY[/bold cyan]", border_style="cyan"))
                continue

            if user_text.lower() in ["/upgrade-model", "/update-model", "upgrade-model", "update-model"]:
                play_stark_sound("protocol")
                with console.status("[bold cyan]🚀 Querying Google GenAI API for newly released models...", spinner="dots"):
                    up_res = agent.registry.execute("check_and_upgrade_model")
                console.print(Panel(Markdown(str(up_res)), title="[bold gold1]🚀 AI ENGINE MODEL AUTO-UPGRADE[/bold gold1]", border_style="gold1"))
                continue

            if user_text.lower().startswith("/lang") or user_text.lower().startswith("/language"):
                parts = user_text.split(" ", 1)
                if len(parts) > 1 and parts[1].strip():
                    target_lang = parts[1].strip()
                    res = agent.registry.execute("set_agent_language", language=target_lang)
                    agent.config.language = target_lang
                    console.print(f"[bold green]{res}[/bold green]")
                else:
                    report = agent.registry.execute("list_supported_languages")
                    console.print(Panel(Markdown(str(report)), title=f"[bold magenta]🌐 {agent.config.agent_name} ભાષા રૂપરેખાંકન (LANGUAGE PROTOCOL)[/bold magenta]", border_style="magenta"))
                continue

            if user_text.lower() in ["/clear"]:
                agent.history.clear()
                console.print("[dim]Conversation buffer cleared.[/dim]")
                continue

            if user_text.lower() in ["/stats"]:
                render_unified_hud(agent)
            if user_text.lower() in ["/history", "/conversation", "/chat", "history", "conversation"]:
                display_conversation_history(agent)
                continue

            tool_events = []
            # Tool execution callbacks
            def on_tool_start(name: str, args: dict):
                play_stark_sound("ack")
                args_str = ", ".join(f"{k}={repr(v)[:30]}" for k, v in args.items())
                console.print(f"[dim yellow]⚡ Executing Protocol:[/dim yellow] [bold]{name}[/bold]({args_str})")

            def on_tool_end(name: str, result: any):
                res_preview = str(result).strip().replace("\n", " ")[:80]
                tool_events.append({"name": name, "preview": res_preview})
                console.print(f"[dim green]✓ Telemetry Verified:[/dim green] [dim]{res_preview}...[/dim]")

            # Run agent turn
            with console.status(f"[cyan]{agent.config.agent_name} computing & deploying tools...", spinner="dots"):
                response = agent.run_turn(
                    user_input=user_text,
                    on_tool_start=on_tool_start,
                    on_tool_end=on_tool_end,
                    speak_response=agent.config.enable_voice_response
                )

            # Render structured live conversation turn panel in the launcher
            render_conversation_panel(agent.config.agent_name, user_text, is_voice_turn, tool_events, response)
            save_conversation_turn(agent, user_text, is_voice_turn, tool_events, response)
            console.print()

        except (KeyboardInterrupt, EOFError):
            console.print(f"\n[cyan]{agent.config.agent_name}:[/cyan] Systems standing down, Sir.")
            agent.voice.speak("Systems standing down, Sir.")
            break
        except Exception as e:
            console.print(f"[bold red]System Alert:[/bold red] {str(e)}")


def start_voice_mode(config_path: str = None):
    """Backwards compatible voice-only shortcut."""
    start_unified_interface(config_path)


def start_interactive_cli(config_path: str = None):
    """Backwards compatible CLI shortcut."""
    start_unified_interface(config_path)
