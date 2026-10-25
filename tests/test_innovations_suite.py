"""
Unit Tests for the 8 JARVIS & Chamunda CEO Innovation Modules.
"""

import pytest
from core.acoustic_diagnostics import REAcousticDiagnosticEngine
from core.vision_part_scanner import REVisionPartScanner
from core.riders_club import ChamundaRidersClubManager
from core.wholesale_po_engine import WholesalePOEngine
from core.wake_word import WakeWordListener
from core.silent_shadow_copilot import SilentShadowCopilot
from core.price_scraper import PriceScraperAndOptimizer
from tools.innovations_suite_tools import (
    diagnose_re_engine_sound,
    scan_re_part_image,
    manage_chamunda_riders_club,
    generate_wholesale_purchase_order,
    optimize_re_part_pricing
)


def test_acoustic_engine_diagnostics():
    engine = REAcousticDiagnosticEngine()
    res = engine.diagnose_engine_sound(bike_model="Classic 350")
    # Clean behavior: notifies when no audio file is provided rather than faking one
    assert "diagnosis" in res
    assert "audio file" in res["diagnosis"].lower() or res["success"] is False


def test_vision_part_scanner():
    scanner = REVisionPartScanner()
    res = scanner.identify_part_from_image(part_hint="oil filter")
    assert res["success"] is True
    assert "oil filter" in res["report"].lower() or "574050" in res["report"]


def test_riders_club_manager():
    mgr = ChamundaRidersClubManager()
    ev = mgr.create_event(
        title="Official Thump Ride",
        date="Next Sunday 6:00 AM",
        destination="Highway Route",
        perks="Free chain lube"
    )
    assert ev["event_id"].startswith("RIDE-")
    events = mgr.get_all_events()
    assert len(events) >= 1


def test_wholesale_po_engine():
    po = WholesalePOEngine()
    res = po.generate_low_stock_purchase_order()
    assert "PO-CAPS-" in res["po_number"]
    assert res["total_outlay_inr"] > 0


def test_wake_word_and_shadow_copilot():
    wake = WakeWordListener()
    assert "armed" in wake.start().lower()
    assert "deactivated" in wake.stop().lower()

    shadow = SilentShadowCopilot()
    assert "monitoring" in shadow.start().lower()
    assert "paused" in shadow.stop().lower()


def test_price_scraper_and_optimizer():
    opt = PriceScraperAndOptimizer()
    res = opt.benchmark_and_optimize_pricing()
    assert len(res["benchmarks"]) > 0
    assert "margin" in res["report"].lower()
