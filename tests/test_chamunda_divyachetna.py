"""
Unit and Integration Test Suite for Project Divya-Drishti & Night-Guardian (પ્રોજેક્ટ દિવ્ય-દ્રષ્ટિ & રાત્રિ-સંરક્ષક).
Validates:
1. WebAR Live Camera Engine Overlay & Interactive Factory Torque Specifications Guide
2. 24/7 Highway Emergency Spares Smart Locker & Midnight Dispenser Kiosk
3. AgentCommander WebAR and Emergency Locker Directives
4. Chamunda CEO Tools Integration
5. FastAPI REST API Endpoints & Portal Dashboard Integration
6. Strict Helpline Compliance (+91 78747 19139)
"""

import sys
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
sys.path.insert(0, "/home/alpesh/jarvis-agent")

from webar_engine_guide import get_webar_engine, ChamundaWebAREngineGuide
from night_locker_engine import get_night_locker_manager, ChamundaNightLockerManager
from core.agent_commander import AgentCommander
from tools.chamunda_ceo_tools import (
    chamunda_get_webar_engine_overlay,
    chamunda_get_night_locker_telemetry,
    chamunda_reserve_emergency_highway_locker,
    chamunda_unlock_emergency_highway_locker,
)
from app import app


@pytest.fixture
def client():
    return TestClient(app)


# =========================================================================
# 1. WebAR Engine Guide & Interactive Torque Overlay Tests
# =========================================================================
def test_webar_engine_assemblies_registration():
    engine = get_webar_engine()
    assemblies = engine.get_assemblies()
    assert len(assemblies) >= 4

    asm_ids = [a["assembly_id"] for a in assemblies]
    assert "AR-J350-HEAD" in asm_ids
    assert "AR-650-CLUTCH" in asm_ids
    assert "AR-VINTAGE-CI-CRANK" in asm_ids
    assert "AR-SHERPA-450-COOLING" in asm_ids


def test_webar_engine_j350_head_overlay_calculation():
    engine = get_webar_engine()
    view = engine.calculate_ar_camera_view("AR-J350-HEAD", camera_feed_width=640, camera_feed_height=480)
    assert view["success"] is True
    assert view["assembly_id"] == "AR-J350-HEAD"
    assert view["camera_resolution"] == "640x480"
    assert view["markers_count"] >= 4
    assert "Criss-Cross" in view["methodology"]
    assert "માસ્ટર ટેક રમેશ" in view["ramesh_advisory"]
    assert len(view["svg_guide_path"]) > 0

    # Ensure sequence step 1 through 4
    steps = [m["sequence_step"] for m in view["markers"]]
    assert steps == sorted(steps)
    assert 1 in steps
    assert 4 in steps

    # Check warehouse stock linkage
    for m in view["markers"]:
        assert "warehouse_stock" in m
        assert "unit_mrp" in m
        assert "bin_location" in m
        assert m["torque_nm"] > 0
        assert m["screen_x"] >= 0 and m["screen_x"] <= 640
        assert m["screen_y"] >= 0 and m["screen_y"] <= 480


def test_webar_engine_vintage_ci_and_sherpa():
    engine = get_webar_engine()
    vintage = engine.calculate_ar_camera_view("AR-VINTAGE-CI-CRANK")
    assert vintage["success"] is True
    assert "1982 Vintage Cast-Iron" in vintage["title"]
    assert len(vintage["markers"]) >= 1

    sherpa = engine.calculate_ar_camera_view("AR-SHERPA-450-COOLING")
    assert sherpa["success"] is True
    assert "Sherpa 450" in sherpa["title"]


def test_webar_engine_invalid_assembly():
    engine = get_webar_engine()
    res = engine.calculate_ar_camera_view("NON-EXISTENT-ASSEMBLY")
    assert res["success"] is False
    assert "not found" in res["error"]


# =========================================================================
# 2. 24/7 Night Highway Emergency Locker Manager Tests
# =========================================================================
def test_night_locker_status_and_telemetry():
    mgr = get_night_locker_manager()
    status = mgr.get_locker_status()

    assert status["locker_station"] == "CHAMUNDA-LOCKER-MEHSANA-HQ"
    assert status["support_whatsapp"] == "+91 78747 19139"
    assert status["total_compartments"] == 8
    assert status["available_compartments_count"] > 0
    assert status["telemetry"]["system_status"] == "ONLINE"
    assert status["telemetry"]["ambient_temp_c"] > 0
    assert status["telemetry"]["backup_battery_pct"] >= 90
    assert len(status["compartments"]) == 8


def test_night_locker_reserve_and_unlock_flow():
    mgr = get_night_locker_manager()
    # Find first available box
    status = mgr.get_locker_status()
    avail_box = next((b for b in status["compartments"] if b["status"] == "Available" and b["units_inside"] > 0), None)
    assert avail_box is not None, "No available locker compartment for test"

    box_id = avail_box["box_id"]
    initial_units = avail_box["units_inside"]

    # 1. Reserve compartment
    res = mgr.reserve_compartment(
        box_id=box_id,
        customer_name="Test Tourer",
        phone="+91 99887 76655",
        vehicle_reg="GJ-01-RE-9999"
    )
    assert res["success"] is True
    res_id = res["reservation_id"]
    otp = res["otp_code"]
    assert len(otp) == 6
    assert "7874719139@upi" in res["upi_payload"]
    assert res["whatsapp_helpline"] == "+91 78747 19139"

    # 2. Re-reserving the same reserved compartment should fail
    fail_res = mgr.reserve_compartment(
        box_id=box_id,
        customer_name="Second Tourer",
        phone="+91 99887 76655"
    )
    assert fail_res["success"] is False

    # 3. Wrong OTP unlock should fail
    bad_unlock = mgr.verify_and_unlock(reservation_id=res_id, otp_code="000000")
    assert bad_unlock["success"] is False
    assert "Invalid OTP" in bad_unlock["error"]

    # 4. Correct OTP unlock succeeds
    good_unlock = mgr.verify_and_unlock(
        reservation_id=res_id,
        otp_code=otp,
        payment_ref="UPI-TEST-CONFIRMED-TXN"
    )
    assert good_unlock["success"] is True
    assert good_unlock["box_id"] == box_id
    assert good_unlock["solenoid_pulse"] == "500ms_12V_HIGH"
    assert "સફળતાપૂર્વક" in good_unlock["message_gu"]

    # Verify inventory was decremented
    updated_status = mgr.get_locker_status()
    updated_box = next(b for b in updated_status["compartments"] if b["box_id"] == box_id)
    assert updated_box["units_inside"] == initial_units - 1
    assert updated_box["door_state"] == "OPEN_UNLOCKED"


# =========================================================================
# 3. AgentCommander WebAR & Emergency Locker Directives Tests
# =========================================================================
def test_agent_commander_webar_directive():
    commander = AgentCommander()
    result = commander.execute_webar_guide_directive(assembly_id="AR-J350-HEAD")
    assert result["success"] is True
    assert "J-Series" in result["platform"]
    assert result["assembly_id"] == "AR-J350-HEAD"
    assert len(result["markers"]) >= 4


def test_agent_commander_emergency_locker_directive():
    commander = AgentCommander()
    # Find available box to reserve
    mgr = get_night_locker_manager()
    status = mgr.get_locker_status()
    avail = next((b for b in status["compartments"] if b["status"] == "Available" and b["units_inside"] > 0), None)
    if avail:
        reserve_res = commander.execute_emergency_locker_directive(
            box_id=avail["box_id"],
            customer_name="Commander Rider",
            phone="+91 98765 43210"
        )
        assert reserve_res["success"] is True
        assert "NLK-" in reserve_res["reservation_id"]
        assert len(reserve_res["otp_code"]) == 6


def test_agent_commander_natural_language_routing_webar_and_locker():
    commander = AgentCommander()

    # Route AR camera torque command
    res_ar = commander.execute_written_directive(
        command_text="J-Series cylinder head tightening torque sequence and WebAR camera overlay check karo",
        sender="Master Tech Alpesh",
        priority="High"
    )
    assert res_ar["success"] is True
    assert "WebAR" in res_ar["directive"]
    assert "વેબAR" in res_ar["response_gu"] or "J-Series" in res_ar["response_gu"]

    # Route Night locker command
    res_lk = commander.execute_written_directive(
        command_text="Check status of 24/7 highway emergency locker bay outside workshop",
        sender="Founder Alpesh Sir",
        priority="Normal"
    )
    assert res_lk["success"] is True
    assert "Locker" in res_lk["directive"]


# =========================================================================
# 4. Chamunda CEO Tools Integration Tests
# =========================================================================
def test_chamunda_ceo_tools_webar_overlay():
    res_str = chamunda_get_webar_engine_overlay("AR-650-CLUTCH")
    assert "650" in res_str
    assert "Clutch" in res_str
    assert "Nm" in res_str


def test_chamunda_ceo_tools_night_locker():
    # Status
    status_str = chamunda_get_night_locker_telemetry()
    assert "CHAMUNDA-LOCKER-MEHSANA-HQ" in status_str
    assert "+91 78747 19139" in status_str

    # Find available box
    mgr = get_night_locker_manager()
    status = mgr.get_locker_status()
    avail = next((b for b in status["compartments"] if b["status"] == "Available" and b["units_inside"] > 0), None)
    if avail:
        res_str = chamunda_reserve_emergency_highway_locker(
            box_id=avail["box_id"],
            customer_name="CEO Tool Rider",
            phone="+91 98250 11223",
            vehicle_reg="GJ-02-ZZ-0001"
        )
        assert "NLK-" in res_str or "Reserved" in res_str or avail["box_id"] in res_str


# =========================================================================
# 5. FastAPI REST API Endpoints Tests
# =========================================================================
def test_api_webar_assemblies_and_overlay(client):
    # GET assemblies
    res = client.get("/api/webar/assemblies")
    assert res.status_code == 200
    assemblies = res.json()
    assert isinstance(assemblies, list)
    assert len(assemblies) >= 4

    # GET overlay for J-Series
    res2 = client.get("/api/webar/overlay/AR-J350-HEAD?width=800&height=600")
    assert res2.status_code == 200
    data = res2.json()
    assert data["success"] is True
    assert data["assembly_id"] == "AR-J350-HEAD"
    assert data["camera_resolution"] == "800x600"
    assert len(data["markers"]) >= 4


def test_api_night_locker_endpoints(client):
    # GET status
    res = client.get("/api/locker/status")
    assert res.status_code == 200
    status = res.json()
    assert status["total_compartments"] == 8
    assert status["support_whatsapp"] == "+91 78747 19139"

    # Find available box
    avail = next((b for b in status["compartments"] if b["status"] == "Available" and b["units_inside"] > 0), None)
    if not avail:
        # restock box 8 for test
        mgr = get_night_locker_manager()
        mgr.restock_compartment("BOX-08", add_units=2)
        avail_box_id = "BOX-08"
    else:
        avail_box_id = avail["box_id"]

    # POST reserve
    payload = {
        "box_id": avail_box_id,
        "customer_name": "API Night Tourer",
        "phone": "+91 98250 55443",
        "vehicle_reg": "GJ-02-API-005"
    }
    res2 = client.post("/api/locker/reserve", json=payload)
    assert res2.status_code == 200
    data = res2.json()
    assert data["success"] is True
    assert "NLK-" in data["reservation_id"]
    assert len(data["otp_code"]) == 6

    # POST unlock
    unlock_payload = {
        "reservation_id": data["reservation_id"],
        "otp_code": data["otp_code"],
        "payment_ref": "API-TEST-UPI-CONFIRM"
    }
    res3 = client.post("/api/locker/unlock", json=unlock_payload)
    assert res3.status_code == 200
    unlock_data = res3.json()
    assert unlock_data["success"] is True
    assert unlock_data["solenoid_pulse"] == "500ms_12V_HIGH"
    assert unlock_data["box_id"] == avail_box_id
