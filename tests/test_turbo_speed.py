"""
Tests for Aradhya TurboSpeed Engine & Maximum Laptop Performance Subsystem.
Verifies memory trimming, deep cache purging, work process priority boosting,
power profile enforcement, tool outputs, and offline commands.
"""

import pytest
from core.turbo_speed import TurboSpeedEngine
from tools.turbo_speed_tools import (
    boost_laptop_to_max_speed,
    inspect_laptop_performance_mode,
    toggle_turbo_performance_profile,
)
from core.offline_commander import OfflineCommander


def test_glibc_memory_trim():
    """Verify that glibc malloc_trim can be invoked safely without errors."""
    res = TurboSpeedEngine.trim_glibc_memory()
    assert isinstance(res, bool)


def test_compact_memory_and_sync():
    """Verify garbage collection and memory compaction routine."""
    engine = TurboSpeedEngine()
    res = engine.compact_memory_and_sync()
    assert "gc_objects_collected" in res
    assert "malloc_trimmed" in res
    assert "filesystem_synced" in res
    assert isinstance(res["malloc_trimmed"], bool)


def test_purge_deep_caches():
    """Verify cache purging logic executes safely."""
    engine = TurboSpeedEngine()
    res = engine.purge_deep_caches(clean_trash=False)
    assert "freed_bytes" in res
    assert "freed_mb" in res
    assert "files_cleared" in res
    assert res["freed_bytes"] >= 0


def test_power_profile():
    """Verify inspecting and setting power profile."""
    engine = TurboSpeedEngine()
    p_info = engine.get_power_profile()
    assert "active_profile" in p_info
    assert "available_profiles" in p_info

    # Test setting performance
    set_res = engine.set_power_profile("performance")
    assert "target_profile" in set_res
    assert set_res["target_profile"] == "performance"


def test_boost_active_work_processes():
    """Verify priority rebalancing for work and background processes."""
    engine = TurboSpeedEngine()
    res = engine.boost_active_work_processes()
    assert "boosted_count" in res
    assert "throttled_count" in res
    assert isinstance(res["boosted_processes"], list)
    assert isinstance(res["throttled_processes"], list)


def test_execute_turbo_boost():
    """Verify comprehensive turbo boost execution pipeline."""
    engine = TurboSpeedEngine()
    res = engine.execute_turbo_boost(aggressive=False, clean_deep_caches=True, boost_active_apps=True)
    assert res["success"] is True
    assert "ram_before_pct" in res
    assert "ram_after_pct" in res
    assert "cpu_after_pct" in res
    assert "gujarati_summary" in res
    assert "english_summary" in res
    assert "જી સાહેબ" in res["gujarati_summary"]


def test_turbo_speed_tools():
    """Verify user-facing TurboSpeed tools."""
    boost_report = boost_laptop_to_max_speed(aggressive=False, clean_deep_caches=False, boost_active_apps=True)
    assert "ARADHYA TURBOSPEED & MAXIMUM PERFORMANCE REPORT" in boost_report or "AROHI TURBOSPEED & MAXIMUM PERFORMANCE REPORT" in boost_report
    assert "RAM Utilization:" in boost_report

    status_report = inspect_laptop_performance_mode()
    assert "Aradhya Laptop Performance Profile & Hardware State" in status_report
    assert "Active Power Profile:" in status_report

    toggle_res = toggle_turbo_performance_profile("performance")
    assert "PERFORMANCE" in toggle_res or "Power profile" in toggle_res


def test_offline_commander_turbo_speed_gujarati():
    """Verify offline natural language handling for maximum speed in Gujarati."""
    commander = OfflineCommander()
    res = commander.execute_offline_turn("લેપટોપને બને તેટલું ઝડપી બનાવો")
    assert "જી સાહેબ" in res
    assert "Turbo Speed" in res or "ઝડપી" in res


def test_offline_commander_turbo_speed_english():
    """Verify offline natural language handling for 'make laptop as much as faster as possible'."""
    commander = OfflineCommander()
    res = commander.execute_offline_turn("also able to make laptop as much as faster as possible")
    assert "Sir" in res or "જી સાહેબ" in res
    assert any(k in res for k in ["Turbo Speed", "TurboSpeed", "ઝડપી", "fast", "speed"])
