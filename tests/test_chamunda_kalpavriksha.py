"""
Unit and Integration Test Suite for Project Kalpavriksha (પ્રોજેક્ટ કલ્પવૃક્ષ).
Autonomous Virtual Growth, Synthetic Simulation Arena, PWA Mobile Access & 100% Offline Intelligence.

Validates:
1. Kalpavriksha Growth Engine Telemetry & Knowledge Base
2. Autonomous Synthetic Diagnostic Simulations & Agent XP Leveling
3. Factory Technical Manuals Ingestion & Offline Persistence
4. AgentCommander Kalpavriksha Directives & Natural Language Routing
5. Chamunda CEO Tools Integration (chamunda_get_kalpavriksha_growth_telemetry, chamunda_trigger_agent_synthetic_training)
6. FastAPI REST Endpoints (GET /api/kalpavriksha/status, POST /api/kalpavriksha/simulate, POST /api/kalpavriksha/ingest-spec)
7. Mobile PWA Architecture (manifest.json & sw.js local caching)
8. Strict Customer Helpline Compliance (+91 78747 19139)
"""

import sys
import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
sys.path.insert(0, "/home/alpesh/jarvis-agent")

from kalpavriksha_growth_engine import get_kalpavriksha_engine, ChamundaKalpavrikshaEngine, OFFICIAL_WHATSAPP_HELPLINE
from core.agent_commander import AgentCommander
from tools.chamunda_ceo_tools import (
    chamunda_get_kalpavriksha_growth_telemetry,
    chamunda_trigger_agent_synthetic_training,
)
from app import app


@pytest.fixture
def client():
    return TestClient(app)


# =========================================================================
# 1. Kalpavriksha Growth Engine Telemetry & Knowledge Base Tests
# =========================================================================
def test_kalpavriksha_growth_telemetry():
    engine = get_kalpavriksha_engine()
    telemetry = engine.get_growth_telemetry()

    assert telemetry["cluster_title"] == "CHAMUNDA-KALPAVRIKSHA-VIRTUAL-BRAIN"
    assert telemetry["offline_mode_active"] is True
    assert telemetry["whatsapp_helpline"] == "+91 78747 19139"
    assert telemetry["fleet_overall_iq"] >= 180
    assert telemetry["total_fleet_xp"] > 0
    assert telemetry["average_agent_level"] >= 10.0

    # Ensure all 6 core sub-agents are actively tracking mastery
    agents = telemetry["agents"]
    assert len(agents) >= 6
    assert "aradhya_ceo" in agents
    assert "ramesh_bay" in agents
    assert "jayesh_parts" in agents
    assert "priya_reception" in agents
    assert "kabir_social" in agents
    assert "hasmukh_accounts" in agents

    # Check specs array
    assert telemetry["knowledge_specs_count"] >= 3
    assert len(telemetry["technical_specs"]) >= 3


# =========================================================================
# 2. Autonomous Synthetic Diagnostic Simulations & Agent XP Leveling Tests
# =========================================================================
def test_synthetic_diagnostic_simulation_execution():
    engine = get_kalpavriksha_engine()
    initial_telemetry = engine.get_growth_telemetry()
    initial_sims = initial_telemetry["total_simulations_executed"]
    initial_total_xp = initial_telemetry["total_fleet_xp"]

    result = engine.run_synthetic_diagnostic_simulation()

    assert result["success"] is True
    assert result["simulation_id"].startswith("SIM-")
    assert result["xp_awarded"] > 0
    assert result["bike_model"] is not None
    assert result["symptom"] is not None
    assert result["diagnosis"] is not None
    assert result["solution_prescribed"] is not None
    assert result["solution_gu"] is not None
    assert result["offline_mode"] is True

    # Check telemetry update
    updated_telemetry = engine.get_growth_telemetry()
    assert updated_telemetry["total_simulations_executed"] == initial_sims + 1
    assert updated_telemetry["total_fleet_xp"] > initial_total_xp
    assert len(updated_telemetry["recent_simulations"]) > 0


# =========================================================================
# 3. Factory Technical Manuals Ingestion & Offline Persistence Tests
# =========================================================================
def test_technical_manual_spec_ingestion():
    engine = get_kalpavriksha_engine()
    initial_count = engine.get_growth_telemetry()["knowledge_specs_count"]

    res = engine.ingest_technical_manual_spec(
        engine_family="Bear 650 Scrambler DOHC",
        category="Suspension & Chassis Torque",
        target_components="Showa USD Fork Pinch Bolts & Triple Tree",
        torque_sequence="Lower pinch bolts: 25 Nm (M8), Upper clamp: 20 Nm",
        clearances="Fork oil capacity: 480 ml per leg (10W synthetic fork oil)",
        ramesh_secret="Always bounce front suspension 3 times before tightening lower clamp to prevent fork stiction."
    )

    assert res["success"] is True
    assert res["spec_id"].startswith("SPEC-")

    # Verify ingestion reflected in telemetry
    updated = engine.get_growth_telemetry()
    assert updated["knowledge_specs_count"] == initial_count + 1
    recent_spec = updated["technical_specs"][-1]
    assert recent_spec["engine_family"] == "Bear 650 Scrambler DOHC"
    assert "Showa USD Fork" in recent_spec["target_components"]
    assert "stiction" in recent_spec["ramesh_secret"]


# =========================================================================
# 4. AgentCommander Kalpavriksha Directives & Natural Language Routing Tests
# =========================================================================
def test_agent_commander_kalpavriksha_simulation_directive():
    commander = AgentCommander()
    res = commander.execute_kalpavriksha_directive(action="simulate")

    assert res["success"] is True
    assert res["simulation_id"].startswith("SIM-")
    assert res["xp_awarded"] > 0
    assert res["offline_mode"] is True


def test_agent_commander_kalpavriksha_status_directive():
    commander = AgentCommander()
    res = commander.execute_kalpavriksha_directive(action="status")

    assert res["cluster_title"] == "CHAMUNDA-KALPAVRIKSHA-VIRTUAL-BRAIN"
    assert res["offline_mode_active"] is True
    assert "agents" in res


def test_agent_commander_natural_language_routing():
    commander = AgentCommander()

    queries = [
        "Run kalpavriksha synthetic simulation for Ramesh",
        "કલ્પવૃક્ષ તાલીમ શરૂ કરો",
        "Trigger virtual growth session",
        "Let agents simulate breakdown scenarios"
    ]

    for q in queries:
        resp = commander.execute_written_directive(
            command_text=q,
            sender="Alpesh Sir (Founder & Chairman)",
            priority="CRITICAL"
        )
        assert resp["success"] is True
        assert resp["target_agent"] == "kalpavriksha_growth_engine"
        assert "result" in resp
        assert resp["result"]["success"] is True


# =========================================================================
# 5. Chamunda CEO Tools Integration Tests
# =========================================================================
def test_ceo_tools_kalpavriksha_telemetry():
    out = chamunda_get_kalpavriksha_growth_telemetry()

    assert "Project Kalpavriksha" in out
    assert "CHAMUNDA-KALPAVRIKSHA-VIRTUAL-BRAIN" in out
    assert "100% ACTIVE" in out
    assert "+91 78747 19139" in out
    assert "Master Tech Ramesh Patel" in out
    assert "Executive Grandmaster" in out or "Aradhya" in out


def test_ceo_tools_kalpavriksha_simulation_trigger():
    out = chamunda_trigger_agent_synthetic_training()

    assert "Autonomous Synthetic Breakdown Simulation Executed" in out
    assert "XP Awarded" in out
    assert "ગુજરાતી ઉકેલ:" in out
    assert "100% Offline Simulation completed locally on laptop" in out


# =========================================================================
# 6. FastAPI REST Endpoints Tests
# =========================================================================
def test_api_kalpavriksha_status(client):
    response = client.get("/api/kalpavriksha/status")
    assert response.status_code == 200
    data = response.json()
    assert data["cluster_title"] == "CHAMUNDA-KALPAVRIKSHA-VIRTUAL-BRAIN"
    assert data["offline_mode_active"] is True
    assert data["whatsapp_helpline"] == "+91 78747 19139"
    assert len(data["agents"]) >= 6


def test_api_kalpavriksha_simulate(client):
    response = client.post("/api/kalpavriksha/simulate")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "simulation_id" in data
    assert "xp_awarded" in data
    assert "solution_gu" in data


def test_api_kalpavriksha_ingest_spec(client):
    payload = {
        "engine_family": "Shotgun 650 Custom Bobber",
        "category": "Chassis & Swingarm",
        "target_components": "Swingarm Pivot Pin & Spindle",
        "torque_sequence": "Pivot Pin Nut: 85 Nm + Loctite 243",
        "clearances": "Axial play: 0.05 - 0.15 mm",
        "ramesh_secret": "Pack needle roller bearings with NLGI Grade 2 lithium molybdenum grease before seating."
    }
    response = client.post("/api/kalpavriksha/ingest-spec", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["spec_id"].startswith("SPEC-")


# =========================================================================
# 7. Mobile PWA Architecture Tests
# =========================================================================
def test_pwa_manifest_and_service_worker():
    manifest_file = Path("/home/alpesh/chamunda_re_enterprise/static/manifest.json")
    sw_file = Path("/home/alpesh/chamunda_re_enterprise/static/sw.js")

    assert manifest_file.exists(), "PWA manifest.json must exist in static directory"
    assert sw_file.exists(), "Service Worker sw.js must exist in static directory"

    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    assert "Chamunda" in manifest_data["name"]
    assert manifest_data["short_name"] == "Chamunda RE"
    assert manifest_data["display"] == "standalone"
    assert manifest_data["theme_color"] == "#f39c12"
    assert len(manifest_data["icons"]) >= 2

    with open(sw_file, "r", encoding="utf-8") as f:
        sw_content = f.read()

    assert "CACHE_NAME" in sw_content
    assert "caches.open" in sw_content
    assert "fetch" in sw_content


# =========================================================================
# 8. Strict Helpline Compliance
# =========================================================================
def test_strict_helpline_compliance():
    assert OFFICIAL_WHATSAPP_HELPLINE == "+91 78747 19139"
    engine = get_kalpavriksha_engine()
    st = engine.get_growth_telemetry()
    assert st["whatsapp_helpline"] == "+91 78747 19139"
