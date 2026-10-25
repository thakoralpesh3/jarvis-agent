"""
Laptop TurboSpeed & High-Performance Optimization Tools for Aradhya.
Allows Aradhya and the user to push laptop performance to maximum potential,
reclaim RAM, purge disk caches, boost active application priorities, and manage power profiles.
"""

from typing import Optional


def boost_laptop_to_max_speed(
    aggressive: bool = False,
    clean_deep_caches: bool = True,
    boost_active_apps: bool = True
) -> str:
    """
    Make the laptop as fast as possible by executing full TurboSpeed optimization:
    reclaims RAM via glibc malloc_trim, purges disk caches, frees zombie processes,
    elevates CPU/IO priority for active work apps (Antigravity IDE, editors, terminals),
    throttles background hogs, and locks power governor to performance mode.

    Args:
        aggressive: Set to True for deep memory reclamation and trash purge.
        clean_deep_caches: Purge pip, thumbnail, and temporary caches.
        boost_active_apps: Rebalance CPU/IO scheduling priority for active work apps.
    """
    from core.turbo_speed import TurboSpeedEngine
    engine = TurboSpeedEngine()
    res = engine.execute_turbo_boost(
        aggressive=aggressive,
        clean_deep_caches=clean_deep_caches,
        boost_active_apps=boost_active_apps
    )

    stopped_lines = []
    if res["stopped_rogue_processes"]:
        for p in res["stopped_rogue_processes"]:
            stopped_lines.append(f"- `{p.get('name', 'unknown')}` (PID `{p.get('pid', 'N/A')}`) • Reclaimed `{p.get('memory_mb', 0)} MB`")
    else:
        stopped_lines.append("- *No runaway or zombie processes required termination.*")

    return f"""### 🚀 ARADHYA TURBOSPEED & MAXIMUM PERFORMANCE REPORT

> **ગુજરાતી સારાંશ:** {res['gujarati_summary']}
>
> **English Summary:** {res['english_summary']}

---
#### ⚡ Performance Benchmarks & Telemetry
- **RAM Utilization:** **`{res['ram_before_pct']}%` ➔ `{res['ram_after_pct']}%`** (Available: **`{res['ram_available_gb']} GB`**)
- **CPU Load:** **`{res['cpu_before_pct']}%` ➔ `{res['cpu_after_pct']}%`**
- **Swap Utilization:** **`{res['swap_before_pct']}%` ➔ `{res['swap_after_pct']}%`**
- **Caches & Junk Purged:** **`{res['total_cache_purged_mb']} MB`**
- **Glibc Memory Trimming (`malloc_trim`):** **`{'SUCCESS' if res['malloc_trimmed'] else 'N/A'}`**
- **Active Work Apps Boosted:** **`{res['boosted_work_apps']}`**
- **Background Processes Throttled:** **`{res['throttled_bg_apps']}`**
- **Power Profile:** **`{res['power_profile'].upper()}`**
- **Optimization Elapsed Time:** **`{res['elapsed_ms']} ms`**

#### 🛑 Handled Processes:
{chr(10).join(stopped_lines)}

*The laptop is primed for maximum throughput and zero micro-stutter latency, Sir.*
"""


def inspect_laptop_performance_mode() -> str:
    """
    Inspect the laptop's current hardware power profile, CPU scaling status,
    RAM pressure, and performance readiness.
    """
    import psutil
    from core.turbo_speed import TurboSpeedEngine
    engine = TurboSpeedEngine()
    power_info = engine.get_power_profile()

    mem = psutil.virtual_memory()
    cpu_pct = psutil.cpu_percent(interval=0.2)
    swap = psutil.swap_memory()
    load = psutil.getloadavg()

    status_badge = "🚀 TURBO / PEAK" if power_info.get("active_profile") == "performance" and mem.percent < 75 else ("🟡 MODERATE LOAD" if mem.percent < 85 else "🔴 MEMORY PRESSURE")

    return f"""### 🏎️ Aradhya Laptop Performance Profile & Hardware State
- **Status:** **{status_badge}**
- **Active Power Profile:** **`{power_info.get('active_profile', 'unknown').upper()}`**
- **Available Profiles:** {', '.join(f'`{p}`' for p in power_info.get('available_profiles', []))}
- **RAM Utilization:** **`{mem.percent}%`** ({round((mem.total - mem.available)/(1024**3), 2)} GB used / {round(mem.total/(1024**3), 2)} GB total)
- **Available Free RAM:** **`{round(mem.available/(1024**3), 2)} GB`**
- **CPU Load:** **`{cpu_pct}%`** (1m load: `{load[0]:.2f}`)
- **Swap Usage:** **`{swap.percent}%`** ({round(swap.used/(1024**3), 2)} GB)
- **Performance Governor Support:** `{'YES (powerprofilesctl)' if power_info.get('supported') else 'NO'}`
"""


def toggle_turbo_performance_profile(mode: str = "performance") -> str:
    """
    Switch laptop power and hardware performance profile.

    Args:
        mode: Profile to set ('performance', 'balanced', 'power-saver').
    """
    from core.turbo_speed import TurboSpeedEngine
    engine = TurboSpeedEngine()
    res = engine.set_power_profile(mode)

    if res.get("success"):
        return f"✅ Power profile successfully switched to **`{mode.upper()}`**. Hardware is configured for optimal speed."
    else:
        return f"⚠️ Could not set profile to `{mode}`: {res.get('error', 'unknown error')}. Falling back to default governors."
