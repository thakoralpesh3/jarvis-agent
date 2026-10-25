"""
System Performance Optimizer & Sluggishness Resolution Tools for Aradhya.
"""

from typing import Optional


def optimize_laptop_performance() -> str:
    """
    Perform deep system cleanup: clear temporary cache files, terminate zombie processes,
    stop unnecessary background tasks, and optimize laptop responsiveness.
    """
    from core.system_optimizer import SystemOptimizer
    optimizer = SystemOptimizer()
    return optimizer.run_optimization_routine(aggressive=False)


def resolve_laptop_sluggishness(aggressive: bool = False) -> str:
    """
    Diagnose why the laptop is feeling sluggish, slow, or unresponsive, and automatically
    stop unnecessary background processes, orphan workers, and zombie handles to restore speed.

    Args:
        aggressive: Set to True for deeper cleanup if the laptop is severely lagging.
    """
    from core.system_optimizer import SystemOptimizer
    optimizer = SystemOptimizer()
    return optimizer.run_optimization_routine(aggressive=aggressive)


def terminate_specific_process(process_name_or_pid: str) -> str:
    """
    Safely stop or terminate a specific unnecessary background program or process by name or PID.
    Protected system, desktop environment, and Aradhya components will not be terminated.

    Args:
        process_name_or_pid: Name of the process (e.g. 'ffmpeg', 'chrome') or PID (e.g. '1234').
    """
    from core.system_optimizer import SystemOptimizer
    optimizer = SystemOptimizer()
    res = optimizer.terminate_process_by_name_or_pid(process_name_or_pid)

    lines = [f"### 🛑 Process Termination Analysis for: `{process_name_or_pid}`"]

    if res["terminated"]:
        lines.append("\n**Terminated Processes:**")
        for p in res["terminated"]:
            lines.append(f"- **{p['name']}** (PID: `{p['pid']}`) • Freed `{p['memory_mb']} MB` RAM")

    if res["rejected"]:
        lines.append("\n**Protected from Termination (Safe Whitelist):**")
        for p in res["rejected"]:
            lines.append(f"- ⚠️ **{p['name']}** (PID: `{p['pid']}`) • *{p['reason']}*")

    if not res["terminated"] and not res["rejected"]:
        lines.append(f"\n*No running processes found matching '{process_name_or_pid}'.*")

    return "\n".join(lines)


def diagnose_system_sluggishness() -> str:
    """
    Inspect CPU, RAM, Swap, and system load to determine if the laptop is overloaded or sluggish,
    and list the top resource-consuming background processes.
    """
    from core.system_optimizer import SystemOptimizer
    optimizer = SystemOptimizer()
    diag = optimizer.diagnose_sluggishness()

    top_cpu_lines = [f"  - `{p['name']}` (PID `{p['pid']}`): **{p['cpu_percent']}% CPU** {'(Protected)' if p.get('is_protected') else ''}" for p in diag['top_cpu_processes']]
    top_mem_lines = [f"  - `{p['name']}` (PID `{p['pid']}`): **{p['memory_mb']} MB RAM** ({p.get('memory_percent', 0):.1f}%) {'(Protected)' if p.get('is_protected') else ''}" for p in diag['top_memory_processes']]

    status_icon = "🔴 HIGH STRESS" if diag['severity'] == "HIGH" else ("🟡 MODERATE LOAD" if diag['is_sluggish'] else "🟢 OPTIMAL")

    return f"""### 💻 Laptop Sluggishness & Resource Telemetry
- **System Health Status:** **{status_icon}**
- **CPU Utilization:** **{diag['cpu_percent']}%** (Load: {diag['load_averages'][0]:.2f}, {diag['load_averages'][1]:.2f}, {diag['load_averages'][2]:.2f})
- **RAM Utilization:** **{diag['ram_percent']}%** ({diag['ram_used_gb']} GB / {diag['ram_total_gb']} GB)
- **Swap Utilization:** **{diag['swap_percent']}%**
- **Zombie Process Handles:** **{diag['zombie_count']}**

**Top CPU Consumers:**
{chr(10).join(top_cpu_lines) if top_cpu_lines else '  - None'}

**Top Memory Consumers:**
{chr(10).join(top_mem_lines) if top_mem_lines else '  - None'}
"""


def remedy_laptop_hang_and_lag(aggressive: bool = False) -> str:
    """
    Autonomously take necessary corrective steps when the laptop is hanging, freezing, or severely lagging.
    Cleans zombie handles, purges temporary cache, terminates rogue runaway/D-state processes
    (safely protecting system and display), renices heavy jobs, and restores laptop fluidity.

    Args:
        aggressive: Set to True if system is completely frozen or heavily lagging.
    """
    from core.system_optimizer import SystemOptimizer
    optimizer = SystemOptimizer()
    res = optimizer.auto_remedy_hang_and_lag(aggressive=aggressive)

    stopped_rows = []
    if res["stopped_processes"]:
        for p in res["stopped_processes"]:
            reason = p.get("reason") or p.get("status") or "Resource contention"
            mem = p.get("memory_mb", 0.0)
            stopped_rows.append(f"| `{p.get('name', 'unknown')}` | `{p.get('pid', 'N/A')}` | {reason} | `{mem} MB` |")
    else:
        stopped_rows.append("| *None* | *—* | *No rogue processes required termination* | *0 MB* |")

    table_str = "\n".join(stopped_rows)

    return f"""### 🛡️ ARADHYA HANG & LAG REMEDIATION REPORT (હૅંગિંગ અને લેગિંગ નિવારણ રિપોર્ટ)

> **ગુજરાતી સારાંશ:** {res['gujarati_summary']}
>
> **English Summary:** {res['english_summary']}

---
#### 📊 System Recovery Telemetry
- **System Stress Level:** `{res['severity_before']}` ➔ **`{res['severity_after']}`**
- **CPU Utilization:** **`{res['cpu_before']}%`** ➔ **`{res['cpu_after']}%`**
- **RAM Utilization:** **`{res['ram_before']}%`** ➔ **`{res['ram_after']}%`**
- **Reclaimed Memory:** **`{res['freed_memory_mb']} MB`**
- **Purged Temp Caches:** **`{res['freed_cache_mb']} MB`**
- **Zombie Handles Cleared:** **`{res['zombies_cleared']}`**
- **Background Tasks Throttled/Reniced:** **`{res['reniced_count']}`**

#### 🛑 Actions Taken on Background Processes
| Process Name | PID | Action / Reason | Reclaimed RAM |
| :--- | :--- | :--- | :--- |
{table_str}

*All essential system, display, and Aradhya components remain fully protected.*
"""


def diagnose_hang_and_lag_causes() -> str:
    """
    Deeply diagnose what is causing the laptop to hang, lag, or stutter.
    Inspects stuck D-state processes, CPU spin loops, memory thrashing, and load averages.
    """
    from core.system_optimizer import SystemOptimizer
    optimizer = SystemOptimizer()
    diag = optimizer.detect_hang_and_lag_indicators()

    d_state_lines = [f"  - ⚠️ PID `{p['pid']}` (`{p['name']}`): {p['status']}" for p in diag['d_state_processes']]
    cpu_lines = [f"  - 🔥 PID `{p['pid']}` (`{p['name']}`): **{p['cpu_percent']}% CPU**" for p in diag['cpu_hog_processes']]
    mem_lines = [f"  - 💾 PID `{p['pid']}` (`{p['name']}`): **{p['memory_mb']} MB RAM**" for p in diag['mem_hog_processes']]

    status_badge = "🚨 CRITICAL HANG / FREEZE" if diag['is_hanging'] else ("⚠️ LAGGING / HIGH STRESS" if diag['is_lagging'] else "✅ HEALTHY / NOMINAL")

    return f"""### 🔍 Aradhya Hang & Lag Diagnostics (હૅંગ અને લેગ ડાયગ્નોસ્ટિક્સ)
- **Overall Status:** **{status_badge}** (`{diag['severity']}`)
- **CPU Usage:** **{diag['cpu_percent']}%** (Cores: {diag['cpu_count']}, Load: {diag['load_averages'][0]:.2f}, {diag['load_averages'][1]:.2f}, {diag['load_averages'][2]:.2f})
- **RAM Usage:** **{diag['ram_percent']}%** | **Swap Usage:** **{diag['swap_percent']}%**
- **Zombie Handles:** **{diag['zombies_count']}**

**Stuck I/O / D-State Processes ({len(diag['d_state_processes'])}):**
{chr(10).join(d_state_lines) if d_state_lines else '  - None (Disk I/O is responsive)'}

**Extreme CPU Consumer Threads ({len(diag['cpu_hog_processes'])}):**
{chr(10).join(cpu_lines) if cpu_lines else '  - None (No runaway CPU spin-loops)'}

**Extreme Memory Consumer Processes ({len(diag['mem_hog_processes'])}):**
{chr(10).join(mem_lines) if mem_lines else '  - None'}
"""


