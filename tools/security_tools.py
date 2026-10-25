"""
Security Tools for Aradhya Agent.
Provides tools for multi-vector cybersecurity audits, network vulnerability scanning,
backdoor/reverse-shell detection, firewall posture check, and threat neutralization.
"""

from typing import Dict, Any, Optional
from config.settings import load_config


_sentry_instance: Optional[Any] = None


def _get_sentry() -> Any:
    global _sentry_instance
    if _sentry_instance is None:
        from core.security_sentry import SecuritySentry
        cfg = load_config()
        _sentry_instance = SecuritySentry(cfg)
    return _sentry_instance


def run_system_security_audit(deep_scan: bool = True) -> str:
    """
    Run a comprehensive cybersecurity audit on this laptop to protect from hackers and malware.
    Inspects listening network ports (0.0.0.0 vs localhost), scans for reverse shells and backdoors,
    audits Linux UFW firewall status, checks authentication logs for failed logins/brute-force attacks,
    and checks crontabs and autostart persistence. Returns a detailed diagnostic report.
    """
    sentry = _get_sentry()
    audit = sentry.audit_system_security(deep_scan=deep_scan)
    curr_lang = getattr(sentry.config, "language", "gujarati")
    return sentry.format_security_report(audit, lang=curr_lang)


def scan_network_vulnerabilities() -> str:
    """
    Scan all network ports and listening sockets on the laptop.
    Identifies which ports are safely restricted to localhost (127.0.0.1)
    and flags any ports exposed to the external network / Wi-Fi (0.0.0.0) or high-risk services.
    """
    sentry = _get_sentry()
    ports_res = sentry.scan_listening_ports()
    
    total = ports_res["total_listening"]
    exposed = ports_res["exposed_count"]
    high_risk = ports_res["high_risk_count"]
    
    lines = [
        f"Network Vulnerability Scan Results:",
        f"- Total Active Listening Sockets: {total}",
        f"- Safely Isolated to Localhost: {total - exposed}",
        f"- Exposed to Local Network/Wi-Fi (0.0.0.0): {exposed}",
        f"- High-Risk Service Ports: {high_risk}",
        ""
    ]
    if ports_res["high_risk_sockets"]:
        lines.append("CRITICAL: High-Risk Listening Ports:")
        for s in ports_res["high_risk_sockets"]:
            lines.append(f"  - Port {s['port']} ({s['ip']}) | PID: {s['pid']} ({s['process_name']}) | Risk: {s.get('warning')}")
        lines.append("")

    if ports_res["exposed_sockets"]:
        lines.append("Exposed Ports (Accessible to LAN/Wi-Fi):")
        for s in ports_res["exposed_sockets"][:10]:
            lines.append(f"  - Port {s['port']} ({s['ip']}) | PID: {s['pid']} ({s['process_name']})")
    else:
        lines.append("All listening sockets are safely restricted to localhost loopback.")

    return "\n".join(lines)


def scan_for_hacker_backdoors() -> str:
    """
    Scan running processes and memory for hacker backdoors, reverse shell command patterns,
    malware running from temporary directories (/tmp, /dev/shm), or hidden executables.
    """
    sentry = _get_sentry()
    threats = sentry.scan_suspicious_processes()
    if not threats:
        return "Clean: Zero reverse shells, zero temporary-directory payloads, and zero hidden executable backdoors detected."

    lines = [f"ALERT: {len(threats)} Suspicious Process Threat(s) Detected!"]
    for t in threats:
        lines.append(f"- [PID {t['pid']}] {t['name']}: {t['description']} (Severity: {t['severity']}, User: {t['user']})")
    lines.append("\nUse neutralize_suspicious_threat(pid) to terminate offending processes.")
    return "\n".join(lines)


def check_firewall_status() -> str:
    """
    Check the current Linux UFW firewall status and incoming/outgoing security policies.
    """
    sentry = _get_sentry()
    fw = sentry.audit_firewall_status()
    enabled_str = "ENABLED (Active & Defending)" if fw["enabled"] else "DISABLED (Unprotected)"
    return (
        f"Linux Firewall (UFW) Status: {enabled_str}\n"
        f"- Systemd Service Active: {fw['systemd_active']}\n"
        f"- Inbound Traffic Policy: {fw['default_input_policy']}\n"
        f"- Outbound Traffic Policy: {fw['default_output_policy']}\n"
        f"- Recommendation: {fw['recommendation']}"
    )


def neutralize_suspicious_threat(target: str) -> str:
    """
    Neutralize a detected cybersecurity threat by terminating the hostile process PID or closing an unauthorized port.
    
    Args:
        target: The Process ID (PID), Port number, or process name to terminate.
    """
    sentry = _get_sentry()
    res = sentry.neutralize_threat(target)
    return res["message"]
