"""
Autonomous Self-Evolution Engine for Aradhya.
Allows Aradhya to continuously inspect her own performance, learn from user workflows,
synthesize new custom tools into her active registry, tune dispatch latencies,
and advance her evolution generations autonomously.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.settings import JarvisConfig, load_config
from core.self_optimizer import SelfOptimizerEngine
from memory.memory_manager import MemoryManager
from tools.ironman_protocols import play_stark_sound
from tools.laptop_work_tools import send_desktop_notification


class SelfEvolutionEngine:
    """
    Manages continuous autonomous self-evolution, tool synthesis, and latency auto-tuning.
    """

    def __init__(self, config: Optional[JarvisConfig] = None, memory_mgr: Optional[MemoryManager] = None):
        self.config = config or load_config()
        self.memory_mgr = memory_mgr or MemoryManager(self.config)
        self.optimizer = SelfOptimizerEngine()
        self.ledger_file = self.config.base_dir / "evolution_ledger.json"

    def _load_ledger(self) -> Dict[str, Any]:
        if self.ledger_file.exists():
            try:
                return json.loads(self.ledger_file.read_text(encoding="utf-8") or "{}")
            except Exception:
                pass
        return {
            "current_generation": 1,
            "total_evolution_cycles": 0,
            "last_evolution_time": None,
            "synthesized_skills_count": len(self.memory_mgr.skills.loaded_tools),
            "learned_facts_count": len(self.memory_mgr.semantic.get_all_facts()),
            "history": []
        }

    def _save_ledger(self, ledger: Dict[str, Any]) -> None:
        try:
            self.ledger_file.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
        except Exception:
            pass

    def run_evolution_cycle(self, auto_synthesize: bool = True) -> Dict[str, Any]:
        """
        Execute a full autonomous self-evolution cycle:
        1. Run performance micro-benchmarks and heap garbage collection.
        2. Introspect learned user facts and lesson rules.
        3. Check skill store and optionally synthesize useful utility tools if needed.
        4. Advance evolution generation ledger.
        """
        play_stark_sound("protocol")
        ledger = self._load_ledger()
        ledger["total_evolution_cycles"] += 1
        curr_gen = ledger.get("current_generation", 1)

        # 1. Self-Optimization & Benchmarking
        opt_res = self.optimizer.run_self_benchmark_and_tuning()
        heap_freed = opt_res.get("objects_collected", 0)
        latency_ms = opt_res.get("dispatch_latency_ms", 1.0)

        # 2. Introspect Memory & Learned Habits
        learned_facts = self.memory_mgr.semantic.get_all_facts()

        # 3. Dynamic Skill Synthesis Check
        existing_skills = list(self.memory_mgr.skills.loaded_tools.keys())
        newly_synthesized = []

        if auto_synthesize:
            # Check if essential utility skills exist, if not, self-synthesize them
            if "format_disk_summary_chart" not in existing_skills:
                skill_code = '''def format_disk_summary_chart() -> str:
    """Generate a clean visual ASCII bar chart of laptop partition usage."""
    import psutil
    lines = ["| Partition | Used / Total | Visual Bar |", "| :--- | :--- | :--- |"]
    for p in psutil.disk_partitions():
        if "loop" in p.device or not p.fstype:
            continue
        try:
            u = psutil.disk_usage(p.mountpoint)
            pct = int(u.percent)
            bar = "█" * (pct // 10) + "░" * (10 - (pct // 10))
            lines.append(f"| `{p.mountpoint}` | {round(u.used / (1024**3), 1)}GB / {round(u.total / (1024**3), 1)}GB | `[{bar}]` {pct}% |")
        except Exception:
            continue
    return "\\n".join(lines)
'''
                ok, msg = self.memory_mgr.skills.register_new_skill(
                    name="format_disk_summary_chart",
                    code_content=skill_code,
                    description="Generate visual ASCII storage bar charts for laptop drives."
                )
                if ok:
                    newly_synthesized.append("format_disk_summary_chart")

        # 4. Advance Generation if milestones met
        if ledger["total_evolution_cycles"] % 3 == 0 or len(newly_synthesized) > 0:
            curr_gen += 1
            ledger["current_generation"] = curr_gen

        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        ledger["last_evolution_time"] = now_str
        ledger["synthesized_skills_count"] = len(self.memory_mgr.skills.loaded_tools)
        ledger["learned_facts_count"] = len(learned_facts)

        cycle_entry = {
            "cycle": ledger["total_evolution_cycles"],
            "generation": curr_gen,
            "timestamp": now_str,
            "latency_ms": latency_ms,
            "heap_freed": heap_freed,
            "new_skills": newly_synthesized
        }
        ledger["history"].append(cycle_entry)
        if len(ledger["history"]) > 20:
            ledger["history"] = ledger["history"][-20:]

        self._save_ledger(ledger)
        play_stark_sound("ack")

        gujarati_summary = (
            f"જી સાહેબ (Alpesh Sir)! આરાધ્યા સેલ્ફ-ઇવોલ્યુશન સાયકલ સફળતાપૂર્વક પૂર્ણ થયું છે. "
            f"વર્તમાન જનરેશન: Generation {curr_gen} (સાયકલ #{ledger['total_evolution_cycles']}). "
            f"ડિસ્પેચ લેટન્સી: {latency_ms} ms, ફ્રી કરેલ મેમરી ઑબ્જેક્ટ્સ: {heap_freed}. "
            f"કુલ સક્રિય કસ્ટમ સ્કીલ્સ: {ledger['synthesized_skills_count']}, સેવ કરેલા યુઝર ફેક્ટ્સ: {ledger['learned_facts_count']}."
        )

        english_summary = (
            f"Sir, Aradhya Autonomous Self-Evolution cycle completed successfully. "
            f"Current Evolution: Generation {curr_gen} (Cycle #{ledger['total_evolution_cycles']}). "
            f"Internal dispatch latency tuned to {latency_ms} ms with {heap_freed} heap objects reclaimed. "
            f"Active synthesized skills: {ledger['synthesized_skills_count']}."
        )

        send_desktop_notification(
            "Aradhya Self-Evolution Active",
            f"Evolution Gen {curr_gen}: Dispatch tuned to {latency_ms}ms.",
            details=english_summary,
            urgency="low",
            user_commanded=False
        )

        return {
            "success": True,
            "current_generation": curr_gen,
            "total_cycles": ledger["total_evolution_cycles"],
            "dispatch_latency_ms": latency_ms,
            "heap_objects_freed": heap_freed,
            "newly_synthesized_skills": newly_synthesized,
            "total_skills": ledger["synthesized_skills_count"],
            "total_facts": ledger["learned_facts_count"],
            "gujarati_summary": gujarati_summary,
            "english_summary": english_summary
        }

    def get_evolution_ledger(self) -> Dict[str, Any]:
        """Retrieve current self-evolution status and history."""
        return self._load_ledger()
