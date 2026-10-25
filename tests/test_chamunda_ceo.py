"""
Tests for Chamunda Automobile Parts & Service - CEO Executive Tools & Royal Enfield OS.
"""

import tempfile
from pathlib import Path
import pytest
import sys

sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
from inventory_engine import ChamundaInventoryManager
from service_engine import ChamundaServiceManager
from billing_engine import ChamundaBillingManager
from tools.chamunda_ceo_tools import (
    chamunda_lookup_part,
    chamunda_create_job_card,
    chamunda_diagnose_re_bike,
    chamunda_generate_ceo_revenue_report
)


@pytest.fixture
def tmp_chamunda_env():
    with tempfile.TemporaryDirectory() as tmpdir:
        d = Path(tmpdir)
        inv = ChamundaInventoryManager(data_dir=d)
        srv = ChamundaServiceManager(data_dir=d)
        bill = ChamundaBillingManager(data_dir=d)
        yield inv, srv, bill


def test_inventory_search_and_valuation(tmp_chamunda_env):
    inv, _, _ = tmp_chamunda_env
    parts = inv.search_parts("oil filter")
    assert len(parts) >= 1
    assert "oil filter" in parts[0]["name"].lower()

    val = inv.get_total_inventory_valuation()
    assert val["total_distinct_skus"] > 5
    assert val["mrp_valuation_inr"] > val["cost_valuation_inr"]


def test_service_jobcard_and_diagnosis(tmp_chamunda_env):
    _, srv, _ = tmp_chamunda_env
    job = srv.create_job_card(
        customer_name="Aarav Mehta",
        phone="+91 99000 11223",
        bike_model="Classic 350 Reborn",
        registration_no="GJ-01-AB-1234",
        odometer_km=15000,
        customer_issues="Cold start tappet noise"
    )
    assert job["job_card_id"].startswith("JOB-")
    assert "valve clearance" in job["diagnostic_recommendation"].lower()


def test_billing_invoice_generation(tmp_chamunda_env):
    _, _, bill = tmp_chamunda_env
    inv = bill.generate_invoice_html(
        job_card_id="JOB-2026-TEST",
        customer_name="Karan Singh",
        phone="+91 98980 98980",
        bike_model="Continental GT 650",
        registration_no="GJ-01-GT-0650",
        odometer_km=8500,
        parts=[{"name": "Slipper Clutch Assembly", "price": 3850, "qty": 1}],
        labor_charges=750
    )
    assert "CAPS-" in inv["invoice_no"]
    assert inv["grand_total"] > 4500
    assert Path(inv["invoice_file"]).exists()


def test_chamunda_ceo_tools():
    rep = chamunda_generate_ceo_revenue_report()
    assert "CHAMUNDA AUTOMOBILE" in rep
    assert "Royal Enfield" in rep

    diag = chamunda_diagnose_re_bike("tappet sound")
    assert "Valve clearance" in diag or "feeler gauge" in diag

    parts = chamunda_lookup_part("Classic 350")
    assert "Classic 350" in parts
