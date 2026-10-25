"""
Comprehensive Unit & Integration Tests for Project Garjana:
1. Chamunda Bay Voice Engine (Hands-Free Gujarati/English Voice-to-Action)
2. Chamunda B2B Wholesale Spares Network (North Gujarat Partner Garages, Tier Margins, Daily Van Routes)
3. Chamunda Royal Riders Club (CRRC) & Annual Maintenance Contracts (AMC)
4. Agent Commander & CEO Tools Integration
5. FastAPI REST API Endpoints Verification
"""

import sys
import json
import pytest
from pathlib import Path

# Add paths
CHAMUNDA_DIR = Path("/home/alpesh/chamunda_re_enterprise")
JARVIS_DIR = Path("/home/alpesh/jarvis-agent")

sys.path.insert(0, str(CHAMUNDA_DIR))
sys.path.insert(0, str(JARVIS_DIR))

from bay_voice_engine import ChamundaBayVoiceEngine, get_bay_voice_engine
from b2b_wholesale_engine import ChamundaB2BWholesaleManager, get_b2b_wholesale_manager
from riders_club_engine import ChamundaRidersClubManager, get_riders_club_manager
from core.agent_commander import AgentCommander
from tools.chamunda_ceo_tools import (
    chamunda_process_bay_voice_command,
    chamunda_get_b2b_wholesale_overview,
    chamunda_create_b2b_wholesale_order,
    chamunda_manage_amc_membership
)


# ==============================================================================
# 1. BAY VOICE ENGINE TESTS
# ==============================================================================

def test_bay_voice_engine_parse_gujarati():
    engine = get_bay_voice_engine()
    spoken = "આરાધ્યા, ગાડી નંબર GJ-02-BQ-1234 માં લિક્વી મોલી 15W-50 એન્જિન ઓઇલ અને નવું ઓઇલ ફિલ્ટર નાખી દીધું છે, બિલમાં એડ કરી દો."
    parsed = engine.parse_spoken_command(spoken)

    assert parsed["registration_no"] == "GJ-02-BQ-1234"
    assert parsed["language_detected"] == "gu"
    assert len(parsed["parts_allocated"]) >= 2
    part_names = [p["part_name"] for p in parsed["parts_allocated"]]
    assert any("Oil" in name or "Liqui" in name for name in part_names)
    assert any("Filter" in name for name in part_names)


def test_bay_voice_engine_parse_english_and_actions():
    engine = get_bay_voice_engine()
    spoken = "Hey Aradhya, installed new brake pads and checked spark plug on GJ-18-AA-9999"
    parsed = engine.parse_spoken_command(spoken)

    assert "GJ-18" in parsed["registration_no"]
    assert parsed["language_detected"] == "en"
    assert len(parsed["parts_allocated"]) >= 2
    parts_categories = [p["category"] for p in parsed["parts_allocated"]]
    assert "Braking System" in parts_categories or "Ignition & Electrical" in parts_categories


def test_bay_voice_process_action_coordination():
    engine = get_bay_voice_engine()
    spoken = "આરાધ્યા GJ-02-BQ-1234 માં એન્જિન ઓઇલ અને ઓઇલ ફિલ્ટર બદલી નાખ્યું છે"
    res = engine.process_voice_action(
        spoken_text=spoken,
        mechanic_name="Master Tech Ramesh",
        bay_id="Bay 1 (J-Series Platform)"
    )

    assert res["success"] is True
    assert res["registration_no"] == "GJ-02-BQ-1234"
    assert res["parts_count"] >= 2
    assert res["parts_total"] > 0

    # Verify 4-Agent Synchronization
    sync = res["subagent_sync"]
    assert "bay_chief" in sync
    assert "parts_specialist" in sync
    assert "accounts_controller" in sync
    assert "customer_receptionist" in sync
    assert "+91 78747 19139" in sync["customer_receptionist"]

    # Verify Gujarati and English Audio Response
    assert "Master Tech Ramesh" in res["audio_response_gu"]
    assert "GJ-02-BQ-1234" in res["audio_response_gu"]
    assert len(res["audio_response_en"]) > 10


# ==============================================================================
# 2. B2B WHOLESALE SPARES NETWORK TESTS
# ==============================================================================

def test_b2b_wholesale_partner_garages():
    mgr = get_b2b_wholesale_manager()
    garages = mgr.get_garages()
    assert len(garages) >= 5

    # Check that key North Gujarat cities are covered
    cities = [g["city"] for g in garages]
    assert "Patan" in cities
    assert "Unjha" in cities
    assert "Visnagar" in cities
    assert "Kadi" in cities
    assert "Siddhpur" in cities


def test_b2b_wholesale_register_garage():
    mgr = get_b2b_wholesale_manager()
    new_g = mgr.register_garage(
        name="Shree Ram Royal Clinic",
        owner_name="Maheshbhai Prajapati",
        phone="+91 98254 77112",
        city="Vadnagar",
        address="Near Toran Circle, Vadnagar",
        tier="Gold"
    )

    assert new_g["garage_id"].startswith("GAR-VADN")
    assert new_g["tier"] == "Gold"
    assert new_g["preferred_route"] == "Route 2: East Industrial Loop"
    assert new_g["credit_limit_inr"] == 150000


def test_b2b_wholesale_order_pricing_and_creation():
    mgr = get_b2b_wholesale_manager()
    items = [
        {"part_number": "574050/C", "name": "Genuine Oil Filter Element", "mrp": 210, "quantity": 10},
        {"part_number": "147008/A", "name": "OEM Pleated Air Filter", "mrp": 380, "quantity": 5}
    ]
    calc = mgr.calculate_order_pricing("GAR-PATAN-001", items)

    # GAR-PATAN-001 is Gold tier -> 20% discount
    assert calc["discount_pct"] == 20.0
    mrp_expected = (210 * 10) + (380 * 5)  # 2100 + 1900 = 4000
    assert calc["mrp_total_inr"] == mrp_expected
    assert calc["discount_amount_inr"] == mrp_expected * 0.20  # 800
    subtotal = mrp_expected - 800  # 3200
    assert calc["subtotal_inr"] == subtotal
    gst = round(subtotal * 0.18, 2)  # 576.0
    assert calc["gst_amount_inr"] == gst
    assert calc["net_payable_inr"] == subtotal + gst  # 3776.0

    # Create Order
    order = mgr.create_order(
        garage_id="GAR-PATAN-001",
        items=items,
        payment_mode="Credit (15 Days)"
    )
    assert order["order_id"].startswith("B2B-")
    assert order["net_payable_inr"] == 3776.0
    assert order["qr_code_b64"].startswith("data:image/png;base64,")


def test_b2b_wholesale_delivery_routes_and_overview():
    mgr = get_b2b_wholesale_manager()
    routes = mgr.get_delivery_routes()
    assert len(routes) == 3
    route_names = [r["name"] for r in routes]
    assert any("North Highway Corridor" in n for n in route_names)
    assert any("East Industrial Loop" in n for n in route_names)
    assert any("South GIDC Express" in n for n in route_names)

    ov = mgr.get_overview()
    assert ov["partner_garages_count"] >= 5
    assert ov["total_orders_count"] >= 1
    assert ov["total_wholesale_revenue_inr"] > 0


# ==============================================================================
# 3. RIDERS CLUB & AMC ENGINE TESTS
# ==============================================================================

def test_riders_club_amc_plans():
    mgr = get_riders_club_manager()
    plans = mgr.get_amc_plans()
    assert len(plans) == 3

    plan_ids = [p["plan_id"] for p in plans]
    assert "AMC-SILVER" in plan_ids
    assert "AMC-GOLD" in plan_ids
    assert "AMC-PLATINUM" in plan_ids

    silver = next(p for p in plans if p["plan_id"] == "AMC-SILVER")
    gold = next(p for p in plans if p["plan_id"] == "AMC-GOLD")
    plat = next(p for p in plans if p["plan_id"] == "AMC-PLATINUM")

    assert silver["annual_fee_inr"] == 3999
    assert gold["annual_fee_inr"] == 7499
    assert plat["annual_fee_inr"] == 11999
    assert gold["parts_discount_pct"] == 10.0
    assert plat["parts_discount_pct"] == 15.0


def test_riders_club_enrollment_and_expeditions():
    mgr = get_riders_club_manager()
    member = mgr.enroll_member(
        name="Kailashbhai Desai",
        phone="+91 98259 88331",
        bike_model="Meteor 350 Supernova",
        registration_no="GJ-02-MN-4455",
        plan_id="AMC-GOLD"
    )

    assert member["member_id"].startswith("CRRC-")
    assert member["tier"] == "Gold Tourer Pass"
    assert member["thump_points"] == 500
    assert member["services_remaining"] == 4

    # Test Expedition Listing & Registration
    expeditions = mgr.get_expeditions()
    assert len(expeditions) >= 2
    polo_exp = next(e for e in expeditions if "POLO" in e["expedition_id"])

    reg_res = mgr.register_for_expedition(
        expedition_id=polo_exp["expedition_id"],
        rider_name="Kailashbhai Desai",
        phone="+91 98259 88331",
        bike_model="Meteor 350 Supernova"
    )
    assert reg_res["success"] is True
    assert "Chamunda Expedition SOS" in reg_res["escort_assigned"]


# ==============================================================================
# 4. AGENT COMMANDER & CEO TOOLS TESTS
# ==============================================================================

def test_agent_commander_voice_and_b2b():
    commander = AgentCommander()
    # Voice Directive
    v_res = commander.execute_bay_voice_directive(
        spoken_text="આરાધ્યા, GJ-02-BQ-1234 માં લિક્વી મોલી ઓઇલ નાખી દીધું છે"
    )
    assert v_res["success"] is True
    assert "bay_chief" in v_res["subagent_sync"]

    # B2B Directive
    b_res = commander.execute_b2b_wholesale_directive(
        garage_id="GAR-PATAN-001",
        items=[{"part_number": "574050/C", "mrp": 210, "quantity": 5}]
    )
    assert b_res["order_id"].startswith("B2B-")


def test_ceo_voice_b2b_and_club_tools():
    # 1. Bay Voice Tool
    v_out = chamunda_process_bay_voice_command(
        spoken_text="આરાધ્યા GJ-02-BQ-1234 માં ઓઇલ ફિલ્ટર બદલી નાખ્યું છે"
    )
    assert "Bay Hands-Free Voice-to-Action Execution" in v_out
    assert "Master Tech Ramesh" in v_out
    assert "+91 78747 19139" in v_out

    # 2. B2B Wholesale Overview Tool
    b_ov = chamunda_get_b2b_wholesale_overview()
    assert "Chamunda B2B Wholesale Genuine Spares Network" in b_ov
    assert "Route 1" in b_ov

    # 3. B2B Order Creation Tool
    b_ord = chamunda_create_b2b_wholesale_order(
        garage_id="GAR-VISN-003",
        items_json='[{"part_number": "574050/C", "name": "Oil Filter", "mrp": 210, "quantity": 10}]'
    )
    assert "Chamunda B2B Wholesale Order Dispatched" in b_ord
    assert "Mahadev RE Clinic" in b_ord

    # 4. AMC Membership Tool
    club_plans = chamunda_manage_amc_membership(action="list_plans")
    assert "Silver Thump Pass" in club_plans
    assert "Gold Tourer Pass" in club_plans

    club_ov = chamunda_manage_amc_membership(action="overview")
    assert "Chamunda Royal Riders Club" in club_ov

    club_enr = chamunda_manage_amc_membership(
        action="enroll",
        name="Jayeshbhai Patel",
        phone="+91 94280 55443",
        bike_model="Continental GT 650",
        registration_no="GJ-02-GT-6500",
        plan_id="AMC-PLATINUM"
    )
    assert "Member Enrolled" in club_enr
    assert "Platinum Vintage & Twin" in club_enr


# ==============================================================================
# 5. FASTAPI REST API ENDPOINTS TESTS
# ==============================================================================

def test_fastapi_voice_b2b_club_endpoints():
    from fastapi.testclient import TestClient
    from app import app
    client = TestClient(app)

    # 1. POST /api/voice/process
    v_resp = client.post("/api/voice/process", json={
        "spoken_text": "આરાધ્યા GJ-02-BQ-1234 માં એન્જિન ઓઇલ અને ઓઇલ ફિલ્ટર બદલી નાખ્યું છે",
        "mechanic_name": "Master Tech Ramesh"
    })
    assert v_resp.status_code == 200
    v_data = v_resp.json()
    assert v_data["success"] is True
    assert v_data["registration_no"] == "GJ-02-BQ-1234"

    # 2. GET /api/voice/logs
    v_logs = client.get("/api/voice/logs")
    assert v_logs.status_code == 200
    assert len(v_logs.json()) >= 1

    # 3. GET /api/b2b/overview
    b_ov = client.get("/api/b2b/overview")
    assert b_ov.status_code == 200
    assert b_ov.json()["partner_garages_count"] >= 5

    # 4. GET /api/b2b/garages
    b_garages = client.get("/api/b2b/garages")
    assert b_garages.status_code == 200
    assert len(b_garages.json()) >= 5

    # 5. POST /api/b2b/orders/create
    b_ord = client.post("/api/b2b/orders/create", json={
        "garage_id": "GAR-PATAN-001",
        "items": [{"part_number": "574050/C", "mrp": 210, "quantity": 5}],
        "payment_mode": "Credit"
    })
    assert b_ord.status_code == 200
    assert b_ord.json()["order_id"].startswith("B2B-")

    # 6. GET /api/b2b/routes
    b_routes = client.get("/api/b2b/routes")
    assert b_routes.status_code == 200
    assert len(b_routes.json()) == 3

    # 7. GET /api/club/amc/plans
    c_plans = client.get("/api/club/amc/plans")
    assert c_plans.status_code == 200
    assert len(c_plans.json()) == 3

    # 8. POST /api/club/members/enroll
    c_enr = client.post("/api/club/members/enroll", json={
        "name": "Arjunsinh Vaghela",
        "phone": "+91 97230 11009",
        "bike_model": "Classic 350 Stealth Black",
        "registration_no": "GJ-02-SB-3322",
        "plan_id": "AMC-GOLD"
    })
    assert c_enr.status_code == 200
    assert c_enr.json()["member_id"].startswith("CRRC-")

    # 9. GET /api/club/expeditions
    c_exp = client.get("/api/club/expeditions")
    assert c_exp.status_code == 200
    assert len(c_exp.json()) >= 2
