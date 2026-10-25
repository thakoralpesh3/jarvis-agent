#!/usr/bin/env bash
# ==============================================================================
# Aradhya Laptop Boot Autostart Orchestrator
# Executes on laptop startup:
# 1. Delivers Morning/Daily Briefing (audio & interactive HUD notification).
# 2. Runs Daily YouTube Shorts AI Agent in background if due (only runs once a day).
# 3. Launches the unified Aradhya interface.
# ==============================================================================

sleep 3
cd /home/alpesh/jarvis-agent || exit 1
export DISPLAY="${DISPLAY:-:0}"
export XAUTHORITY="${XAUTHORITY:-$HOME/.Xauthority}"

# 1. Run Daily YouTube Shorts pipeline quietly in background if due for today
python3 -c "
from core.youtube_commander import YouTubeShortsCommander

yt = YouTubeShortsCommander()
if yt.is_daily_run_due():
    import threading
    t = threading.Thread(target=yt.run_and_supervise_pipeline, daemon=False)
    t.start()
" >/dev/null 2>&1 &

# 2. Launch Aradhya Unified Interface in styled terminal
gnome-terminal --title="Aradhya AI Assistant" --geometry=110x32 -- /home/alpesh/jarvis-agent/launch_jarvis.sh
