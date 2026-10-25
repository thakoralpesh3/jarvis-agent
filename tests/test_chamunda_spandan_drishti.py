"""
Comprehensive Unit & Integration Tests for Project Spandan & Drishti:
1. Chamunda OBD-II Live IoT Scanner & ECU DTC Fault Decoder (Spandan)
2. Chamunda 24/7 Smart Lounge Self-Check-In Kiosk (Drishti)
3. AI Predictive Supply Chain & Auto-Reordering Engine
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

from obd_diagnostics_engine import ChamundaOBDDiagnosticsEngine, get_obd_diagnostics_engine, DTC_DATABASE
from smart_kiosk_engine import ChamundaSmartKioskEngine, get_smart_kiosk_engine
from predictive_supply_chain_engine import ChamundaPredictiveSupplyChainManager, get_predictive_supply_chain_manager
from core.agent_commander import AgentCommander
from tools.chamunda_ceo_tools import (
    chamunda_run_obd_iot_scan,
    chamunda_kiosk_express_checkin,
    chamunda_get_predictive_supply_forecast,
    chamunda_generate_predictive_auto_po
)


# ==============================================================================
# 1. OBD-II ENGINE TESTS
# ==============================================================================

def test_obd_engine_live_telemetry_ranges():
    engine = get_obd_diagnostics_engine()
    telem = engine.generate_live_telemetry("Classic 350 (Reborn)", is_faulty=False)

    assert 1000 <= telem["engine_rpm"] <= 1200
    assert 14.0 <= telem["battery_voltage"] <= 14.6
    assert 80 <= telem["engine_temp_c"] <= 100
    assert 0.4 <= telem["o2_sensor_v"] <= 0.8
    assert 30 <= telem["manifold_pressure_kpa"] <= 50


def test_obd_engine_dtc_scan_and_decoding():
    engine = get_obd_diagnostics_engine()

    # Test P0505 (Idle Stepper)
    res_p0505 = engine.run_obd_scan("Classic 350 (Reborn)", "GJ-02-BQ-1234", simulate_dtc="P0505")
    assert res_p0505["dtc_count"] == 1
    assert res_p0505["active_dtcs"][0]["dtc_code"] == "P0505"
    assert "KXA00112" in res_p0505["active_dtcs"][0]["oem_part_needed"]["part_number"]
    assert "માસ્ટર ટેક રમેશ" in res_p0505["diagnosis_gu"]

    # Test P0130 (O2 Sensor)
    res_p0130 = engine.run_obd_scan("Hunter 350", "GJ-02-CD-5678", simulate_dtc="P0130")
    assert res_p0130["dtc_count"] == 1
    assert res_p0130["active_dtcs"][0]["dtc_code"] == "P0130"
    assert "571052/B" in res_p0130["active_dtcs"][0]["oem_part_needed"]["part_number"]
    assert res_p0130["active_dtcs"][0]["severity"] == "Critical"

    # Test Healthy Scan
    res_healthy = engine.run_obd_scan("Interceptor 650", "GJ-02-EF-9012", simulate_dtc="HEALTHY")
    assert res_healthy["dtc_count"] == 0
    assert res_healthy["overall_ecu_health"] == "Optimal (Zero DTCs)"


# ==============================================================================
# 2. SMART KIOSK ENGINE TESTS
# ==============================================================================

def test_smart_kiosk_lookup():
    engine = get_smart_kiosk_engine()
    lookup = engine.lookup_vehicle("GJ-02-BQ-1234")

    assert "registration_no" in lookup
    assert "customer_name" in lookup
    assert "bike_model" in lookup


def test_smart_kiosk_checkin_and_token():
    engine = get_smart_kiosk_engine()
    checkin = engine.process_checkin(
        registration_no="GJ-02-BQ-1234",
        customer_name="Alpesh Sir",
        phone="+91 78747 19139",
        bike_model="Classic 350 (Reborn)",
        selected_issues=["Periodic Service", "Acoustic Tappet Check"],
        odometer_km=14200
    )

    assert checkin["token_id"].startswith("TKN-")
    assert checkin["job_card_id"].startswith("JOB-")
    assert checkin["assigned_bay"] == "Bay 1 (J-Series Platform)"
    assert checkin["assigned_mechanic"] == "Master Tech Ramesh"
    assert checkin["whatsapp_slip_sent"] is True
    assert "+91 78747 19139" in checkin["whatsapp_message"]


# ==============================================================================
# 3. PREDICTIVE SUPPLY CHAIN TESTS
# ==============================================================================

def test_predictive_supply_chain_forecast():
    mgr = get_predictive_supply_chain_manager()
    fc_diwali = mgr.get_critical_parts_forecast("diwali_dhanteras_rush")

    assert fc_diwali["multiplier"] == 2.5
    assert fc_diwali["critical_shortage_skus"] >= 1
    assert len(fc_diwali["at_risk_parts"]) >= 4

    pnos = [p["part_number"] for p in fc_diwali["at_risk_parts"]]
    assert "574050/C" in pnos
    assert "LM-15W50-4T" in pnos

    fc_baseline = mgr.get_critical_parts_forecast("routine_baseline")
    assert fc_baseline["multiplier"] == 1.0


def test_predictive_supply_chain_auto_po():
    mgr = get_predictive_supply_chain_manager()
    po = mgr.generate_auto_replenishment_po("diwali_dhanteras_rush")

    assert po["po_number"].startswith("AUTO-PO-")
    assert po["multiplier_applied"] == 2.5
    assert po["total_units"] >= 100
    assert po["total_po_valuation_inr"] > 50000
    assert len(po["items"]) >= 4


# ==============================================================================
# 4. AGENT COMMANDER & CEO TOOLS TESTS
# ==============================================================================

def test_agent_commander_obd_and_kiosk():
    commander = AgentCommander()
    # OBD directive
    obd_res = commander.execute_obd_diagnostic_directive(
        bike_model="Classic 350 (Reborn)",
        registration_no="GJ-02-BQ-1234",
        simulate_dtc="P0300"
    )
    assert obd_res["dtc_count"] == 1
    assert obd_res["active_dtcs"][0]["dtc_code"] == "P0300"

    # Kiosk directive
    kiosk_res = commander.execute_kiosk_checkin_directive(
        registration_no="GJ-02-BQ-1234",
        customer_name="Alpesh Sir",
        phone="+91 78747 19139",
        bike_model="Classic 350 Reborn",
        selected_issues=["Periodic Service"]
    )
    assert kiosk_res["token_id"].startswith("TKN-")


def test_ceo_obd_kiosk_and_supply_tools():
    # 1. OBD Tool
    obd_out = chamunda_run_obd_iot_scan(
        bike_model="Classic 350 (Reborn)",
        registration_no="GJ-02-BQ-1234",
        simulate_dtc="P0115"
    )
    assert "OBD-II Live IoT Telemetry & ECU Scan" in obd_out
    assert "P0115" in obd_out
    assert "586044/A" in obd_out

    # 2. Kiosk Tool
    kiosk_out = chamunda_kiosk_express_checkin(
        registration_no="GJ-02-BQ-1234",
        customer_name="Alpesh Sir",
        phone="+91 78747 19139",
        bike_model="Classic 350",
        issues_csv="Periodic Service, Tappet Check"
    )
    assert "Smart Lounge Kiosk Express Check-In" in kiosk_out
    assert "TKN-" in kiosk_out
    assert "+91 78747 19139" in kiosk_out

    # 3. Supply Forecast Tool
    supply_out = chamunda_get_predictive_supply_forecast(season_key="diwali_dhanteras_rush")
    assert "Predictive Supply Chain Forecast" in supply_out
    assert "2.5x" in supply_out

    # 4. Auto PO Tool
    po_out = chamunda_generate_predictive_auto_po(season_key="diwali_dhanteras_rush")
    assert "Automated Wholesale Purchase Order Generated" in po_out
    assert "AUTO-PO-" in po_out


# ==============================================================================
# 5. FASTAPI REST API ENDPOINTS TESTS
# ==============================================================================

def test_fastapi_obd_kiosk_supply_endpoints():
    from fastapi.testclient import TestClient
    from app import app
    client = TestClient(app)

    # 1. POST /api/obd/scan
    obd_resp = client.post("/api/obd/scan", json={
        "bike_model": "Classic 350 (Reborn)",
        "registration_no": "GJ-02-BQ-1234",
        "simulate_dtc": "P0505"
    })
    assert obd_resp.status_code == 200
    assert obd_resp.json()["dtc_count"] == 1

    # 2. GET /api/obd/telemetry/Classic 350
    telem_resp = client.get("/api/obd/telemetry/Classic%20350")
    assert telem_resp.status_code == 200
    assert "engine_rpm" in telem_resp.json()

    # 3. GET /api/obd/scans
    scans_resp = client.get("/api/obd/scans")
    assert scans_resp.status_code == 200
    assert len(scans_resp.json()) >= 1

    # 4. GET /api/kiosk/lookup/{reg}
    lookup_resp = client.get("/api/kiosk/lookup/GJ-02-BQ-1234")
    assert lookup_resp.status_code == 200
    assert "customer_name" in lookup_resp.json()

    # 5. POST /api/kiosk/checkin
    checkin_resp = client.post("/api/kiosk/checkin", json={
        "registration_no": "GJ-02-BQ-1234",
        "customer_name": "Alpesh Sir",
        "phone": "+91 78747 19139",
        "bike_model": "Classic 350 (Reborn)",
        "selected_issues": ["Periodic Service", "Foam Wash"]
    })
    assert checkin_resp.status_code == 200
    assert checkin_resp.json()["token_id"].startswith("TKN-")

    # 6. GET /api/kiosk/tokens
    tokens_resp = client.get("/api/kiosk/tokens")
    assert tokens_resp.status_code == 200
    assert len(tokens_resp.json()) >= 1

    # 7. GET /api/supply-chain/forecast
    forecast_resp = client.get("/api/supply-chain/forecast?season=diwali_dhanteras_rush")
    assert forecast_resp.status_code == 200
    assert forecast_resp.json()["multiplier"] == 2.5

    # 8. POST /api/supply-chain/auto-po/generate
    auto_po_resp = client.post("/api/supply-chain/auto-po/generate", json={
        "season_key": "diwali_dhanteras_rush"
    })
    assert auto_po_resp.status_code == 200
    assert auto_po_resp.json()["po_number"].startswith("AUTO-PO-")

    # 9. GET /api/supply-chain/pos
    pos_resp = client.get("/api/supply-chain/pos")
    assert pos_resp.status_code == 200
    assert len(pos_resp.json()) >= 1
