"""
Anti-Hacker Cyber Defense & Security Sentry Subsystem for Aradhya.
Protects the user's laptop from hackers, malware, unauthorized network listeners,
reverse shells, suspicious background processes, brute-force intrusions, and persistence backdoors.
Operates completely offline with zero cloud dependency, while offering rich bilingual diagnostics.
"""

import os
import re
import sys
import time
import socket
import datetime
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import psutil

from config.settings import JarvisConfig, load_config
from tools.laptop_work_tools import send_desktop_notification
from tools.ironman_protocols import play_stark_sound


class SecuritySentry:
    """
    Autonomous cybersecurity defense engine for Aradhya.
    Continuously audits system posture, identifies hacker intrusion vectors,
    and neutralizes suspicious processes.
    """

    # High-risk ports commonly targeted by exploit kits, reverse shells, or insecure services
    HIGH_RISK_PORTS = {
        21: "FTP (Plaintext credentials)",
        23: "Telnet (Unencrypted remote shell)",
        445: "SMB (EternalBlue / NetBIOS exploit target)",
        1337: "Common Hacker Backdoor / Elite shell",
        3389: "RDP (Exposed Remote Desktop)",
        4444: "Metasploit Default Listener / Reverse Shell",
        5900: "VNC (Unencrypted remote frame buffer)",
        6667: "IRC (Botnet Command & Control)",
        8888: "Alternative HTTP / Common web proxy backdoor",
        9999: "Common Trojan backdoor port",
        31337: "Back Orifice Trojan default",
    }

    # Regex patterns indicating reverse shell executions
    REVERSE_SHELL_PATTERNS = [
        r'bash\s+-i\s+>&\s*/dev/tcp/',
        r'sh\s+-i\s+>&\s*/dev/tcp/',
        r'nc(?:at)?(?:\.traditional)?\s+-[elvp]*e\s+(?:/bin/)?(?:ba)?sh',
        r'socat\s+.*(?:exec|system):',
        r'python(?:3)?\s+-c\s+.*import\s+(?:socket|subprocess|pty).*pty\.spawn',
        r'perl\s+-e\s+.*use\s+Socket.*open\(STDIN',
        r'php\s+-r\s+.*fsockopen\(',
        r'ruby\s+-rsocket\s+-e\s+.*spawn\(',
    ]

    # Temporary directories where malware often hides
    TEMP_EXEC_DIRS = ("/tmp", "/dev/shm", "/var/tmp")

    def __init__(self, config: Optional[JarvisConfig] = None):
        self.config = config or load_config()
        self.compiled_shell_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.REVERSE_SHELL_PATTERNS
        ]
        self.security_log_file = self.config.base_dir / "security_audit.log"
        self._ensure_log_exists()

    def _ensure_log_exists(self) -> None:
        try:
            self.security_log_file.parent.mkdir(parents=True, exist_ok=True)
            if not self.security_log_file.exists():
                self.security_log_file.write_text(
                    f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Aradhya Security Sentry Audit Log Initialized.\n",
                    encoding="utf-8"
                )
        except Exception:
            pass

    def log_security_event(self, level: str, message: str) -> None:
        """Append a timestamped security event to the audit log."""
        try:
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            entry = f"[{ts}] [{level.upper()}] {message}\n"
            with open(self.security_log_file, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # 1. Port & Socket Vulnerability Scanner
    # -------------------------------------------------------------------------
    def scan_listening_ports(self) -> Dict[str, Any]:
        """
        Scan all active listening sockets on the laptop.
        Identifies whether ports are safely isolated to localhost (127.0.0.1)
        or exposed to the local network / internet (0.0.0.0 or public interface).
        """
        listening_sockets = []
        exposed_sockets = []
        high_risk_sockets = []

        try:
            connections = psutil.net_connections(kind="inet")
            for c in connections:
                if c.status != psutil.CONN_LISTEN:
                    continue

                local_ip = c.laddr.ip if hasattr(c, 'laddr') and c.laddr else ""
                local_port = c.laddr.port if hasattr(c, 'laddr') and c.laddr else 0
                pid = c.pid

                proc_name = "Unknown"
                proc_exe = ""
                proc_user = ""
                if pid and psutil.pid_exists(pid):
                    try:
                        p = psutil.Process(pid)
                        proc_name = p.name()
                        proc_exe = p.exe()
                        proc_user = p.username()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                is_loopback = local_ip in ("127.0.0.1", "::1", "localhost")
                is_public_bound = local_ip in ("0.0.0.0", "::", "") or not is_loopback

                sock_info = {
                    "ip": local_ip,
                    "port": local_port,
                    "pid": pid,
                    "process_name": proc_name,
                    "executable": proc_exe,
                    "user": proc_user,
                    "is_loopback": is_loopback,
                    "is_public_bound": is_public_bound,
                    "risk": "LOW" if is_loopback else "MEDIUM"
                }

                if local_port in self.HIGH_RISK_PORTS:
                    sock_info["risk"] = "CRITICAL" if is_public_bound else "HIGH"
                    sock_info["warning"] = self.HIGH_RISK_PORTS[local_port]
                    high_risk_sockets.append(sock_info)
                elif is_public_bound:
                    exposed_sockets.append(sock_info)

                listening_sockets.append(sock_info)

        except Exception as e:
            self.log_security_event("ERROR", f"Failed scanning listening sockets: {str(e)}")

        return {
            "total_listening": len(listening_sockets),
            "exposed_count": len(exposed_sockets),
            "high_risk_count": len(high_risk_sockets),
            "listening_sockets": listening_sockets,
            "exposed_sockets": exposed_sockets,
            "high_risk_sockets": high_risk_sockets
        }

    # -------------------------------------------------------------------------
    # 2. Suspicious Process & Reverse Shell Scanner
    # -------------------------------------------------------------------------
    def scan_suspicious_processes(self) -> List[Dict[str, Any]]:
        """
        Inspect all running processes for backdoor indicators:
        - Reverse shell command invocations
        - Executables running out of /tmp, /dev/shm, or /var/tmp
        - Hidden binary executables
        """
        suspicious = []
        my_pid = os.getpid()
        parent_pid = os.getppid()

        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'username', 'create_time']):
            pid = proc.info.get('pid')
            if pid in (my_pid, parent_pid) or pid == 1:
                continue

            try:
                exe = proc.info.get('exe') or ""
                name = proc.info.get('name') or ""
                cmdline_list = proc.info.get('cmdline') or []
                cmdline = " ".join(cmdline_list)
                user = proc.info.get('username') or ""

                # Indicator 1: Binary executing from temporary or shared memory directories
                if any(exe.startswith(d) for d in self.TEMP_EXEC_DIRS):
                    suspicious.append({
                        "pid": pid,
                        "name": name,
                        "exe": exe,
                        "cmdline": cmdline[:100],
                        "user": user,
                        "threat_type": "TEMP_EXECUTION",
                        "severity": "HIGH",
                        "description": f"Process executing from temporary directory ({exe})"
                    })
                    continue

                # Indicator 2: Reverse shell command signatures
                for pattern in self.compiled_shell_patterns:
                    if pattern.search(cmdline):
                        suspicious.append({
                            "pid": pid,
                            "name": name,
                            "exe": exe,
                            "cmdline": cmdline[:120],
                            "user": user,
                            "threat_type": "REVERSE_SHELL",
                            "severity": "CRITICAL",
                            "description": "Reverse shell payload detected in process command line"
                        })
                        break

                # Indicator 3: Hidden executables (e.g. /home/user/.hidden_binary)
                if exe and Path(exe).name.startswith(".") and not exe.startswith("/proc"):
                    suspicious.append({
                        "pid": pid,
                        "name": name,
                        "exe": exe,
                        "cmdline": cmdline[:100],
                        "user": user,
                        "threat_type": "HIDDEN_BINARY",
                        "severity": "HIGH",
                        "description": f"Hidden executable binary running: {exe}"
                    })

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            except Exception:
                continue

        return suspicious

    # -------------------------------------------------------------------------
    # 3. Firewall (UFW) Posture Auditor
    # -------------------------------------------------------------------------
    def audit_firewall_status(self) -> Dict[str, Any]:
        """
        Inspects Linux Uncomplicated Firewall (UFW) configuration.
        Returns active state, configured rules, and security rating.
        """
        ufw_conf = Path("/etc/ufw/ufw.conf")
        default_ufw = Path("/etc/default/ufw")

        enabled = False
        default_input = "UNKNOWN"
        default_output = "UNKNOWN"

        # Check /etc/ufw/ufw.conf
        if ufw_conf.exists():
            try:
                text = ufw_conf.read_text(encoding="utf-8")
                for line in text.splitlines():
                    line = line.strip()
                    if line.startswith("ENABLED="):
                        val = line.split("=", 1)[1].strip().lower()
                        enabled = val in ("yes", "true", "1")
            except Exception:
                pass

        # Check /etc/default/ufw
        if default_ufw.exists():
            try:
                text = default_ufw.read_text(encoding="utf-8")
                for line in text.splitlines():
                    line = line.strip()
                    if line.startswith("DEFAULT_INPUT_POLICY="):
                        default_input = line.split("=", 1)[1].replace('"', '').strip()
                    elif line.startswith("DEFAULT_OUTPUT_POLICY="):
                        default_output = line.split("=", 1)[1].replace('"', '').strip()
            except Exception:
                pass

        # Also check systemd service
        service_active = False
        try:
            res = subprocess.run(["systemctl", "is-active", "ufw"], capture_output=True, text=True)
            service_active = res.stdout.strip() == "active"
        except Exception:
            pass

        return {
            "installed": ufw_conf.exists(),
            "enabled": enabled,
            "systemd_active": service_active,
            "default_input_policy": default_input,
            "default_output_policy": default_output,
            "status_summary": "PROTECTED" if enabled else "UNPROTECTED_FIREWALL_DISABLED",
            "recommendation": "Firewall active and defending" if enabled else "Run 'sudo ufw enable' to drop unsolicited incoming connections."
        }

    # -------------------------------------------------------------------------
    # 4. Authentication & Brute-Force Monitor (/var/log/auth.log)
    # -------------------------------------------------------------------------
    def audit_auth_logs(self, max_lines: int = 400) -> Dict[str, Any]:
        """
        Reads system authentication logs to identify failed password attempts,
        brute-force sweeps, invalid user probes, or sudo anomalies.
        """
        auth_log = Path("/var/log/auth.log")
        failed_attempts: List[str] = []
        sudo_violations: List[str] = []
        invalid_users: List[str] = []

        if not auth_log.exists():
            return {
                "available": False,
                "reason": "Log file /var/log/auth.log not found",
                "failed_attempts": [],
                "brute_force_detected": False
            }

        try:
            with open(auth_log, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                tail = lines[-max_lines:] if len(lines) > max_lines else lines

            for line in tail:
                line_lower = line.lower()
                if "failed password" in line_lower or "authentication failure" in line_lower:
                    failed_attempts.append(line.strip())
                if "invalid user" in line_lower:
                    invalid_users.append(line.strip())
                if "not in sudoers" in line_lower or "incorrect password attempt" in line_lower:
                    sudo_violations.append(line.strip())

        except PermissionError:
            return {
                "available": False,
                "reason": "Permission denied reading /var/log/auth.log",
                "failed_attempts": [],
                "brute_force_detected": False
            }
        except Exception as e:
            return {
                "available": False,
                "reason": str(e),
                "failed_attempts": [],
                "brute_force_detected": False
            }

        brute_force = len(failed_attempts) >= 10
        return {
            "available": True,
            "failed_attempts_count": len(failed_attempts),
            "invalid_users_count": len(invalid_users),
            "sudo_violations_count": len(sudo_violations),
            "brute_force_detected": brute_force,
            "recent_failures": failed_attempts[-5:]
        }

    # -------------------------------------------------------------------------
    # 5. Persistence Mechanisms & SSH Keys Audit
    # -------------------------------------------------------------------------
    def audit_persistence_and_ssh(self) -> Dict[str, Any]:
        """
        Audit persistence vectors where attackers install backdoors:
        - ~/.ssh/authorized_keys (backdoor SSH access)
        - User and system crontabs
        - ~/.config/autostart desktop entries
        """
        # SSH Authorized keys
        auth_keys_path = Path.home() / ".ssh" / "authorized_keys"
        ssh_keys = []
        if auth_keys_path.exists():
            try:
                for line in auth_keys_path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        ssh_keys.append(line[:50] + "...")
            except Exception:
                pass

        # User crontab
        user_crons = []
        try:
            res = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout:
                for line in res.stdout.splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        user_crons.append(line)
        except Exception:
            pass

        # Autostart applications
        autostart_dir = Path.home() / ".config" / "autostart"
        autostart_files = []
        if autostart_dir.exists():
            for f in autostart_dir.glob("*.desktop"):
                autostart_files.append(f.name)

        return {
            "ssh_authorized_keys_count": len(ssh_keys),
            "ssh_authorized_keys": ssh_keys,
            "user_cron_entries": user_crons,
            "user_cron_count": len(user_crons),
            "autostart_entries": autostart_files
        }

    # -------------------------------------------------------------------------
    # 6. Comprehensive System Security Audit
    # -------------------------------------------------------------------------
    def audit_system_security(self, deep_scan: bool = True) -> Dict[str, Any]:
        """
        Perform a comprehensive multi-vector cybersecurity audit.
        Calculates an overall threat severity score: SECURE, LOW, MEDIUM, HIGH, CRITICAL.
        """
        start_t = time.time()
        port_scan = self.scan_listening_ports()
        proc_scan = self.scan_suspicious_processes()
        fw_audit = self.audit_firewall_status()
        auth_audit = self.audit_auth_logs()
        persist_audit = self.audit_persistence_and_ssh()

        findings = []
        severity = "SECURE"

        # Evaluate Port Exposures
        if port_scan["high_risk_count"] > 0:
            severity = "CRITICAL"
            findings.append(f"CRITICAL: {port_scan['high_risk_count']} high-risk ports listening!")
        elif port_scan["exposed_count"] > 0:
            if severity in ("SECURE", "LOW"):
                severity = "MEDIUM"
            findings.append(f"WARNING: {port_scan['exposed_count']} ports exposed to 0.0.0.0 (Local Network / Wi-Fi).")

        # Evaluate Suspicious Processes
        if proc_scan:
            for p in proc_scan:
                if p["severity"] == "CRITICAL":
                    severity = "CRITICAL"
                elif p["severity"] == "HIGH" and severity != "CRITICAL":
                    severity = "HIGH"
                findings.append(f"{p['severity']}: {p['threat_type']} detected on PID {p['pid']} ({p['name']}).")

        # Evaluate Firewall
        if not fw_audit["enabled"]:
            if severity == "SECURE":
                severity = "LOW"
            findings.append("NOTICE: Linux UFW Firewall is currently disabled.")

        # Evaluate Auth Log
        if auth_audit.get("brute_force_detected"):
            severity = "HIGH"
            findings.append(f"ALERT: Brute-force login probe detected ({auth_audit['failed_attempts_count']} failed password attempts).")

        audit_result = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "elapsed_seconds": round(time.time() - start_t, 2),
            "overall_severity": severity,
            "findings_count": len(findings),
            "findings": findings,
            "ports": port_scan,
            "suspicious_processes": proc_scan,
            "firewall": fw_audit,
            "authentication": auth_audit,
            "persistence": persist_audit
        }

        self.log_security_event(severity, f"Audit complete: {len(findings)} findings. Severity: {severity}")
        return audit_result

    # -------------------------------------------------------------------------
    # 7. Threat Neutralizer (Kill hostile process or close port)
    # -------------------------------------------------------------------------
    def neutralize_threat(self, target: Union[int, str]) -> Dict[str, Any]:
        """
        Safely neutralize a detected security threat by PID or Port number.
        Sends SIGTERM first, waits, then forcefully issues SIGKILL.
        """
        target_str = str(target).strip()
        pid_to_kill: Optional[int] = None
        target_desc = ""

        # Check if target is a port number
        if target_str.isdigit() and int(target_str) > 1024:
            port_num = int(target_str)
            for c in psutil.net_connections(kind="inet"):
                if hasattr(c, "laddr") and c.laddr and c.laddr.port == port_num:
                    if c.pid:
                        pid_to_kill = c.pid
                        target_desc = f"Port {port_num} (PID: {pid_to_kill})"
                        break

        # Check if target is a PID
        if not pid_to_kill:
            try:
                pid_val = int(target_str)
                if psutil.pid_exists(pid_val):
                    pid_to_kill = pid_val
                    target_desc = f"PID {pid_val}"
            except ValueError:
                for p in psutil.process_iter(['pid', 'name']):
                    if p.info['name'] and p.info['name'].lower() == target_str.lower():
                        pid_to_kill = p.info['pid']
                        target_desc = f"Process '{target_str}' (PID: {pid_to_kill})"
                        break

        if not pid_to_kill:
            return {
                "success": False,
                "message": f"Target '{target}' not found among active processes or listening ports."
            }

        whitelist_pids = {1, os.getpid(), os.getppid()}
        if pid_to_kill in whitelist_pids:
            return {
                "success": False,
                "message": f"Cannot terminate protected system PID {pid_to_kill}."
            }

        try:
            proc = psutil.Process(pid_to_kill)
            proc_name = proc.name()
            proc.terminate()
            try:
                proc.wait(timeout=2.0)
            except psutil.TimeoutExpired:
                proc.kill()

            msg = f"Threat successfully neutralized: {target_desc} ({proc_name}) terminated."
            self.log_security_event("NEUTRALIZED", msg)
            play_stark_sound("protocol")
            return {
                "success": True,
                "pid": pid_to_kill,
                "process_name": proc_name,
                "message": msg
            }
        except psutil.NoSuchProcess:
            return {
                "success": True,
                "pid": pid_to_kill,
                "message": f"Target process {pid_to_kill} has already terminated."
            }
        except Exception as e:
            return {
                "success": False,
                "pid": pid_to_kill,
                "message": f"Failed to neutralize threat PID {pid_to_kill}: {str(e)}"
            }

    # -------------------------------------------------------------------------
    # 8. Report Formatter (Gujarati & English)
    # -------------------------------------------------------------------------
    def format_security_report(self, audit: Dict[str, Any], lang: str = "gu") -> str:
        """Format the security audit diagnostic into an executive bilingual report."""
        severity = audit.get("overall_severity", "SECURE")
        ports = audit.get("ports", {})
        fw = audit.get("firewall", {})
        procs = audit.get("suspicious_processes", [])
        auth = audit.get("authentication", {})
        persist = audit.get("persistence", {})
        findings = audit.get("findings", [])

        sev_icons = {
            "SECURE": "🟢 સુરક્ષિત (SECURE - NO THREATS)",
            "LOW": "🟡 સામાન્ય ચેતવણી (LOW - MINOR NOTICE)",
            "MEDIUM": "🟠 મધ્યમ જોખમ (MEDIUM ATTENTION)",
            "HIGH": "🔴 ઉચ્ચ જોખમ (HIGH RISK DETECTED)",
            "CRITICAL": "🚨 ગંભીર ખતરો (CRITICAL THREAT INTRUSION)"
        }
        sev_display = sev_icons.get(severity, severity)

        if lang.lower() in ("en", "english"):
            lines = [
                f"# 🛡️ ARADHYA CYBER DEFENSE & SECURITY AUDIT REPORT\n",
                f"- **Overall Security Status:** **{severity}**",
                f"- **Audit Completed:** {audit.get('timestamp')} (Scan Time: {audit.get('elapsed_seconds')}s)",
                "",
                f"### 🔍 Key Findings & Alerts ({len(findings)}):"
            ]
            if findings:
                for f in findings:
                    lines.append(f"  - {f}")
            else:
                lines.append("  - *No security vulnerabilities or unauthorized intrusions detected.*")

            lines.extend([
                "",
                "### 📡 Network Ports & Listening Sockets:",
                f"- **Total Listening Sockets:** {ports.get('total_listening', 0)}",
                f"- **Safely Isolated to Localhost (127.0.0.1):** {ports.get('total_listening', 0) - ports.get('exposed_count', 0)}",
                f"- **Exposed to Network (0.0.0.0):** {ports.get('exposed_count', 0)}",
                f"- **High-Risk Ports Detected:** {ports.get('high_risk_count', 0)}",
                "",
                "### 🧱 Linux Firewall (UFW) Posture:",
                f"- **Firewall Enabled:** {'YES (Active)' if fw.get('enabled') else 'NO (Disabled)'}",
                f"- **Default Inbound Policy:** `{fw.get('default_input_policy')}`",
                f"- **Recommendation:** {fw.get('recommendation')}",
                "",
                "### 🕵️ Backdoor & Suspicious Process Inspection:",
                f"- **Threats Identified:** {len(procs)}",
            ])
            if procs:
                for p in procs:
                    lines.append(f"  - **[PID {p['pid']}]** {p['name']}: {p['description']} (Severity: {p['severity']})")
            else:
                lines.append("  - *Zero reverse shells, no temp-directory payloads, zero hidden binaries.*")

            lines.extend([
                "",
                "### 🔐 Authentication & Access Telemetry:",
                f"- **Failed Login Probes:** {auth.get('failed_attempts_count', 0)}",
                f"- **Brute-Force Attack Status:** {'DETECTED' if auth.get('brute_force_detected') else 'None'}",
                f"- **Authorized SSH Keys:** {persist.get('ssh_authorized_keys_count', 0)}",
                f"- **Active User Crontabs:** {persist.get('user_cron_count', 0)}",
                "",
                "*Aradhya Cyber Sentry continues active monitoring in background.*"
            ])
            return "\n".join(lines)

        lines = [
            f"# 🛡️ આરાધ્યા સાયબર ડિફેન્સ અને સિક્યુરિટી ઑડિટ રિપોર્ટ",
            f"- **કુલ સુરક્ષા સ્થિતિ (Security Posture):** **{sev_display}**",
            f"- **ઑડિટ પૂર્ણ થયું:** {audit.get('timestamp')} (સ્કેન સમય: {audit.get('elapsed_seconds')}s)",
            "",
            f"### 🔍 મુખ્ય તારણો અને ચેતવણીઓ ({len(findings)}):"
        ]
        if findings:
            for f in findings:
                lines.append(f"  - {f}")
        else:
            lines.append("  - *લેપટોપ પર કોઈ શંકાસ્પદ ઘૂસણખોરી, હેકર પેલોડ કે વાયરસ મળ્યા નથી.*")

        lines.extend([
            "",
            "### 📡 નેટવર્ક પોર્ટ્સ અને લિસનિંગ સોકેટ્સ:",
            f"- **કુલ સક્રિય લિસનિંગ સોકેટ્સ:** {ports.get('total_listening', 0)}",
            f"- **સુરક્ષિત લોકલહોસ્ટ (127.0.0.1):** {ports.get('total_listening', 0) - ports.get('exposed_count', 0)}",
            f"- **નેટવર્ક પર ખુલ્લા પોર્ટ્સ (0.0.0.0):** {ports.get('exposed_count', 0)}",
            f"- **જોખમી પોર્ટ્સ (High-Risk):** {ports.get('high_risk_count', 0)}",
            "",
            "### 🧱 લિનક્સ ફાયરવોલ (UFW) સ્થિતિ:",
            f"- **ફાયરવોલ સક્રિય છે?:** {'હા (સુરક્ષિત)' if fw.get('enabled') else 'ના (નિષ્ક્રિય - Disabled)'}",
            f"- **ઇનકમિંગ પોલિસી:** `{fw.get('default_input_policy')}`",
            f"- **ભલામણ:** {fw.get('recommendation')}",
            "",
            "### 🕵️ બેકડોર્સ અને શંકાસ્પદ પ્રોસેસ તપાસ:",
            f"- **શંકાસ્પદ પ્રક્રિયાઓ:** {len(procs)}",
        ])
        if procs:
            for p in procs:
                lines.append(f"  - **[PID {p['pid']}]** {p['name']}: {p['description']} (જોખમ સ્તર: {p['severity']})")
        else:
            lines.append("  - *કોઈ રિવર્સ શેલ, અસ્થાયી (/tmp) પેલોડ કે છૂપી બાઈનરી સક્રિય નથી.*")

        lines.extend([
            "",
            "### 🔐 ઓથેન્ટિકેશન અને પ્રવેશ સુરક્ષા:",
            f"- **નિષ્ફળ લોગિન પ્રયાસો:** {auth.get('failed_attempts_count', 0)}",
            f"- **બ્રુટ-ફોર્સ અટેક:** {'ચેતવણી - જણાયું છે' if auth.get('brute_force_detected') else 'કોઈ નથી (સામાન્ય)'}",
            f"- **ઓથોરાઇઝ્ડ SSH કીઝ:** {persist.get('ssh_authorized_keys_count', 0)}",
            f"- **યુઝર ક્રોન જોબ્સ:** {persist.get('user_cron_count', 0)}",
            "",
            "*જી સાહેબ, આરાધ્યા સાયબર સેન્ટ્રી બેકગ્રાઉન્ડમાં સતત આપના લેપટોપની સુરક્ષા જાળવી રહી છે.*"
        ])
        return "\n".join(lines)
