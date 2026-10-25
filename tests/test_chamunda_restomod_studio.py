"""
Unit & Integration Tests for Chamunda AI:
Royal Enfield Custom Resto-Mod, Vintage Cast-Iron (CI) Heavy Crank Rebirth & Performance Dyno Studio Engine.
"""

import sys
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure paths
SYS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SYS_DIR))
sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")

from restomod_studio_engine import (
    ChamundaRestoModStudio,
    RESTOMOD_STYLES,
    CUSTOM_PAINT_THEMES,
    PERFORMANCE_STAGES,
    VINTAGE_CI_SPECS,
    VINTAGE_CI_FAULTS,
    RESTOMODS_DIR
)
from tools.chamunda_ceo_tools import (
    chamunda_build_custom_restomod_quote,
    chamunda_calculate_performance_stage_tune,
    chamunda_diagnose_vintage_ci_bullet
)
from core.offline_commander import OfflineCommander
from app import app


@pytest.fixture
def studio():
    return ChamundaRestoModStudio()


@pytest.fixture
def client():
    return TestClient(app)


def test_restomod_quote_generation_all_styles(studio):
    """Verify quote calculation, BOM generation, timeline, and QR blueprint for all 4 styles."""
    styles = ["bobber_solo", "cafe_racer", "desert_scrambler", "vintage_heritage_standard"]

    for st in styles:
        quote = studio.generate_restomod_quote(
            customer_name="Test Rider",
            phone="+91 98250 11223",
            bike_model="Classic 350 Reborn",
            registration_no="GJ-01-AB-1234",
            style_key=st,
            paint_theme_key="british_racing_green_gold",
            performance_stage_key="stage_1_street_thump",
            include_vintage_ci_package=False,
            custom_notes="Custom test build"
        )
        assert quote["resto_id"].startswith("RESTO-RE-")
        assert quote["grand_total"] > 50000
        assert quote["timeline_days"] >= 12
        assert len(quote["bom_parts"]) >= 4
        assert len(quote["qr_code_base64"]) > 50
        assert Path(quote["blueprint_html_path"]).exists()

        # Check cost breakdown integrity
        cb = quote["cost_breakdown"]
        expected_total = cb["style_labor"] + cb["paint_finish"] + cb["performance_tuning"] + cb["vintage_ci_package"] + cb["bom_spares"]
        assert quote["grand_total"] == expected_total


def test_vintage_ci_heavy_crank_rebirth_package(studio):
    """Verify inclusion of Vintage CI heavy crank rebirth package adds 12500 INR and 7 days."""
    quote_without = studio.generate_restomod_quote(
        customer_name="Kishorbhai Parmar",
        phone="+91 98250 44551",
        bike_model="Bullet 350 Cast-Iron CI",
        registration_no="GJ-01-AB-1982",
        style_key="bobber_solo",
        paint_theme_key="matte_phantom_black",
        performance_stage_key="stage_1_street_thump",
        include_vintage_ci_package=False
    )

    quote_with = studio.generate_restomod_quote(
        customer_name="Kishorbhai Parmar",
        phone="+91 98250 44551",
        bike_model="Bullet 350 Cast-Iron CI",
        registration_no="GJ-01-AB-1982",
        style_key="bobber_solo",
        paint_theme_key="matte_phantom_black",
        performance_stage_key="stage_1_street_thump",
        include_vintage_ci_package=True
    )

    assert quote_with["cost_breakdown"]["vintage_ci_package"] == 12500
    assert quote_with["grand_total"] == quote_without["grand_total"] + 12500
    assert quote_with["timeline_days"] == quote_without["timeline_days"] + 7


def test_dyno_performance_stage_tuning_gains(studio):
    """Verify Stage 1 and Stage 2 dyno calculations across Classic 350, Himalayan 450, and 650 Twins."""
    # Stage 1 on Classic 350
    dyno_st1 = studio.calculate_performance_stage(bike_model="Classic 350 Reborn", stage_key="stage_1_street_thump")
    assert dyno_st1["baseline_hp"] == 20.2
    assert dyno_st1["tuned_hp"] == 23.6  # 20.2 + 3.4
    assert dyno_st1["baseline_torque_nm"] == 27.0
    assert dyno_st1["tuned_torque_nm"] == 31.2  # 27.0 + 4.2
    assert dyno_st1["rto_legal"] is True
    assert dyno_st1["exhaust_decibel"] < 85.0
    assert len(dyno_st1["required_spares"]) >= 3

    # Stage 2 on Interceptor 650
    dyno_st2 = studio.calculate_performance_stage(bike_model="Interceptor 650", stage_key="stage_2_dyno_sprint")
    assert dyno_st2["baseline_hp"] == 47.0
    assert dyno_st2["tuned_hp"] == 54.2  # 47.0 + 7.2
    assert dyno_st2["baseline_torque_nm"] == 52.0
    assert dyno_st2["tuned_torque_nm"] == 60.6  # 52.0 + 8.6
    assert dyno_st2["rto_legal"] is True
    assert dyno_st2["exhaust_decibel"] <= 85.0


def test_vintage_cast_iron_bullet_diagnostics(studio):
    """Verify Vintage CI mechanical diagnostic rules for CB points, tappets, kickback, and Albion gearbox."""
    # 1. Contact Breaker Points
    diag_cb = studio.diagnose_vintage_ci_bullet("cb point gap misfire at high speed")
    assert "point_pitted_misfire" in diag_cb["fault_key"]
    assert "૦.૩૫ mm" in diag_cb["mechanic_directive_gu"]
    assert "0.35 mm" in diag_cb["mechanic_directive_en"]
    assert len(diag_cb["parts_needed"]) >= 1

    # 2. Pushrod Tappets
    diag_tappet = studio.diagnose_vintage_ci_bullet("pushrod clatter excessive tappet noise")
    assert "pushrod_tappet_noise" in diag_tappet["fault_key"]
    assert "પુશરોડ" in diag_tappet["mechanic_directive_gu"]
    assert "zero lash" in diag_tappet["mechanic_directive_en"].lower()

    # 3. Kickback & Timing
    diag_timing = studio.diagnose_vintage_ci_bullet("severe kickback timing advance")
    assert "kickback_timing" in diag_timing["fault_key"]
    assert "Top Dead Center" in diag_timing["mechanic_directive_en"]

    # 4. Albion 4-Speed Gearbox
    diag_albion = studio.diagnose_vintage_ci_bullet("albion 4 speed false neutral slipping")
    assert "albion_gear_slip" in diag_albion["fault_key"]
    assert "EP-90" in diag_albion["mechanic_directive_en"]

    # 5. Duckbill Wet Sumping
    diag_sump = studio.diagnose_vintage_ci_bullet("wet sumping oil puking from duckbill breather")
    assert "duckbill_breather_leak" in diag_sump["fault_key"]
    assert "wet sumping" in diag_sump["mechanic_directive_en"].lower()


def test_chamunda_ceo_executive_tools():
    """Verify executive CEO tools return well-structured markdown and hyperlinks."""
    # 1. Build Quote Tool
    q_md = chamunda_build_custom_restomod_quote(
        customer_name="Maheshbhai",
        phone="+91 98250 99999",
        bike_model="Bullet 350 Cast-Iron CI",
        registration_no="GJ-01-XX-1980",
        style_key="bobber_solo",
        paint_theme_key="matte_phantom_black",
        performance_stage_key="stage_1_street_thump",
        include_vintage_ci_package=True
    )
    assert "Chamunda AI • Bespoke Resto-Mod &amp; Vintage CI Blueprint" in q_md
    assert "RESTO-RE-" in q_md
    assert "Grand Total Build Cost" in q_md
    assert "http://127.0.0.1:8080/restomod/" in q_md

    # 2. Performance Tune Tool
    tune_md = chamunda_calculate_performance_stage_tune(
        bike_model="Classic 350 Reborn",
        stage_key="stage_2_dyno_sprint"
    )
    assert "Dyno Performance Calibration Analysis" in tune_md
    assert "Peak Power:" in tune_md
    assert "RTO Legal Compliant" in tune_md

    # 3. Vintage CI Diagnose Tool
    ci_md = chamunda_diagnose_vintage_ci_bullet("cb point gap misfire")
    assert "Vintage Cast-Iron (CI) Bullet Rebirth Diagnosis" in ci_md
    assert "ગુજરાતી (Gujarati):" in ci_md
    assert "Factory Specification & Tolerance:" in ci_md


def test_offline_commander_restomod_and_vintage_routing():
    """Verify offline voice commander routes natural Gujarati and English inputs accurately."""
    oc = OfflineCommander()

    # 1. Gujarati Vintage CI query
    res_gu_ci = oc.execute_offline_turn("વિન્ટેજ બુલેટ cb પોઇન્ટ મિસફાયર ચેક કરો")
    assert "વિન્ટેજ કાસ્ટ-આયર્ન (CI) હેવી ક્રેન્ક બુલેટ ડાયગ્નોસિસ" in res_gu_ci

    # 2. English Dyno query
    res_en_dyno = oc.execute_offline_turn("run classic 350 dyno tune stage 2")
    assert "Dyno Performance" in res_en_dyno

    # 3. Gujarati Resto-Mod quote query
    res_gu_resto = oc.execute_offline_turn("રોયલ એનફિલ્ડ બુલેટ માટે બોબર રેસ્ટોમોડ ક્વોટ બનાવો")
    assert "કસ્ટમ રેસ્ટો-મોડ" in res_gu_resto or "Bespoke Royal Enfield" in res_gu_resto


def test_fastapi_restomod_endpoints(client):
    """Verify all 6 FastAPI REST endpoints for the Resto-Mod & Vintage CI Studio."""
    # 1. POST /api/restomod/quote
    resp_q = client.post("/api/restomod/quote", json={
        "customer_name": "API Tester",
        "phone": "+91 99988 77665",
        "bike_model": "Classic 350 Reborn",
        "registration_no": "GJ-01-API-99",
        "style_key": "cafe_racer",
        "paint_theme_key": "british_racing_green_gold",
        "performance_stage_key": "stage_1_street_thump",
        "include_vintage_ci_package": False,
        "custom_notes": "Tested via pytest client"
    })
    assert resp_q.status_code == 200
    q_data = resp_q.json()
    resto_id = q_data["resto_id"]
    assert resto_id.startswith("RESTO-RE-")

    # 2. POST /api/restomod/performance-tune
    resp_tune = client.post("/api/restomod/performance-tune", json={
        "bike_model": "Himalayan 450",
        "stage_key": "stage_1_street_thump"
    })
    assert resp_tune.status_code == 200
    assert resp_tune.json()["tuned_hp"] > resp_tune.json()["stock_hp"]

    # 3. POST /api/restomod/vintage-ci-diagnose
    resp_diag = client.post("/api/restomod/vintage-ci-diagnose", json={
        "symptom_query": "pushrod tappet rattle clatter"
    })
    assert resp_diag.status_code == 200
    assert "pushrod_tappet_noise" in resp_diag.json()["fault_key"]

    # 4. GET /api/restomod/blueprint/{resto_id}
    resp_bp = client.get(f"/api/restomod/blueprint/{resto_id}")
    assert resp_bp.status_code == 200
    assert resp_bp.json()["customer_name"] == "API Tester"

    # 5. GET /restomod/{resto_id} (HTML view)
    resp_html = client.get(f"/restomod/{resto_id}")
    assert resp_html.status_code == 200
    assert "<!DOCTYPE html>" in resp_html.text or "CHAMUNDA" in resp_html.text

    # 6. GET /api/restomod/recent
    resp_rec = client.get("/api/restomod/recent?limit=10")
    assert resp_rec.status_code == 200
    assert isinstance(resp_rec.json(), list)
    assert len(resp_rec.json()) >= 1
