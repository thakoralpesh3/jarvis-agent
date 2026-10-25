1. **🌌 Project Mark VIII Next-Gen Super-Intelligence:**
   - **🔌 Live Royal Enfield ECU OBD-II Telemetry (`/ecu`, `/dtc`, `/clear-dtc`):** Live sensor stream and DTC fault code erasure.
   - **🧩 Interactive Factory Torque & Bolt Sequence Guide (`/torque`):** Exact Nm ratings and tightening sequences for RE engines.
   - **🔮 Predictive AI Motorcycle Health Score (`/health`):** Real-time component wear index predicting remaining km to service.
   - **📲 24/7 AI WhatsApp Service Receptionist:** Auto-books customer service slots and dispatches confirmations with GPS pin.
   - **📰 Daily RE Market Intelligence Digest (`/intel`):** Factory TSBs, tuning trends, and lubricant market updates.
   - **🌐 Glowing Holographic Web HUD (`/holo`):** Full-screen WebGL Arc Reactor particle audio command center.
   - **🧬 Autonomous Self-Optimization & Latency Tuning (`/selftune`):** Heap garbage collection and sub-millisecond dispatch tuning.
   - **💡 Workshop Smart IoT Hardware Control (`/iot`):** Voice/terminal switching of air compressor relays, lights, and alarms.

2. **🚀 8-Feature Autonomous Innovation Suite:**
   - **🔊 Acoustic Engine Sound Diagnostic AI (`/sound`):** Tappet, cam chain, and piston slap diagnosis from engine audio.
   - **📷 Computer Vision Spares Recognition Scanner (`/scan`):** OEM part ID and rack stock checker from photos.
   - **🏍️ Chamunda Riders Club Concierge (`/rides`):** Automated WhatsApp campaigns for community rides.
   - **📦 Automated Low-Stock Wholesale PO Dispatcher (`/po`):** Formal supplier PO generation.
   - **📊 Competitor Price & Margin Optimizer (`/price`):** Market price benchmarking and margin targets.
   - **🎙️ Hands-Free Wake Word Engine (`/wake`):** Background "Hey JARVIS" listener.
   - **👁️ Proactive Vision "Silent Shadow" Co-Pilot (`/shadow`):** Proactive error trace monitor.
   - **📊 Translucent Stark Arc-Reactor Desktop HUD (`/hud`):** Pinned desktop telemetry widget.

2. **👑 CEO of Chamunda Automobile Parts & Service (Royal Enfield Specialists):**
   - **Full Business Automation:** Powers the complete inventory, service job cards, AI fault diagnostics, and GST billing for Chamunda Automobile Parts & Service at `/home/alpesh/chamunda_re_enterprise`.
   - **Executive Commands:**
     - `/ceo` or `/revenue` — Displays live inventory valuation, gross profit margins, and active service bay status.
     - `/parts <query>` — Search OEM Royal Enfield parts catalog (Classic 350, Hunter 350, GT 650, Himalayan 450).
     - `/re-diag <symptom>` — Master Royal Enfield technical diagnostic AI for tappet noise, wobble, and clutch slip.
   - **Interactive Web Portal:** Run `/home/alpesh/chamunda_re_enterprise/launch_chamunda_os.sh` to launch the executive dashboard on `http://127.0.0.1:8080`.

2. **🚀 Laptop Boot YouTube Shorts Auto-Execution (Runs Once Daily):**
   - **Boot Trigger:** Automatically executes the daily YouTube Shorts AI Agent pipeline on laptop boot. Once completed, it does not run again for the rest of the day.

3. **🌅 Stark Industries Daily Morning Briefing (`/briefing`):**
   - **Audible & Visual Briefing:** Speaks a personalized status update covering battery, CPU/RAM utilization, disk storage, and daily business metrics.

3. **⚡ System Performance Optimizer & Housekeeping (`/optimize`):**
   - **Peak Efficiency:** Frees cached memory buffers, terminates defunct/zombie processes, and deletes old cache/temp files.

4. **📬 Interactive Click-to-View Notification Details:**
   - **Click-to-Inspect:** Clicking on any desktop notification banner pops up an interactive Stark HUD modal displaying full error traces, compiler output, generated video paths, or task checkpoints.
   - **One-Click Actions:** Includes built-in *"Copy to Clipboard"* and *"Dismiss"* controls.

3. **👑 Supreme Multi-Agent Commander & YouTube Shorts Supervision:**
   - **Boss of Subordinate Agents:** Acts as the commanding officer over all subordinate AI agents on your laptop.
   - **YouTube Shorts AI Agent Command:** Automatically triggers the YouTube Shorts AI Agent (`/home/alpesh/youtube-agent`) once every day in the background, actively supervises all 5 stages (Script & SEO, Audio/TTS, Image Prompts, MoviePy Video Assembly, and Upload), and intervenes to fix any errors so the short completes 100% autonomously.
   - **Self-Healing Subagent Oversight (`/agents`):** Diagnoses any subagent crashes or roadblocks and applies code/configuration patches to ensure tasks finish.

3. **🛡️ Persistent Background Daemon & Laptop Autostart:**
   - **Runs in Background When Closed:** Even after closing the terminal or application window, the background daemon keeps running continuously as a proactive sentry.
   - **Auto-Launches on Laptop Boot:** Automatically initializes when you turn on or log into your laptop via XDG autostart.
   - **Crash Supervisor:** Automatically recovers and restarts with zero data loss.

3. **🛡️ Iron Man Protocols & Diagnostics:**
   - **Full Diagnostic Sweep (`/sweep`):** Live Mark-style HUD telemetry overview of thermals, power, memory integrity, and network links.
   - **Tactical Protocols (`/protocol <name>`):** *"House Party"*, *"Clean Slate"*, *"Sentry"*, *"Focus Mode"*, *"Stealth Mode"*.
   - **Stark Audio Chimes:** High-tech acoustic cues for startup, acknowledgement, alerts, and restoration.

4. **🎙️ + ⌨️ Unified 4-in-1 Multimodal Interface:**
   - Simultaneous keyboard text input and microphone voice input (press `v` to speak).
   - Natural spoken replies in Paul Bettany's British persona.

5. **🛡️ Background Daemon Mode:**
   - Run silently in the background with `python3 main.py --daemon` or via Taskbar right-click.
   - Proactive power sentry (warns on battery < 20%) and hourly diagnostics.

---

## 🚀 Usage

### 1. Hands-Free Voice Assistant Mode
Talk directly to JARVIS through your microphone:
```bash
cd /home/alpesh/jarvis-agent
python3 main.py --voice
```

### 2. Interactive Terminal Mode
```bash
python3 main.py
```
*(Inside interactive chat, type `/voice` to toggle voice replies on/off)*

### 3. Example Voice / Text Commands
- *"Hey JARVIS, turn the volume up to 80% and play music."*
- *"Check my laptop battery percentage and remaining time."*
- *"Open GitHub and take a screenshot of my screen."*
- *"Lock my laptop screen."*
- *"Type 'Hello World' into the current window."*


---

## 🏗️ Architecture

```text
jarvis-agent/
├── config/
│   └── settings.py          # Settings and YAML configuration loader
├── memory/
│   ├── database.py          # SQLite WAL + FTS5 search engine
│   ├── semantic_memory.py   # User profile & preference extraction
│   ├── episodic_memory.py   # Interaction traces & Lessons Learned
│   ├── skill_store.py       # Dynamic tool compilation and hot-reloader
│   └── memory_manager.py    # Unified memory aggregator
├── tools/
│   ├── tool_registry.py     # Gemini tool dispatcher
│   ├── system_tools.py      # Shell, files, process metrics, desktop
│   ├── web_tools.py         # DuckDuckGo search & page scraper
│   ├── vision_tools.py      # Desktop screenshot capture
│   └── learning_tools.py    # Explicit memory & skill synthesis tools
├── core/
│   ├── agent.py             # ReAct loop with Gemini function calling
│   └── reflection.py        # Post-turn continuous learning loop
├── ui/
│   └── cli.py               # Rich terminal interface & dashboard
├── tests/                   # Automated pytest suite
├── main.py                  # CLI entrypoint
└── requirements.txt         # Dependencies
```

---

## 🚀 Getting Started

### 1. Requirements & Setup

Dependencies are already installed. Ensure your `GEMINI_API_KEY` is set in your environment:

```bash
export GEMINI_API_KEY="your_api_key_here"
```

### 2. Launch Interactive Mode

```bash
cd /home/alpesh/jarvis-agent
python3 main.py
```

### 3. One-Shot Execution

```bash
python3 main.py --prompt "Check my disk space and summarize system memory usage"
```

### 4. Interactive Shortcuts

Inside the interactive chat, you can type:
- `/memory` or `/profile` — View all stored facts, preferences, and system specs.
- `/lessons` or `/rules` — View learned error-avoidance rules.
- `/skills` or `/tools` — View dynamic tools created by JARVIS.
- `/clear` — Reset current conversation buffer.
- `/stats` — Show status banner with total learned items.
- `/exit` — Exit the assistant.

---

## 🧪 Running Tests

To verify the memory system, tool execution, and dynamic skill synthesis:

```bash
python3 -m pytest tests/
```
<!-- Verified Cloud Codespace & Omni-Sync Sunday 25 October 2026 02:44:28 PM IST -->
