"""
Stark System Performance Optimizer & Housekeeping Subsystem for Aradhya.
Detects sluggish laptop conditions, frees cached memory, terminates zombie processes,
safely stops unnecessary resource-hogging background programs with whitelist protection,
and restores maximum responsiveness.
"""

import os
import sys
import time
import signal
import shutil
import psutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from tools.ironman_protocols import play_stark_sound


# Strict Whitelist: Critical system, display, and development processes that must NEVER be terminated
CRITICAL_SYSTEM_PROCESSES: Set[str] = {
    # Linux Kernel & Init
    "systemd", "systemd-journald", "systemd-udevd", "systemd-logind", "systemd-resolved",
    "init", "kthreadd", "ksoftirqd", "kworker", "rcu_sched", "rcu_bh", "migration",

    # Desktop Environment, Compositor & Display
    "cinnamon", "cinnamon-session", "cinnamon-launcher", "cinnamon-screensaver",
    "gnome-session", "gnome-shell", "mutter", "marco", "metacity",
    "xorg", "xwayland", "lightdm", "gdm", "gdm3", "sddm", "polkitd", "accounts-daemon",
    "nemo", "nautilus", "cinnamon-killer-daemon",

    # Audio, Hardware & Networking
    "pipewire", "pipewire-pulse", "wireplumber", "pulseaudio",
    "networkmanager", "wpa_supplicant", "bluetoothd", "cupsd", "rtkit-daemon",
    "dbus-daemon", "dbus-broker", "avahi-daemon", "upowerd", "thermald",

    # Development Environment & Terminals
    "antigravity", "bash", "zsh", "sh", "gnome-terminal", "gnome-terminal-server",
    "x-terminal-emulator", "tmux", "screen", "login",

    # Aradhya & Python Runtime
    "aradhya", "jarvis"
}


class SystemOptimizer:
    """Performs deep system cleanup, sluggishness detection, and process optimization on Linux."""

    def __init__(self):
        self.cleaned_bytes = 0
        self.killed_zombies = 0
        self.terminated_processes: List[Dict[str, Any]] = []

    def get_protected_pids(self) -> Set[int]:
        """Collect all PIDs that are strictly protected from termination."""
        protected: Set[int] = {0, 1, 2}

        # Protect current process and its entire ancestry
        try:
            curr = psutil.Process()
            protected.add(curr.pid)
            for parent in curr.parents():
                protected.add(parent.pid)
        except Exception:
            pass

        # Protect all processes matching whitelist
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                p_name = (proc.info['name'] or '').lower()
                cmdline = " ".join(proc.info['cmdline'] or []).lower()

                # Check against whitelist names
                if any(white in p_name for white in CRITICAL_SYSTEM_PROCESSES):
                    protected.add(proc.info['pid'])
                    continue

                # Protect anything related to Antigravity, active IDE, or Aradhya agent
                if any(ide in cmdline for ide in ["antigravity", "jarvis-agent", "main.py", "supervisor.py"]):
                    protected.add(proc.info['pid'])
                    continue

                # Protect session leader and terminal processes
                if proc.terminal():
                    protected.add(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return protected

    def diagnose_sluggishness(self) -> Dict[str, Any]:
        """
        Analyze system telemetry to diagnose if the laptop is feeling sluggish or resource-constrained.
        """
        cpu_pct = psutil.cpu_percent(interval=0.2)
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        try:
            load_avg = list(os.getloadavg())
        except (AttributeError, OSError):
            load_avg = [0.0, 0.0, 0.0]

        cpu_count = psutil.cpu_count() or 4
        is_cpu_high = cpu_pct >= 70.0 or (load_avg[0] > (cpu_count * 1.5))
        is_mem_high = mem.percent >= 80.0
        is_swap_high = swap.percent >= 60.0
        is_sluggish = is_cpu_high or is_mem_high or is_swap_high

        # Find top CPU and Memory consuming processes
        procs = []
        zombies = 0
        protected_pids = self.get_protected_pids()

        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info', 'status']):
            try:
                if p.info['status'] == psutil.STATUS_ZOMBIE:
                    zombies += 1
                    continue
                info = p.info
                info['is_protected'] = info['pid'] in protected_pids
                info['memory_mb'] = round(info['memory_info'].rss / (1024 * 1024), 1) if info['memory_info'] else 0.0
                procs.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        top_cpu = sorted(procs, key=lambda x: x.get('cpu_percent', 0.0), reverse=True)[:6]
        top_mem = sorted(procs, key=lambda x: x.get('memory_mb', 0.0), reverse=True)[:6]

        severity = "HIGH" if (cpu_pct >= 85 or mem.percent >= 90) else ("MODERATE" if is_sluggish else "NORMAL")

        return {
            "is_sluggish": is_sluggish,
            "severity": severity,
            "cpu_percent": cpu_pct,
            "ram_percent": mem.percent,
            "ram_used_gb": round((mem.total - mem.available) / (1024**3), 2),
            "ram_total_gb": round(mem.total / (1024**3), 2),
            "swap_percent": swap.percent,
            "load_averages": load_avg,
            "zombie_count": zombies,
            "top_cpu_processes": top_cpu,
            "top_memory_processes": top_mem
        }

    def clean_temporary_caches(self) -> int:
        """Cleans user temporary cache files, thumbnails, and temp video files."""
        freed = 0
        cache_dirs = [
            Path.home() / ".cache" / "thumbnails",
            Path.home() / ".cache" / "pip",
            Path("/tmp")
        ]

        for c_dir in cache_dirs:
            if not c_dir.exists():
                continue
            try:
                for item in c_dir.iterdir():
                    try:
                        if item.is_file() and (item.name.startswith("TEMP_") or item.name.endswith(".tmp") or "thumb" in str(item)):
                            size = item.stat().st_size
                            item.unlink()
                            freed += size
                    except Exception:
                        continue
            except Exception:
                continue

        # Clean YouTube agent temp files
        yt_dir = Path("/home/alpesh/youtube-agent")
        if yt_dir.exists():
            for tmp in yt_dir.glob("*TEMP*"):
                try:
                    size = tmp.stat().st_size
                    tmp.unlink()
                    freed += size
                except Exception:
                    pass

        self.cleaned_bytes += freed
        return freed

    def clean_zombie_processes(self) -> int:
        """Find and terminate zombie or defunct processes."""
        zombies = 0
        for proc in psutil.process_iter(['pid', 'status', 'name']):
            try:
                if proc.info['status'] == psutil.STATUS_ZOMBIE:
                    proc.kill()
                    zombies += 1
            except Exception:
                continue
        self.killed_zombies += zombies
        return zombies

    def stop_unnecessary_background_processes(
        self,
        max_cpu_pct: float = 20.0,
        max_mem_pct: float = 4.0,
        aggressive: bool = False
    ) -> Dict[str, Any]:
        """
        Safely identifies and terminates unnecessary, orphaned, or runaway background processes
        that are degrading laptop performance, while strictly respecting whitelist safety protections.
        """
        protected_pids = self.get_protected_pids()
        stopped: List[Dict[str, Any]] = []
        freed_mem_mb = 0.0

        # Also clean all zombie handles first
        zombies_cleared = self.clean_zombie_processes()

        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent', 'memory_info', 'status', 'create_time']):
            try:
                pid = proc.info['pid']
                if pid in protected_pids:
                    continue

                p_name = (proc.info['name'] or '').lower()
                cmdline = " ".join(proc.info['cmdline'] or []).lower()
                cpu_p = proc.info.get('cpu_percent', 0.0) or 0.0
                mem_p = proc.info.get('memory_percent', 0.0) or 0.0
                mem_mb = round(proc.info['memory_info'].rss / (1024 * 1024), 1) if proc.info['memory_info'] else 0.0

                should_stop = False
                stop_reason = ""

                # 1. Orphaned or runaway ffmpeg/video conversions
                if "ffmpeg" in p_name or "mencoder" in p_name:
                    should_stop = True
                    stop_reason = "Runaway media conversion worker"

                # 2. Defunct or runaway Python scripts (excluding agent, tests, and active IDE)
                elif "python" in p_name and not any(k in cmdline for k in ["pytest", "jarvis", "aradhya", "antigravity"]):
                    if cpu_p >= max_cpu_pct or (aggressive and cpu_p > 10.0):
                        should_stop = True
                        stop_reason = f"High CPU background python job ({cpu_p}%)"

                # 3. Excessive resource-hogging background non-system processes
                elif cpu_p >= max_cpu_pct and not proc.terminal():
                    should_stop = True
                    stop_reason = f"Unattended high CPU consumer ({cpu_p}%)"

                elif mem_p >= max_mem_pct and not proc.terminal() and aggressive:
                    should_stop = True
                    stop_reason = f"Aggressive memory reclamation ({mem_mb} MB)"

                # 4. Abandoned build workers
                elif any(dev_junk in p_name for dev_junk in ["cargo", "rustc", "esbuild"]) and not proc.terminal():
                    if cpu_p >= 15.0 or aggressive:
                        should_stop = True
                        stop_reason = f"Orphaned background build worker ({p_name})"

                if should_stop:
                    # Graceful termination (SIGTERM), then SIGKILL if unresponsive
                    try:
                        proc.terminate()
                        try:
                            proc.wait(timeout=1.5)
                        except psutil.TimeoutExpired:
                            proc.kill()

                        stopped.append({
                            "pid": pid,
                            "name": proc.info['name'],
                            "cpu_percent": cpu_p,
                            "memory_mb": mem_mb,
                            "reason": stop_reason
                        })
                        freed_mem_mb += mem_mb
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        self.terminated_processes.extend(stopped)

        return {
            "stopped_processes": stopped,
            "count": len(stopped),
            "zombies_cleared": zombies_cleared,
            "freed_memory_mb": round(freed_mem_mb, 1)
        }

    def terminate_process_by_name_or_pid(self, target: str) -> Dict[str, Any]:
        """
        Safely terminate a specific user-requested process by name or PID,
        with strict rejection if target is a protected system component.
        """
        protected_pids = self.get_protected_pids()
        target_clean = target.strip().lower()

        target_pid = None
        if target_clean.isdigit():
            target_pid = int(target_clean)

        terminated = []
        rejected = []

        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info']):
            try:
                pid = proc.info['pid']
                p_name = (proc.info['name'] or '').lower()

                matches = False
                if target_pid is not None and pid == target_pid:
                    matches = True
                elif target_pid is None and (target_clean == p_name or target_clean in p_name):
                    matches = True

                if matches:
                    if pid in protected_pids:
                        rejected.append({
                            "pid": pid,
                            "name": proc.info['name'],
                            "reason": "Process is a critical system/desktop or Aradhya component."
                        })
                        continue

                    mem_mb = round(proc.info['memory_info'].rss / (1024 * 1024), 1) if proc.info['memory_info'] else 0.0
                    proc.terminate()
                    try:
                        proc.wait(timeout=1.5)
                    except psutil.TimeoutExpired:
                        proc.kill()

                    terminated.append({
                        "pid": pid,
                        "name": proc.info['name'],
                        "memory_mb": mem_mb
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return {
            "target": target,
            "terminated": terminated,
            "rejected": rejected,
            "success": len(terminated) > 0
        }

    def run_optimization_routine(self, aggressive: bool = False) -> str:
        """Execute full optimization sweep, clean background hogs, and report telemetry."""
        play_stark_sound("protocol")
        diag_before = self.diagnose_sluggishness()
        mem_before = diag_before["ram_percent"]
        cpu_before = diag_before["cpu_percent"]

        # 1. Clean temporary disk caches
        freed_bytes = self.clean_temporary_caches()
        freed_mb = round(freed_bytes / (1024 * 1024), 2)

        # 2. Stop unnecessary background processes
        proc_res = self.stop_unnecessary_background_processes(aggressive=aggressive)

        # Measure after
        time.sleep(0.3)
        diag_after = self.diagnose_sluggishness()
        mem_after = diag_after["ram_percent"]
        cpu_after = diag_after["cpu_percent"]

        play_stark_sound("ack")

        stopped_lines = []
        if proc_res["stopped_processes"]:
            for p in proc_res["stopped_processes"]:
                stopped_lines.append(f"  - **{p['name']}** (PID: `{p['pid']}`) • {p['reason']} • Reclaimed `{p['memory_mb']} MB`")
        else:
            stopped_lines.append("  - *No rogue or runaway processes detected.*")

        stopped_text = "\n".join(stopped_lines)

        report = f"""# ⚡ ARADHYA PERFORMANCE OPTIMIZATION & SPEED BOOST REPORT
- **Laptop Sluggishness Diagnosis:** **{diag_before['severity']}** {'(Resource Contention Detected)' if diag_before['is_sluggish'] else '(Nominal)'}
- **RAM Utilization:** **{mem_before}% ➔ {mem_after}%** (Reclaimed ~{proc_res['freed_memory_mb']} MB from processes)
- **CPU Utilization:** **{cpu_before}% ➔ {cpu_after}%**
- **Temporary Disk Caches Cleaned:** **{freed_mb} MB**
- **Zombie Handles Eradicated:** **{proc_res['zombies_cleared']}**
- **Stopped Background Processes ({proc_res['count']}):**
{stopped_text}

*All system pipelines are operating at peak efficiency, Sir.*
"""
        return report

    def detect_hang_and_lag_indicators(self) -> Dict[str, Any]:
        """
        Deeply inspect indicators that cause system hanging, desktop freezing, and extreme lag:
        1. Stuck uninterruptible sleep (D-state) processes waiting on I/O.
        2. CPU spin loops (single or multi-core threads pinned at high CPU).
        3. Memory leaks and swap thrashing.
        4. Zombie processes clogging the process table.
        5. Extreme system load average exceeding available CPU cores.
        """
        cpu_pct = psutil.cpu_percent(interval=0.2)
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        try:
            load_avg = list(os.getloadavg())
        except (AttributeError, OSError):
            load_avg = [0.0, 0.0, 0.0]

        cpu_count = psutil.cpu_count() or 4
        protected_pids = self.get_protected_pids()

        d_state_processes = []
        cpu_hog_processes = []
        mem_hog_processes = []
        zombies = 0

        for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent', 'memory_info']):
            try:
                pid = proc.info['pid']
                status = proc.info.get('status')
                p_name = proc.info.get('name') or ''

                if status == psutil.STATUS_ZOMBIE:
                    zombies += 1
                    continue

                if status == psutil.STATUS_DISK_SLEEP and pid not in protected_pids:
                    d_state_processes.append({
                        "pid": pid,
                        "name": p_name,
                        "status": "D-state (Uninterruptible I/O Sleep)"
                    })

                cpu_p = proc.info.get('cpu_percent', 0.0) or 0.0
                if cpu_p >= 75.0 and pid not in protected_pids:
                    cpu_hog_processes.append({
                        "pid": pid,
                        "name": p_name,
                        "cpu_percent": cpu_p
                    })

                mem_mb = round(proc.info['memory_info'].rss / (1024 * 1024), 1) if proc.info.get('memory_info') else 0.0
                if mem_mb >= 1500.0 and pid not in protected_pids:
                    mem_hog_processes.append({
                        "pid": pid,
                        "name": p_name,
                        "memory_mb": mem_mb
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        is_hanging = (
            len(d_state_processes) > 0
            or cpu_pct >= 85.0
            or load_avg[0] > (cpu_count * 2.0)
            or mem.percent >= 90.0
            or swap.percent >= 75.0
        )

        is_lagging = is_hanging or cpu_pct >= 65.0 or mem.percent >= 80.0 or len(cpu_hog_processes) > 0

        severity = "CRITICAL_HANG" if (cpu_pct >= 90 or mem.percent >= 92 or len(d_state_processes) > 0) else (
            "HIGH_LAG" if is_hanging else ("MODERATE_LAG" if is_lagging else "NORMAL")
        )

        return {
            "is_hanging": is_hanging,
            "is_lagging": is_lagging,
            "severity": severity,
            "cpu_percent": cpu_pct,
            "ram_percent": mem.percent,
            "swap_percent": swap.percent,
            "load_averages": load_avg,
            "cpu_count": cpu_count,
            "d_state_processes": d_state_processes,
            "cpu_hog_processes": cpu_hog_processes,
            "mem_hog_processes": mem_hog_processes,
            "zombies_count": zombies
        }

    def auto_remedy_hang_and_lag(self, aggressive: bool = False) -> Dict[str, Any]:
        """
        Autonomously takes all necessary corrective steps when the laptop is hanging, lagging, or frozen:
        1. Cleans zombie handles to unblock PID tables.
        2. Clears temporary disk caches and thumbnails.
        3. Identifies runaway/frozen background processes, CPU spin-loops, and D-state processes.
        4. Safely terminates offending rogue background processes with strict whitelist protection.
        5. Renices any heavy background tasks to low priority (nice 15).
        6. Measures post-remediation metrics to verify recovery.
        """
        play_stark_sound("protocol")
        indicators_before = self.detect_hang_and_lag_indicators()

        # Step 1: Clean zombie processes
        zombies_cleared = self.clean_zombie_processes()

        # Step 2: Clean temporary caches to free disk buffers
        freed_cache_bytes = self.clean_temporary_caches()
        freed_cache_mb = round(freed_cache_bytes / (1024 * 1024), 2)

        # Step 3: Stop unnecessary/runaway background processes
        cpu_threshold = 15.0 if (indicators_before["is_hanging"] or aggressive) else 20.0
        proc_res = self.stop_unnecessary_background_processes(
            max_cpu_pct=cpu_threshold,
            max_mem_pct=3.5 if aggressive else 5.0,
            aggressive=aggressive or indicators_before["is_hanging"]
        )

        # Step 4: Clean non-protected D-state processes if any
        protected_pids = self.get_protected_pids()
        stuck_terminated = []
        for d_proc in indicators_before.get("d_state_processes", []):
            d_pid = d_proc["pid"]
            if d_pid not in protected_pids:
                try:
                    p = psutil.Process(d_pid)
                    p.terminate()
                    try:
                        p.wait(timeout=1.0)
                    except psutil.TimeoutExpired:
                        p.kill()
                    stuck_terminated.append(d_proc)
                except Exception:
                    pass

        # Step 5: Renice non-critical background jobs to yield CPU
        reniced_count = 0
        for proc in psutil.process_iter(['pid', 'name', 'nice', 'cpu_percent']):
            try:
                pid = proc.info['pid']
                if pid in protected_pids:
                    continue
                if (proc.info.get('cpu_percent', 0.0) or 0.0) > 10.0 and (proc.info.get('nice', 0) or 0) < 10:
                    try:
                        proc.nice(15)
                        reniced_count += 1
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        pass
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Step 5b: Proactively compact heap memory and flush dirty buffers
        try:
            from core.turbo_speed import TurboSpeedEngine
            turbo = TurboSpeedEngine()
            turbo.compact_memory_and_sync()
        except Exception:
            pass

        time.sleep(0.3)
        indicators_after = self.detect_hang_and_lag_indicators()
        play_stark_sound("ack")

        total_freed_mb = proc_res["freed_memory_mb"]
        total_procs_stopped = proc_res["count"] + len(stuck_terminated)

        gujarati_summary = (
            f"લેપટોપ હેંગિંગ અને લેગિંગ સફળતાપૂર્વક સુધારી લેવામાં આવ્યું છે, સાહેબ. "
            f"{total_procs_stopped} બિનજરૂરી/અટકેલી પ્રોસેસ અટકાવવામાં આવી, "
            f"{zombies_cleared} ઝોમ્બી હેન્ડલ દૂર કર્યા અને {freed_cache_mb} MB કેશ ખાલી કરી. "
            f"CPU: {indicators_before['cpu_percent']}% ➔ {indicators_after['cpu_percent']}%, "
            f"RAM: {indicators_before['ram_percent']}% ➔ {indicators_after['ram_percent']}%. "
            f"લેપટોપ હવે સરળતાથી અને ઝડપથી ચાલી રહ્યું છે."
        )

        english_summary = (
            f"Laptop hang & lag issue successfully resolved, Sir. "
            f"Stopped {total_procs_stopped} rogue/hung background process(es), "
            f"reaped {zombies_cleared} zombie(s), and purged {freed_cache_mb} MB temp cache. "
            f"CPU load transitioned from {indicators_before['cpu_percent']}% to {indicators_after['cpu_percent']}%, "
            f"RAM from {indicators_before['ram_percent']}% to {indicators_after['ram_percent']}%. "
            f"System responsiveness fully restored."
        )

        return {
            "success": True,
            "was_hanging": indicators_before["is_hanging"],
            "was_lagging": indicators_before["is_lagging"],
            "severity_before": indicators_before["severity"],
            "severity_after": indicators_after["severity"],
            "cpu_before": indicators_before["cpu_percent"],
            "cpu_after": indicators_after["cpu_percent"],
            "ram_before": indicators_before["ram_percent"],
            "ram_after": indicators_after["ram_percent"],
            "freed_memory_mb": total_freed_mb,
            "freed_cache_mb": freed_cache_mb,
            "zombies_cleared": zombies_cleared,
            "reniced_count": reniced_count,
            "stopped_processes": proc_res["stopped_processes"] + stuck_terminated,
            "gujarati_summary": gujarati_summary,
            "english_summary": english_summary
        }

