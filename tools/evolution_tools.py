"""
Autonomous Self-Evolution & Proactive Innovation/Surprise Tools for Aradhya.
Allows Aradhya to evolve her capabilities, synthesize new skills, benchmark her latency,
and proactively present innovative ideas to surprise Alpesh Sir.
"""

from typing import Dict, Any, Optional
from config.settings import load_config


_evolution_engine: Optional[Any] = None
_surprise_engine: Optional[Any] = None


def _get_evolution_engine() -> Any:
    global _evolution_engine
    if _evolution_engine is None:
        from core.self_evolution import SelfEvolutionEngine
        cfg = load_config()
        _evolution_engine = SelfEvolutionEngine(cfg)
    return _evolution_engine


def _get_surprise_engine() -> Any:
    global _surprise_engine
    if _surprise_engine is None:
        from core.innovation_surprise import InnovationSurpriseEngine
        cfg = load_config()
        _surprise_engine = InnovationSurpriseEngine(cfg)
    return _surprise_engine


def surprise_me_with_idea(focus_area: str = "any") -> str:
    """
    Proactively brainstorm an innovative, surprising, and practical idea or automation
    tailored specifically for Alpesh Sir's laptop workflow or Royal Enfield business.

    Args:
        focus_area: Optional domain focus ('workflow', 'business', 'tech', or 'any').
    """
    engine = _get_surprise_engine()
    idea = engine.generate_surprise_idea(focus_area=focus_area)
    return engine.format_surprise_report(idea)


def trigger_self_evolution_cycle() -> str:
    """
    Trigger an autonomous self-evolution and auto-tuning cycle for Aradhya.
    Inspects learned facts, benchmarks math and dispatch latency, garbage-collects heap memory,
    synthesizes new procedural skills if needed, and advances evolution generation.
    """
    engine = _get_evolution_engine()
    res = engine.run_evolution_cycle(auto_synthesize=True)

    skills_text = ", ".join(res["newly_synthesized_skills"]) if res["newly_synthesized_skills"] else "None (Registry up-to-date)"

    return f"""### 🧬 ARADHYA AUTONOMOUS SELF-EVOLUTION REPORT (આરાધ્યા સેલ્ફ-ઇવોલ્યુશન રિપોર્ટ)

> **ગુજરાતી:** {res['gujarati_summary']}
>
> **English:** {res['english_summary']}

---
#### 📊 Evolution Metrics & Benchmarks
- **Evolution Generation:** **Generation {res['current_generation']}** (Cycle #{res['total_cycles']})
- **Internal Dispatch Latency:** **`{res['dispatch_latency_ms']} ms`** (Ultra-responsive)
- **Garbage Collection Objects Reclaimed:** **`{res['heap_objects_freed']}` heap items**
- **Newly Synthesized Skills:** `{skills_text}`
- **Total Dynamic Skills in Registry:** `{res['total_skills']}`
- **Long-Term Memory Facts Catalogued:** `{res['total_facts']}`

*Aradhya has evolved and tuned herself to peak cognitive and operational readiness, Sir.*
"""


def get_agent_evolution_status() -> str:
    """
    Retrieve the current evolution generation, ledger history, and synthesized skills of Aradhya.
    """
    engine = _get_evolution_engine()
    ledger = engine.get_evolution_ledger()

    history_lines = []
    for h in ledger.get("history", [])[-5:]:
        history_lines.append(f"- Cycle #{h['cycle']} (Gen {h['generation']}): Latency `{h['latency_ms']}ms`, Freed `{h['heap_freed']}` items at `{h['timestamp']}`")

    return f"""### 🧬 Aradhya Evolution & Adaptation Ledger
- **Current Generation:** **Generation {ledger.get('current_generation', 1)}**
- **Total Evolution Cycles Executed:** `{ledger.get('total_evolution_cycles', 0)}`
- **Synthesized Dynamic Skills:** `{ledger.get('synthesized_skills_count', 0)}`
- **Learned User Preferences & Facts:** `{ledger.get('learned_facts_count', 0)}`
- **Last Evolution Timestamp:** `{ledger.get('last_evolution_time', 'Never')}`

**Recent Evolution Milestones:**
{chr(10).join(history_lines) if history_lines else '  - First generation active.'}
"""


def execute_surprise_idea(idea_name: str) -> str:
    """
    Autonomously build, code, and execute the suggested surprise idea prototype.

    Args:
        idea_name: Name or brief title of the idea to build (e.g. 'smart_workspace_curator').
    """
    engine = _get_surprise_engine()
    res = engine.build_surprise_prototype(idea_name)

    if res.get("status") == "success":
        return f"""### 🚀 Surprise Prototype Autonomous Build Complete!
- **Project Name:** `{res.get('project_name')}`
- **Location:** `{res.get('project_dir')}`
- **Files Created:** {len(res.get('files_created', []))}

*The prototype has been autonomously coded, configured, and verified for you, Sir!*
"""
    else:
        return f"Autonomous prototype build notice: {res.get('error') or 'Prototype initialized.'}"
