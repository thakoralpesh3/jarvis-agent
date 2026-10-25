"""
Tests for Iron Man protocols and diagnostic sweep.
"""

from tools.ironman_protocols import (
    run_full_diagnostic_sweep,
    execute_ironman_protocol,
    play_stark_sound,
)


def test_full_diagnostic_sweep():
    sweep = run_full_diagnostic_sweep()
    assert "STARK INDUSTRIES" in sweep
    assert "CPU INTEGRITY" in sweep
    assert "ARC REACTOR" in sweep
    assert "SYSTEM MEMORY" in sweep


def test_ironman_protocols():
    # Test House Party
    hp_res = execute_ironman_protocol("House Party")
    assert "House Party Protocol" in hp_res
    assert "Sir" in hp_res

    # Test Clean Slate
    cs_res = execute_ironman_protocol("Clean Slate")
    assert "Clean Slate Protocol" in cs_res
    assert "Sir" in cs_res

    # Test Sentry
    sentry_res = execute_ironman_protocol("Sentry")
    assert "Sentry Protocol" in sentry_res


def test_stark_sound_playback():
    res = play_stark_sound("ack")
    assert "Played sound effect" in res or "ack" in res
