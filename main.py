#!/usr/bin/env python3
"""
JARVIS: Unified Mark VII Autonomous AI Assistant.
Combines Chat, Voice, Laptop & Browser Automation, Memory, and Background Daemon into a single seamless interface.
"""

import sys
import argparse
from pathlib import Path

# Add jarvis-agent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from config.settings import load_config, save_config, JarvisConfig
from core.agent import JarvisAgent
from core.daemon import JarvisDaemon
from ui.cli import (
    start_unified_interface,
    display_memory_table,
    display_lessons_table,
    display_skills_table,
)


def main():
    parser = argparse.ArgumentParser(description="JARVIS: Unified AI Assistant with Full Laptop Control, Voice & Memory")
    parser.add_argument("-c", "--config", type=str, help="Path to custom config.yaml")
    parser.add_argument("-p", "--prompt", type=str, help="Execute a one-shot instruction and exit")
    parser.add_argument("-v", "--voice", action="store_true", help="Launch in Unified Voice Mode")
    parser.add_argument("-d", "--daemon", "--background", action="store_true", help="Run JARVIS continuously in the background")
    parser.add_argument("--stop", action="store_true", help="Stop the running background daemon")
    parser.add_argument("--status", action="store_true", help="Check status of the background daemon")
    parser.add_argument("--logs", action="store_true", help="View recent background daemon logs")
    parser.add_argument("--memory", action="store_true", help="Display all learned facts and user profile")
    parser.add_argument("--lessons", action="store_true", help="Display all learned self-correction rules")
    parser.add_argument("--skills", action="store_true", help="Display all synthesized dynamic skills")
    parser.add_argument("--init-config", action="store_true", help="Create default configuration file")

    args = parser.parse_args()

    if args.init_config:
        cfg = JarvisConfig()
        save_config(cfg)
        print(f"JARVIS default configuration saved to {cfg.base_dir / 'config.yaml'}")
        return

    config = load_config(args.config)
    daemon = JarvisDaemon(config)

    if args.daemon:
        print(daemon.start(daemonize=True))
        return

    if args.stop:
        print(daemon.stop())
        return

    if args.status:
        print(daemon.status())
        return

    if args.logs:
        print(daemon.get_logs(30))
        return

    if args.memory:
        agent = JarvisAgent(config)
        display_memory_table(agent)
        return

    if args.lessons:
        agent = JarvisAgent(config)
        display_lessons_table(agent)
        return

    if args.skills:
        agent = JarvisAgent(config)
        display_skills_table(agent)
        return

    if args.prompt:
        agent = JarvisAgent(config)
        res = agent.run_turn(args.prompt)
        print(f"\nJARVIS: {res}\n")
        return

    # Default to the Unified 4-in-1 Interface
    start_unified_interface(args.config)


if __name__ == "__main__":
    main()
