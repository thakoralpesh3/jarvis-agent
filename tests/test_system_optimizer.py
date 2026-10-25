"""
Tests for System Optimizer, Sluggishness Detection & Process Terminator.
"""

import os
import pytest
from core.system_optimizer import SystemOptimizer, CRITICAL_SYSTEM_PROCESSES
from tools.system_optimizer_tools import (
    optimize_laptop_performance,
    resolve_laptop_sluggishness,
    terminate_specific_process,
    diagnose_system_sluggishness,
)


def test_system_optimizer():
    optimizer = SystemOptimizer()
    report = optimizer.run_optimization_routine()
    assert isinstance(report, str)
    assert "PERFORMANCE OPTIMIZATION" in report


def test_optimize_laptop_performance_tool():
    res = optimize_laptop_performance()
    assert isinstance(res, str)
    assert "OPTIMIZATION" in res


def test_diagnose_sluggishness():
    optimizer = SystemOptimizer()
    diag = optimizer.diagnose_sluggishness()
    assert isinstance(diag, dict)
    assert "is_sluggish" in diag
    assert "cpu_percent" in diag
    assert "ram_percent" in diag
    assert "top_cpu_processes" in diag
    assert "top_memory_processes" in diag
    assert isinstance(diag["top_cpu_processes"], list)


def test_protected_whitelist():
    optimizer = SystemOptimizer()
    protected = optimizer.get_protected_pids()
    assert isinstance(protected, set)
    # PID 1 and current process must be protected
    assert 1 in protected
    assert os.getpid() in protected


def test_stop_unnecessary_background_processes():
    optimizer = SystemOptimizer()
    res = optimizer.stop_unnecessary_background_processes()
    assert isinstance(res, dict)
    assert "stopped_processes" in res
    assert "zombies_cleared" in res
    assert "freed_memory_mb" in res


def test_terminate_specific_process_protected():
    # Attempting to terminate systemd or current process must be rejected
    optimizer = SystemOptimizer()
    res = optimizer.terminate_process_by_name_or_pid("systemd")
    assert isinstance(res, dict)
    # systemd must be in rejected if found running, never terminated
    if res["rejected"]:
        assert any("systemd" in r["name"].lower() for r in res["rejected"])
    assert len(res["terminated"]) == 0


def test_terminate_specific_process_not_found():
    res = terminate_specific_process("totally_nonexistent_process_xyz_9999")
    assert "No running processes found matching" in res


def test_resolve_laptop_sluggishness_tool():
    report = resolve_laptop_sluggishness(aggressive=False)
    assert isinstance(report, str)
    assert "SPEED BOOST" in report
    assert "RAM Utilization" in report


def test_diagnose_system_sluggishness_tool():
    report = diagnose_system_sluggishness()
    assert isinstance(report, str)
    assert "Laptop Sluggishness & Resource Telemetry" in report
    assert "CPU Utilization" in report


def test_detect_hang_and_lag_indicators():
    from core.system_optimizer import SystemOptimizer
    optimizer = SystemOptimizer()
    diag = optimizer.detect_hang_and_lag_indicators()
    assert isinstance(diag, dict)
    assert "is_hanging" in diag
    assert "is_lagging" in diag
    assert "severity" in diag
    assert "d_state_processes" in diag
    assert "cpu_hog_processes" in diag
    assert "mem_hog_processes" in diag
    assert "zombies_count" in diag
    assert isinstance(diag["d_state_processes"], list)


def test_auto_remedy_hang_and_lag():
    from core.system_optimizer import SystemOptimizer
    optimizer = SystemOptimizer()
    res = optimizer.auto_remedy_hang_and_lag(aggressive=False)
    assert isinstance(res, dict)
    assert res["success"] is True
    assert "gujarati_summary" in res
    assert "english_summary" in res
    assert "freed_memory_mb" in res
    assert "zombies_cleared" in res
    assert "stopped_processes" in res
    assert "હેંગિંગ" in res["gujarati_summary"] or "સુધારી" in res["gujarati_summary"]


def test_remedy_laptop_hang_and_lag_tool():
    from tools.system_optimizer_tools import remedy_laptop_hang_and_lag
    report = remedy_laptop_hang_and_lag(aggressive=False)
    assert isinstance(report, str)
    assert "ARADHYA HANG & LAG REMEDIATION REPORT" in report or "AROHI HANG & LAG REMEDIATION REPORT" in report
    assert "ગુજરાતી સારાંશ" in report
    assert "System Recovery Telemetry" in report


def test_diagnose_hang_and_lag_causes_tool():
    from tools.system_optimizer_tools import diagnose_hang_and_lag_causes
    report = diagnose_hang_and_lag_causes()
    assert isinstance(report, str)
    assert "Aradhya Hang & Lag Diagnostics" in report
    assert "Overall Status" in report


