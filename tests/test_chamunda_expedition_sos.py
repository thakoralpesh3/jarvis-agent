"""
Unit & Integration Tests for Chamunda AI:
Royal Enfield Expedition Readiness, Carry-Along Spares Kit Builder & 24/7 Gujarat Highway SOS Shield.
"""

import sys
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure paths
SYS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SYS_DIR))
sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")

from expedition_sos_engine import ChamundaExpeditionManager, TOURING_DESTINATIONS, SOS_ROAD_FAULTS, EXPEDITIONS_DIR
from tools.chamunda_ceo_tools import (
    chamunda_audit_expedition_readiness,
    chamunda_build_carry_along_spares_kit,
    chamunda_highway_breakdown_sos_triage
)
from core.offline_commander import OfflineCommander
from app import app


@pytest.fixture
def expedition_mgr():
    return ChamundaExpeditionManager()


@pytest.fixture
def client():
    return TestClient(app)


def test_expedition_audit_scoring_and_tiers(expedition_mgr):
    """Verify 48-point scoring, clearance tiers, QR generation, and HTML passport creation."""
    # 1. High Score -> LADAKH EXPEDITION READY (>= 90)
    audit_ladakh = expedition_mgr.conduct_expedition_audit(
        rider_name="Alpesh Patel",
        phone="+91 98250 54321",
        bike_model="Himalayan 450",
        registration_no="GJ-01-RE-4500",
        destination_key="ladakh_high_altitude",
        planned_km=4200,
        domain_scores={
            "engine_altitude": 20,
            "suspension_load": 19,
            "electricals_cold": 15,
            "brakes_fluid": 15,
            "tyres_terrain": 15,
            "survival_pack": 15
        }
    )
    assert audit_ladakh["total_score"] >= 90.0
    assert "LADAKH READY" in audit_ladakh["clearance_tier"]
    assert audit_ladakh["clearance_granted"] is True
    assert "24/7 GPS SOS Guard" in audit_ladakh["sos_shield"]
    assert audit_ladakh["qr_code_base64"].startswith("data:image/png;base64,")
    assert Path(audit_ladakh["passport_html_file"]).exists()
    assert len(audit_ladakh["carry_along_spares"]) >= 5

    # 2. Moderate Score -> HIGHWAY TOURING CLEARED (80 - 89)
    audit_hwy = expedition_mgr.conduct_expedition_audit(
        rider_name="Ketan Parmar",
        phone="+91 98251 11223",
        bike_model="Classic 350",
        registration_no="GJ-01-KP-3500",
        destination_key="coastal_highway",
        planned_km=1800,
        domain_scores={
            "engine_altitude": 17,
            "suspension_load": 17,
            "electricals_cold": 12,
            "brakes_fluid": 12,
            "tyres_terrain": 13,
            "survival_pack": 12
        }
    )
    assert 80.0 <= audit_hwy["total_score"] < 90.0
    assert "HIGHWAY TOURING" in audit_hwy["clearance_tier"]
    assert audit_hwy["clearance_granted"] is True

    # 3. Marginal Score -> SHORT RUN ONLY (< 80)
    audit_marginal = expedition_mgr.conduct_expedition_audit(
        rider_name="Test Rider",
        phone="+91 98000 11111",
        bike_model="Bullet 350",
        registration_no="GJ-01-XX-1111",
        destination_key="desert_run",
        planned_km=2500,
        domain_scores={
            "engine_altitude": 14,
            "suspension_load": 12,
            "electricals_cold": 10,
            "brakes_fluid": 10,
            "tyres_terrain": 10,
            "survival_pack": 10
        }
    )
    assert audit_marginal["total_score"] < 80.0
    assert "SHORT RUN" in audit_marginal["clearance_tier"] or "NOT CLEARED" in audit_marginal["clearance_tier"] or "REJECTED" in audit_marginal["clearance_tier"]


def test_carry_along_spares_kit_builder(expedition_mgr):
    """Verify custom carry-along backup spares kit packaged from 4,469 parts catalog."""
    # 1. Himalayan 450 for Ladakh
    kit_himalayan = expedition_mgr.build_carry_along_spares_kit(
        bike_model="Himalayan 450",
        destination_key="ladakh_high_altitude"
    )
    assert kit_himalayan["bike_model"] == "Himalayan 450"
    assert "Ladakh" in kit_himalayan["destination"]
    assert kit_himalayan["item_count"] >= 5
    assert kit_himalayan["total_estimated_cost_inr"] > 1000

    # Ensure key survival spares exist in kit
    item_names = [i["name"].lower() for i in kit_himalayan["items"]]
    assert any("clutch" in n for n in item_names)
    assert any("plug" in n or "spark" in n for n in item_names)
    assert any("chain" in n or "lube" in n for n in item_names)
    assert any("fuse" in n for n in item_names)

    # 2. Classic 350 for Desert Run
    kit_classic = expedition_mgr.build_carry_along_spares_kit(
        bike_model="Classic 350",
        destination_key="desert_run"
    )
    assert kit_classic["bike_model"] == "Classic 350"
    assert kit_classic["item_count"] >= 5


def test_highway_sos_breakdown_triage(expedition_mgr):
    """Verify 24/7 roadside emergency breakdown diagnostic triage and bilingual directives."""
    # 1. Clutch cable snap
    sos_clutch = expedition_mgr.highway_sos_triage("clutch wire snapped on Ahmedabad highway NH 48")
    assert "Clutch" in sos_clutch["fault_category"]
    assert sos_clutch["urgency"] == "HIGH (Immobilized)"
    assert "safety_protocol" in sos_clutch
    assert len(sos_clutch["roadside_fix_steps"]) > 0
    assert "emergency" in sos_clutch["english_directive"].lower() or "clutch" in sos_clutch["english_directive"].lower()
    assert "ક્લચ" in sos_clutch["gujarati_directive"]
    assert "+91 98250 12345" in sos_clutch["helpline_24x7"]

    # 2. Engine overheating
    sos_heat = expedition_mgr.highway_sos_triage("engine overheating smoke steam coming from radiator")
    assert "Engine" in sos_heat["fault_category"] or "Overheat" in sos_heat["fault_category"]
    assert "ઓવરહીટ" in sos_heat["gujarati_directive"] or "એન્જિન" in sos_heat["gujarati_directive"]

    # 3. Flat tubeless puncture
    sos_punc = expedition_mgr.highway_sos_triage("rear tyre puncture air leaking fast at night")
    assert "Puncture" in sos_punc["fault_category"] or "Tyre" in sos_punc["fault_category"]
    assert "ટાયર" in sos_punc["gujarati_directive"] or "પંચર" in sos_punc["gujarati_directive"]

    # 4. Dead battery / EFI
    sos_bat = expedition_mgr.highway_sos_triage("battery dead efi fuel pump not priming no display")
    assert "Dead" in sos_bat["fault_category"] or "Starter" in sos_bat["fault_category"] or "Battery" in sos_bat["fault_category"]

    # 5. Snapped chain
    sos_chain = expedition_mgr.highway_sos_triage("drive chain broke sprocket jam")
    assert "Chain" in sos_chain["fault_category"]


def test_ceo_tools_expedition_and_sos():
    """Verify executive CEO tools for expedition readiness audit, spares kit, and highway SOS."""
    # 1. Expedition Audit Tool
    res_audit = chamunda_audit_expedition_readiness(
        rider_name="Alpesh Patel",
        phone="+91 98250 54321",
        bike_model="Himalayan 450",
        registration_no="GJ-01-RE-4500",
        destination_key="ladakh_high_altitude",
        planned_km=4200
    )
    assert "Chamunda Royal Enfield Expedition Pre-Flight Clearance" in res_audit
    assert "EXP-RE-" in res_audit
    assert "Himalayan 450" in res_audit
    assert "Tour Endurance Score" in res_audit
    assert "6 Touring Survival Domains Breakdown" in res_audit
    assert "Essential Carry-Along Spares Kit" in res_audit

    # 2. Carry-Along Spares Kit Tool
    res_kit = chamunda_build_carry_along_spares_kit("Himalayan 450", "ladakh_high_altitude")
    assert "Chamunda AI • Expedition Carry-Along Spares Kit" in res_kit
    assert "Himalayan 450" in res_kit
    assert "Essential Spares Packing List" in res_kit

    # 3. Highway Breakdown SOS Tool
    res_sos = chamunda_highway_breakdown_sos_triage("clutch cable snapped on national highway")
    assert "Chamunda 24/7 Gujarat Highway Breakdown SOS Shield" in res_sos
    assert "Roadside Safety Protocol" in res_sos
    assert "Immediate Roadside Fix Steps" in res_sos
    assert "Mechanic Directives (દ્વિભાષી / Bilingual)" in res_sos
    assert "+91 98250 12345" in res_sos


def test_offline_commander_expedition_and_sos_routing():
    """Verify offline autonomous intent routing in Gujarati and English for expedition & SOS."""
    commander = OfflineCommander()

    # 1. Gujarati Expedition Audit Command
    gu_audit = commander.execute_offline_turn("રોયલ એનફિલ્ડ Himalayan 450 GJ-01-RE-2024 નું લદાખ ટૂર ઓડિટ અને એક્સપિડિશન ક્લિયરન્સ ચેક કરો")
    assert "૪૮-પોઇન્ટ એક્સપિડિશન પ્રી-ટુર ઓડિટ" in gu_audit or "48-Point Expedition" in gu_audit
    assert "EXP-RE-" in gu_audit
    assert "Himalayan 450" in gu_audit

    # 2. English Spares Kit Command
    en_kit = commander.execute_offline_turn("Generate carry along touring spares kit for Himalayan 450")
    assert "Carry-Along Backup Spares Kit" in en_kit or "કસ્ટમ એક્સપિડિશન કેરી-અલોંગ બેકઅપ સ્પેર કીટ" in en_kit
    assert "Himalayan 450" in en_kit

    # 3. Emergency Highway SOS Command in Gujarati
    gu_sos = commander.execute_offline_turn("હાઇવે પર ક્લચ વાયર તૂટી ગયો છે તાત્કાલિક SOS મદદ જોઈએ છે")
    assert "ગુજરાત હાઇવે બ્રેકડાઉન SOS" in gu_sos or "Highway Breakdown SOS" in gu_sos
    assert "Clutch" in gu_sos
    assert "+91 98250 12345" in gu_sos


def test_fastapi_expedition_endpoints(client):
    """Verify all 6 REST API endpoints for expedition pre-touring audit, kit builder, and SOS triage."""
    # 1. POST /api/expedition/audit
    r_audit = client.post("/api/expedition/audit", json={
        "rider_name": "Alpesh Patel",
        "phone": "+91 98250 54321",
        "bike_model": "Himalayan 450",
        "registration_no": "GJ-01-AP-4500",
        "destination_key": "ladakh_high_altitude",
        "planned_km": 3800,
        "domain_scores": {
            "engine_altitude": 19,
            "suspension_load": 18,
            "electricals_cold": 15,
            "brakes_fluid": 14,
            "tyres_terrain": 14,
            "survival_pack": 14
        }
    })
    assert r_audit.status_code == 200
    aud_data = r_audit.json()
    exp_id = aud_data["expedition_id"]
    assert exp_id.startswith("EXP-RE-")
    assert aud_data["total_score"] >= 90.0
    assert "LADAKH READY" in aud_data["clearance_tier"]

    # 2. POST /api/expedition/spares-kit
    r_kit = client.post("/api/expedition/spares-kit", json={
        "bike_model": "Classic 350",
        "destination_key": "coastal_highway"
    })
    assert r_kit.status_code == 200
    kit_data = r_kit.json()
    assert kit_data["bike_model"] == "Classic 350"
    assert len(kit_data["items"]) >= 5

    # 3. POST /api/expedition/sos-triage
    r_sos = client.post("/api/expedition/sos-triage", json={
        "symptom_query": "engine overheating steam coming out"
    })
    assert r_sos.status_code == 200
    sos_data = r_sos.json()
    assert "Heat" in sos_data["fault_category"] or "Overheat" in sos_data["fault_category"] or "Engine" in sos_data["fault_category"]
    assert "gujarati_directive" in sos_data

    # 4. GET /api/expedition/passport/{exp_id}
    r_pass = client.get(f"/api/expedition/passport/{exp_id}")
    assert r_pass.status_code == 200
    pass_data = r_pass.json()
    assert pass_data["rider_name"] == "Alpesh Patel"
    assert pass_data["expedition_id"] == exp_id

    # 5. GET /expedition/{exp_id} (HTML Passport Viewer)
    r_html = client.get(f"/expedition/{exp_id}")
    assert r_html.status_code == 200
    passport_markup = r_html.text
    assert "CHAMUNDA EXPEDITION SHIELD" in passport_markup or "Expedition Passport" in passport_markup
    assert exp_id in passport_markup
    assert "GJ-01-AP-4500" in passport_markup
    assert "48-Point" in passport_markup

    # 6. GET /api/expedition/recent
    r_rec = client.get("/api/expedition/recent?limit=10")
    assert r_rec.status_code == 200
    recent_list = r_rec.json()
    assert isinstance(recent_list, list)
    assert len(recent_list) > 0

    # 7. GET / Dashboard Tab 9 Integration
    r_dash = client.get("/")
    assert r_dash.status_code == 200
    dash_html = r_dash.text
    assert "Expedition Readiness" in dash_html
    assert "expedition-sos" in dash_html
    assert "48-Point Expedition Pre-Touring" in dash_html
    assert "Highway SOS" in dash_html
