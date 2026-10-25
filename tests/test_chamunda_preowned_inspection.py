"""
Unit & Integration Tests for Chamunda AI:
Certified Pre-Owned Royal Enfield & 100-Point Digital Inspection Shield Engine.
"""

import sys
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure paths
SYS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SYS_DIR))
sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")

from used_bike_inspection_engine import ChamundaPreOwnedManager, OEM_BASE_PRICES, INSPECTIONS_DIR
from tools.chamunda_ceo_tools import (
    chamunda_inspect_preowned_bike,
    chamunda_evaluate_market_valuation
)
from core.offline_commander import OfflineCommander
from app import app


@pytest.fixture
def preowned_mgr():
    return ChamundaPreOwnedManager()


@pytest.fixture
def client():
    return TestClient(app)


def test_fair_market_valuation_algorithm(preowned_mgr):
    """Verify AI valuation calculation across different models, ages, and mileages."""
    # 1. Classic 350 (2022, 18,000 km, 85 condition)
    val1 = preowned_mgr.calculate_fair_market_valuation("Classic 350", 2022, 18000, 85.0)
    assert val1["bike_model"] == "Classic 350"
    assert val1["manufacturing_year"] == 2022
    assert val1["fair_market_value_inr"] > 100000
    assert val1["recommended_buyer_price_inr"] < val1["fair_market_value_inr"]
    assert val1["recommended_seller_asking_inr"] > val1["fair_market_value_inr"]
    assert "HIGH" in val1["gujarat_market_demand"]

    # 2. Himalayan 450 (2024, 5,000 km, 95 condition)
    val2 = preowned_mgr.calculate_fair_market_valuation("Himalayan 450", 2024, 5000, 95.0)
    assert val2["fair_market_value_inr"] > 200000
    assert val2["original_ex_showroom_est"] == OEM_BASE_PRICES["Himalayan 450"]

    # 3. High mileage penalty check
    val_high_km = preowned_mgr.calculate_fair_market_valuation("Classic 350", 2022, 60000, 85.0)
    val_low_km = preowned_mgr.calculate_fair_market_valuation("Classic 350", 2022, 10000, 85.0)
    assert val_high_km["fair_market_value_inr"] < val_low_km["fair_market_value_inr"]


def test_conduct_100_point_inspection_and_shield_tiers(preowned_mgr):
    """Verify 100-point inspection scoring, shield tier qualification, and certificate generation."""
    # 1. High Score -> PLATINUM CERTIFIED
    platinum_report = preowned_mgr.conduct_100_point_inspection(
        customer_name="Vikram Rathod",
        phone="+91 98250 99887",
        bike_model="Classic 350",
        registration_no="GJ-01-VR-1901",
        manufacturing_year=2023,
        odometer_km=9500,
        checklist_overrides={
            "engine_pts": 25,
            "chassis_pts": 20,
            "acoustic_pts": 15,
            "brakes_pts": 15,
            "electrical_pts": 15,
            "aesthetics_pts": 10
        }
    )
    assert platinum_report["total_score"] == 100.0
    assert platinum_report["certification_tier"] == "PLATINUM CERTIFIED"
    assert platinum_report["warranty_qualified"] is True
    assert "3-Month" in platinum_report["warranty_shield"]
    assert platinum_report["qr_code_base64"].startswith("data:image/png;base64,")
    assert Path(platinum_report["cert_html_file"]).exists()

    # 2. Moderate Score -> GOLD CERTIFIED
    gold_report = preowned_mgr.conduct_100_point_inspection(
        customer_name="Kishore Solanki",
        phone="+91 98251 22334",
        bike_model="Hunter 350",
        registration_no="GJ-01-KS-3500",
        manufacturing_year=2022,
        odometer_km=22000,
        checklist_overrides={
            "engine_pts": 21,
            "chassis_pts": 17,
            "acoustic_pts": 13,
            "brakes_pts": 12,
            "electrical_pts": 13,
            "aesthetics_pts": 8
        }
    )
    assert 80.0 <= gold_report["total_score"] < 90.0
    assert gold_report["certification_tier"] == "GOLD CERTIFIED"
    assert gold_report["warranty_qualified"] is True
    assert len(gold_report["recommended_spares"]) > 0

    # 3. Fail Score -> REPAIR REQUIRED
    fail_report = preowned_mgr.conduct_100_point_inspection(
        customer_name="Test Fail Case",
        phone="+91 98000 00000",
        bike_model="Bullet 350",
        registration_no="GJ-01-XX-0000",
        manufacturing_year=2016,
        odometer_km=85000,
        checklist_overrides={
            "engine_pts": 12,
            "chassis_pts": 10,
            "acoustic_pts": 8,
            "brakes_pts": 7,
            "electrical_pts": 8,
            "aesthetics_pts": 5
        }
    )
    assert fail_report["total_score"] < 70.0
    assert "NOT CERTIFIED" in fail_report["certification_tier"]
    assert fail_report["warranty_qualified"] is False


def test_ceo_tools_preowned_execution():
    """Verify executive CEO tools for pre-owned inspection and valuation."""
    # 1. Valuation tool
    res_val = chamunda_evaluate_market_valuation("Classic 350", 2022, 18000, 88.0)
    assert "Chamunda AI • Royal Enfield Fair Market Valuation" in res_val
    assert "Classic 350" in res_val
    assert "AI Fair Market Value" in res_val
    assert "Gujarat Regional Demand" in res_val

    # 2. Inspection tool
    res_insp = chamunda_inspect_preowned_bike(
        customer_name="Harshad Mehta",
        phone="+91 98250 55667",
        bike_model="Meteor 350",
        registration_no="GJ-01-HM-3500",
        manufacturing_year=2021,
        odometer_km=25000,
        engine_pts=23,
        chassis_pts=18,
        acoustic_pts=14,
        brakes_pts=14,
        electrical_pts=13,
        aesthetics_pts=8
    )
    assert "Chamunda Certified Pre-Owned Royal Enfield" in res_insp
    assert "CERT-RE-" in res_insp
    assert "Meteor 350" in res_insp
    assert "Total Quality Score" in res_insp
    assert "Warranty Shield" in res_insp
    assert "Category Breakdown" in res_insp


def test_offline_commander_preowned_routing():
    """Verify offline natural language voice/text intent routing in Gujarati and English."""
    commander = OfflineCommander()

    # 1. Pre-Owned Inspection Command in Gujarati
    gu_res = commander.execute_offline_turn("રોયલ એનફિલ્ડ Classic 350 GJ-01-RE-2022 નું 100 point preowned inspection કરો")
    assert "૧૦૦-પોઇન્ટ ડિજિટલ ઇન્સ્પેક્શન" in gu_res or "100-Point Digital" in gu_res
    assert "CERT-RE-" in gu_res
    assert "Classic 350" in gu_res

    # 2. Valuation Command in English
    en_res = commander.execute_offline_turn("Calculate fair market valuation for Hunter 350 2023 12000 km")
    assert "Fair Market Valuation" in en_res or "ફેર માર્કેટ વેલ્યુએશન" in en_res
    assert "Hunter 350" in en_res
    assert "₹" in en_res


def test_fastapi_preowned_endpoints(client):
    """Verify all REST API endpoints for pre-owned valuation, inspection, and verification."""
    # 1. POST /api/preowned/valuation
    r_val = client.post("/api/preowned/valuation", json={
        "bike_model": "Classic 350",
        "manufacturing_year": 2022,
        "odometer_km": 18000,
        "condition_score": 85.0
    })
    assert r_val.status_code == 200
    val_data = r_val.json()
    assert "fair_market_value_inr" in val_data
    assert val_data["fair_market_value_inr"] > 100000

    # 2. POST /api/preowned/inspect
    r_insp = client.post("/api/preowned/inspect", json={
        "customer_name": "Narendra Soni",
        "phone": "+91 98250 77889",
        "bike_model": "Interceptor 650",
        "registration_no": "GJ-01-NS-6500",
        "manufacturing_year": 2023,
        "odometer_km": 8000,
        "checklist_overrides": {
            "engine_pts": 24,
            "chassis_pts": 19,
            "acoustic_pts": 15,
            "brakes_pts": 14,
            "electrical_pts": 14,
            "aesthetics_pts": 9
        }
    })
    assert r_insp.status_code == 200
    report = r_insp.json()
    cert_id = report["cert_id"]
    assert cert_id.startswith("CERT-RE-")
    assert report["total_score"] >= 90.0

    # 3. GET /api/preowned/report/{cert_id}
    r_rep = client.get(f"/api/preowned/report/{cert_id}")
    assert r_rep.status_code == 200
    assert r_rep.json()["customer_name"] == "Narendra Soni"

    # 4. GET /certification/{cert_id} (Verifiable HTML Certificate)
    r_cert = client.get(f"/certification/{cert_id}")
    assert r_cert.status_code == 200
    html = r_cert.text
    assert "CHAMUNDA AUTOMOBILE" in html
    assert "CERTIFIED PRE-OWNED ROYAL ENFIELD" in html
    assert cert_id in html
    assert "GJ-01-NS-6500" in html

    # 5. GET /api/preowned/recent
    r_recent = client.get("/api/preowned/recent?limit=10")
    assert r_recent.status_code == 200
    recent = r_recent.json()
    assert isinstance(recent, list)
    assert len(recent) > 0

    # 6. GET / Dashboard Tab 8 Integration
    r_dash = client.get("/")
    assert r_dash.status_code == 200
    dash_html = r_dash.text
    assert "Certified Pre-Owned Inspection" in dash_html
    assert "preowned-inspection" in dash_html
    assert "AI Gujarat Fair Market Valuation" in dash_html
