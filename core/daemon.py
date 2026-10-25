"""
JARVIS Background Daemon & Service Manager.
Allows JARVIS to run unobtrusively in the background with proactive monitoring and voice listener.
"""

import os
import sys
import time
import json
import uuid
import signal
import psutil
import subprocess
from pathlib import Path
from typing import Optional

# Ensure jarvis-agent root is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from config.settings import JarvisConfig, load_config
from core.agent import JarvisAgent
from tools.laptop_work_tools import send_desktop_notification
from tools.ironman_protocols import play_stark_sound


class JarvisDaemon:
    """Manages background lifecycle, PID tracking, and proactive sentry monitoring."""

    def __init__(self, config: Optional[JarvisConfig] = None):
        self.config = config or load_config()
        self.pid_file = self.config.pid_file
        self.log_file = self.config.log_file
        self._running = False

    def is_running(self) -> tuple[bool, Optional[int]]:
        """Check if the background daemon is currently active."""
        if not self.pid_file.exists():
            return False, None

        try:
            pid = int(self.pid_file.read_text().strip())
            if psutil.pid_exists(pid):
                proc = psutil.Process(pid)
                if proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE:
                    return True, pid
        except Exception:
            pass

        # Cleanup stale pid file
        if self.pid_file.exists():
            try:
                self.pid_file.unlink()
            except Exception:
                pass
        return False, None

    def start(self, daemonize: bool = True) -> str:
        """Start the background daemon process."""
        running, pid = self.is_running()
        if running:
            return f"{self.config.agent_name} is already running in the background (PID: {pid})."

        if daemonize:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            # First fork
            try:
                pid = os.fork()
                if pid > 0:
                    # Parent process: wait for second fork to record PID, then return cleanly
                    time.sleep(0.3)
                    real_pid = int(self.pid_file.read_text().strip()) if self.pid_file.exists() else pid
                    play_stark_sound("protocol")
                    send_desktop_notification("Aradhya Background Core Active", f"Aradhya daemon online (PID: {real_pid}). Proactive sentry enabled.", user_commanded=False)
                    return f"{self.config.agent_name} background daemon successfully started (PID: {real_pid}). Logs: {self.log_file}"
            except OSError as e:
                return f"Fork #1 failed: {str(e)}"

            # Decouple from parent environment
            os.setsid()
            os.umask(0)

            # Second fork
            try:
                pid2 = os.fork()
                if pid2 > 0:
                    os._exit(0)
            except OSError as e:
                os._exit(1)

            # Daemon child process
            self._run_daemon_loop()
            os._exit(0)
        else:
            # Run in foreground of current process
            self._run_daemon_loop()
            return f"{self.config.agent_name} daemon stopped."

    def stop(self) -> str:
        """Stop the running background daemon."""
        running, pid = self.is_running()
        if not running or not pid:
            return f"{self.config.agent_name} background daemon is not running."

        try:
            proc = psutil.Process(pid)
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except psutil.TimeoutExpired:
                proc.kill()
        except psutil.NoSuchProcess:
            pass
        except Exception as e:
            return f"Error stopping daemon: {str(e)}"

        if self.pid_file.exists():
            try:
                self.pid_file.unlink()
            except Exception:
                pass

        play_stark_sound("ack")
        send_desktop_notification("Aradhya Background Core", "Background daemon standing down.", user_commanded=False)
        return f"{self.config.agent_name} background daemon (PID: {pid}) has been stopped."

    def status(self) -> str:
        """Get the current status of the background daemon."""
        running, pid = self.is_running()
        if not running or not pid:
            return f"{self.config.agent_name} Background Daemon: [STANDBY / INACTIVE]"

        try:
            proc = psutil.Process(pid)
            mem_mb = proc.memory_info().rss / (1024 * 1024)
            cpu = proc.cpu_percent(interval=0.1)
            create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(proc.create_time()))
            
            return (
                f"{self.config.agent_name} Background Daemon: [ACTIVE / ONLINE]\n"
                f"- Process ID: {pid}\n"
                f"- Started At: {create_time}\n"
                f"- CPU Usage: {cpu:.1f}%\n"
                f"- Memory Usage: {mem_mb:.1f} MB\n"
                f"- Telemetry Log: {self.log_file}"
            )
        except Exception as e:
            return f"Error retrieving daemon status: {str(e)}"

    def queue_background_task(self, command: str) -> dict:
        """Enqueue a laptop mission or command to be executed by Aradhya in the background."""
        import json, uuid
        queue_file = self.config.base_dir / "daemon_queue.json"
        tasks = []
        if queue_file.exists():
            try:
                tasks = json.loads(queue_file.read_text(encoding="utf-8") or "[]")
            except Exception:
                tasks = []
        task_id = f"bg_{int(time.time())}_{uuid.uuid4().hex[:4]}"
        task_entry = {
            "id": task_id,
            "command": command,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        tasks.append(task_entry)
        queue_file.write_text(json.dumps(tasks, indent=2), encoding="utf-8")
        return {"task_id": task_id, "status": "queued", "command": command}

    def process_background_queue(self, executor_fn=None, agent=None) -> list:
        """Process pending background tasks in the daemon queue."""
        queue_file = self.config.base_dir / "daemon_queue.json"
        if not queue_file.exists():
            return []

        executed_tasks = []
        try:
            raw = queue_file.read_text(encoding="utf-8").strip()
            tasks = json.loads(raw or "[]")
            if not tasks:
                return []

            while tasks:
                curr_task = tasks.pop(0)
                queue_file.write_text(json.dumps(tasks, indent=2), encoding="utf-8")
                cmd_str = curr_task.get("command", "")
                t_id = curr_task.get("id", "task")
                if not cmd_str:
                    continue

                self._log(f"Executing background task [{t_id}]: '{cmd_str}'")
                if executor_fn:
                    exec_res = executor_fn(cmd_str)
                else:
                    from core.laptop_work_executor import LaptopWorkExecutor
                    executor = LaptopWorkExecutor(agent=agent)
                    exec_res = executor.execute_mission(cmd_str)

                self._log(f"Task [{t_id}] completed.")
                send_desktop_notification(
                    "Aradhya Background Work Complete",
                    f"Laptop task completed: {cmd_str[:50]}",
                    details=exec_res.get("summary", "") if isinstance(exec_res, dict) else str(exec_res),
                    urgency="normal",
                    user_commanded=True
                )
                executed_tasks.append({"id": t_id, "command": cmd_str, "result": exec_res})
        except Exception as q_e:
            self._log(f"Queue processor error: {str(q_e)}")

        return executed_tasks

    def get_logs(self, lines: int = 25) -> str:
        """Read recent logs from the background daemon."""
        if not self.log_file.exists():
            return "No background logs available yet."

        try:
            with open(self.log_file, "r", encoding="utf-8", errors="replace") as f:
                all_lines = f.readlines()
                tail = all_lines[-lines:] if len(all_lines) > lines else all_lines
                return "".join(tail) if tail else "Log file is currently empty."
        except Exception as e:
            return f"Error reading logs: {str(e)}"

    def _log(self, msg: str) -> None:
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
                f.flush()
        except Exception:
            pass

    def _run_daemon_loop(self) -> None:
        """Internal proactive monitoring loop running in background process."""
        self.pid_file.write_text(str(os.getpid()))
        self._running = True
        self._log(f"{self.config.agent_name} Background Daemon initialized (PID: {os.getpid()}).")

        def _handle_signal(signum, frame):
            self._running = False

        signal.signal(signal.SIGTERM, _handle_signal)
        signal.signal(signal.SIGINT, _handle_signal)
        if hasattr(signal, "SIGHUP"):
            signal.signal(signal.SIGHUP, signal.SIG_IGN)

        agent = JarvisAgent(self.config)
        agent.config.enable_voice_response = False  # Keep quiet unless speech triggered
        
        last_battery_alert = 0
        last_hourly_ping = time.time()
        last_sluggish_check = time.time()
        last_hang_remedy_time = 0.0
        last_security_check = time.time() - 250  # Run initial scan 50s after startup
        last_cloud_sync = time.time()
        last_stay_awake_check = time.time() - 20
        last_evolution_check = time.time() - 21000
        last_speed_sentry_check = time.time() - 25
        self._stay_awake_sentry = None
        queue_file = self.config.base_dir / "daemon_queue.json"

        # Initial Cloud Synchronization: Pull any tasks queued by user while laptop was off
        try:
            from core.cloud_sync import CloudSyncManager
            cloud_sync = CloudSyncManager(self.config)
            cloud_sync.send_heartbeat()
            initial_tasks = cloud_sync.fetch_and_execute_pending_cloud_tasks(agent=agent)
            if initial_tasks:
                self._log(f"Executed {len(initial_tasks)} offline task(s) from cloud mailbox on boot.")
        except Exception as cs_err:
            self._log(f"Initial cloud sync notice: {str(cs_err)}")

        # Initialize hands-free background Wake Word listener ("Hey Aradhya")
        wake_listener = None
        try:
            from core.wake_word import WakeWordListener
            wake_listener = WakeWordListener(config=self.config)
            wake_listener.set_agent(agent)
            wake_listener.start()
            self._log("Step 12: Hands-free 'Hey Aradhya' background wake word listener online.")
        except Exception as wl_err:
            self._log(f"Wake word listener init notice: {str(wl_err)}")

        while self._running:
            try:
                # 1. Proactive Battery Sentry
                battery = psutil.sensors_battery()
                if battery and not battery.power_plugged and battery.percent <= 20:
                    now = time.time()
                    if now - last_battery_alert > 600:  # Alert every 10 minutes
                        last_battery_alert = now
                        send_desktop_notification(
                            "Aradhya Power Warning",
                            f"Sir, battery reserve is at {battery.percent}%. Please connect AC power.",
                            urgency="critical",
                            user_commanded=False
                        )

                # 2. Hourly Heartbeat & Maintenance
                if time.time() - last_hourly_ping > 3600:
                    last_hourly_ping = time.time()
                    self._log("Hourly sentry diagnostics nominal.")

                # 3. Daily Autonomous YouTube Shorts Agent Execution & Supervision
                from core.youtube_commander import YouTubeShortsCommander
                from core.network_resilience import check_internet_connection
                yt_commander = YouTubeShortsCommander()
                if yt_commander.is_daily_run_due():
                    if check_internet_connection(timeout=1.0):
                        self._log("Daily YouTube Shorts pipeline execution due. Commanding subordinate agent...")
                        yt_res = yt_commander.run_and_supervise_pipeline()
                        self._log(f"Daily YouTube Shorts execution result: {yt_res.get('status')} (Video: {yt_res.get('video_path', 'None')})")
                    else:
                        self._log("Offline: Skipping YouTube Shorts generation until internet is restored.")

                # 4. Universal Application Stoppage & Interrupted Task Resumption
                from core.universal_resumer import UniversalApplicationResumer
                resumer = UniversalApplicationResumer()
                app_resumes = resumer.inspect_and_auto_resume_all(agent_instance=agent)
                if app_resumes:
                    for item in app_resumes:
                        self._log(f"Universal Resumer recovered: {item}")

                # 5. Background Laptop Work / Mission Queue Processor
                self.process_background_queue(agent=agent)

                # 6. Proactive Hang & Lag Watchdog (HangShield) - Immediate Remediation
                try:
                    if time.time() - last_sluggish_check > 10:  # Fast sentry check every 10s
                        last_sluggish_check = time.time()
                        from core.system_optimizer import SystemOptimizer
                        optimizer = SystemOptimizer()
                        indicators = optimizer.detect_hang_and_lag_indicators()

                        # Immediate reaction to acute hang or any severe/moderate lagging
                        needs_remedy = (
                            indicators["is_hanging"]
                            or indicators["is_lagging"]
                            or indicators["severity"] in ("CRITICAL_HANG", "HIGH_LAG", "MODERATE_LAG")
                        )
                        is_critical = indicators["is_hanging"] or indicators["severity"] in ("CRITICAL_HANG", "HIGH_LAG")
                        cooldown = 15 if is_critical else 30

                        if needs_remedy and (time.time() - last_hang_remedy_time > cooldown):
                            last_hang_remedy_time = time.time()
                            self._log(
                                f"ALERT: Laptop lag/hang condition detected (Severity: {indicators['severity']}, "
                                f"CPU: {indicators['cpu_percent']}%, RAM: {indicators['ram_percent']}%, "
                                f"D-State: {len(indicators['d_state_processes'])}). Executing immediate autonomous remediation..."
                            )
                            remedy_res = optimizer.auto_remedy_hang_and_lag(aggressive=is_critical)

                            if (
                                remedy_res["stopped_processes"]
                                or remedy_res["zombies_cleared"] > 0
                                or remedy_res["freed_cache_mb"] > 5.0
                                or remedy_res.get("reniced_count", 0) > 0
                            ):
                                self._log(f"Auto-healed system hang/lag right away: {remedy_res['english_summary']}")
                                play_stark_sound("alert" if is_critical else "ack")
                                send_desktop_notification(
                                    "Aradhya HangShield: લેપટોપ હેંગિંગ/લેગિંગ અટકાવ્યું",
                                    remedy_res["gujarati_summary"][:120] + "...",
                                    details=remedy_res["english_summary"],
                                    urgency="critical" if is_critical else "normal",
                                    user_commanded=False
                                )
                except Exception as opt_err:
                    self._log(f"HangShield watchdog warning: {str(opt_err)}")

                # 7. Proactive Anti-Hacker Cyber Defense & Security Sentry
                try:
                    if time.time() - last_security_check > 300:  # Check every 5 minutes
                        last_security_check = time.time()
                        from core.security_sentry import SecuritySentry
                        sentry = SecuritySentry(self.config)
                        proc_threats = sentry.scan_suspicious_processes()
                        port_scan = sentry.scan_listening_ports()

                        if proc_threats:
                            crit_procs = [p for p in proc_threats if p.get("severity") in ("CRITICAL", "HIGH")]
                            if crit_procs:
                                threat_summary = f"{len(crit_procs)} malicious process indicator(s) detected: {crit_procs[0]['name']} (PID {crit_procs[0]['pid']})"
                                self._log(f"SECURITY ALERT: {threat_summary}")
                                sentry.log_security_event("CRITICAL_DAEMON_ALERT", threat_summary)
                                play_stark_sound("alert")
                                send_desktop_notification(
                                    "Aradhya Cyber Defense Alert",
                                    f"Threat Detected: {threat_summary}",
                                    details="Run '/security' in Aradhya CLI or command 'સિક્યુરિટી ચેક કરો' to inspect and neutralize.",
                                    urgency="critical",
                                    user_commanded=False
                                )

                        if port_scan.get("high_risk_count", 0) > 0:
                            hr_ports = port_scan["high_risk_sockets"]
                            p_info = f"Port {hr_ports[0]['port']} ({hr_ports[0].get('warning', 'High risk')})"
                            self._log(f"SECURITY ALERT: High-risk listening port exposed: {p_info}")
                            sentry.log_security_event("HIGH_RISK_PORT", p_info)
                            send_desktop_notification(
                                "Aradhya Port Sentry Alert",
                                f"High-risk network listener detected: {p_info}",
                                details="Inspect with '/ports' or command 'સિક્યુરિટી ચેક કરો'.",
                                urgency="critical",
                                user_commanded=False
                            )
                except Exception as sec_err:
                    self._log(f"Security sentry error: {str(sec_err)}")

                # 8. 24/7 Cloud Sentinel Heartbeat & Offline Task Sync
                try:
                    if time.time() - last_cloud_sync > 60:  # Every 60 seconds
                        last_cloud_sync = time.time()
                        from core.cloud_sync import CloudSyncManager
                        cloud_sync = CloudSyncManager(self.config)
                        cloud_sync.send_heartbeat()
                        cloud_tasks = cloud_sync.fetch_and_execute_pending_cloud_tasks(agent=agent)
                        if cloud_tasks:
                            self._log(f"Executed {len(cloud_tasks)} pending task(s) from cloud mailbox.")
                except Exception as cs_loop_err:
                    self._log(f"Cloud sync loop warning: {str(cs_loop_err)}")

                # 9. Autonomous Work StayAwake Sentry (AwakeGuard)
                try:
                    if time.time() - last_stay_awake_check > 20:  # Check every 20 seconds
                        last_stay_awake_check = time.time()
                        from core.stay_awake_sentry import StayAwakeSentry
                        if self._stay_awake_sentry is None:
                            self._stay_awake_sentry = StayAwakeSentry(self.config)
                        sync_res = self._stay_awake_sentry.evaluate_and_sync()
                        if sync_res.get("state_changed"):
                            if sync_res.get("action_taken") == "engaged":
                                self._log(f"StayAwake Sentry engaged: Work in progress ({', '.join(sync_res['active_apps'][:4])}). Sleep and lockscreen suppressed.")
                            elif sync_res.get("action_taken") == "released":
                                self._log("StayAwake Sentry released: Work apps closed. Normal power management restored.")
                except Exception as stay_err:
                    self._log(f"StayAwake sentry warning: {str(stay_err)}")

                # 10. Autonomous Self-Evolution & Tuning Maintenance (Every 6 hours)
                try:
                    if time.time() - last_evolution_check > 21600:  # Every 6 hours
                        last_evolution_check = time.time()
                        from core.self_evolution import SelfEvolutionEngine
                        evo = SelfEvolutionEngine(self.config)
                        evo_res = evo.run_evolution_cycle(auto_synthesize=False)
                        self._log(f"Autonomous Self-Evolution cycle completed: Gen {evo_res['current_generation']} (Latency: {evo_res['dispatch_latency_ms']}ms, Freed: {evo_res['heap_objects_freed']} objs).")
                except Exception as evo_err:
                    self._log(f"Self-evolution maintenance warning: {str(evo_err)}")

                # 11. Autonomous Continuous TurboSpeed Watchdog & Anti-Swap Thrashing Guard (Every 30 seconds)
                try:
                    if time.time() - last_speed_sentry_check > 30:
                        last_speed_sentry_check = time.time()
                        mem = psutil.virtual_memory()
                        # If RAM utilization exceeds 75% on this 3.73GB system,
                        # proactively execute glibc malloc_trim and buffer sync to prevent swap-thrashing
                        if mem.percent >= 75.0:
                            from core.turbo_speed import TurboSpeedEngine
                            turbo = TurboSpeedEngine(self.config)
                            compact_res = turbo.compact_memory_and_sync()
                            self._log(f"TurboSpeed Sentry: Proactively compacted memory at {mem.percent}% RAM (Trimmed: {compact_res['malloc_trimmed']}).")
                except Exception as spd_err:
                    self._log(f"TurboSpeed sentry warning: {str(spd_err)}")

                time.sleep(5)
            except Exception as e:
                self._log(f"Daemon error: {str(e)}")
                time.sleep(5)

        # Cleanup on exit
        if wake_listener and wake_listener.is_listening:
            try:
                wake_listener.stop()
            except Exception:
                pass

        if self._stay_awake_sentry is not None:
            try:
                self._stay_awake_sentry.release_inhibitors()
            except Exception:
                pass

        if self.pid_file.exists():
            try:
                self.pid_file.unlink()
            except Exception:
                pass
        self._log(f"{self.config.agent_name} Background Daemon exited cleanly.")


if __name__ == "__main__":
    if "--run-internal" in sys.argv:
        daemon = JarvisDaemon()
        daemon.start(daemonize=False)
