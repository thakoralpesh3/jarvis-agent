"""
Unit and Integration Test Suite for Project Trinetra (પ્રોજેક્ટ ત્રિનેત્ર).
Validates:
1. 3D Interactive Exploded Engine Schematics & Factory Torque Specifications
2. Non-Invasive AI Borescope Combustion Chamber & Cylinder Inspection
3. Multi-Branch Cloud Network & Franchise Operating System
4. AgentCommander Trinetra Directives
5. Chamunda CEO Tools Integration
6. FastAPI REST API Endpoints & Portal Dashboard Integration
"""

import sys
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
sys.path.insert(0, "/home/alpesh/jarvis-agent")

from schematics_3d_engine import get_schematics_3d_engine, Chamunda3DSchematicsManager
from borescope_inspection_engine import get_borescope_engine, ChamundaBorescopeEngine
from multibranch_hub_engine import get_multibranch_engine, ChamundaMultiBranchManager
from core.agent_commander import AgentCommander
from tools.chamunda_ceo_tools import (
    chamunda_lookup_3d_engine_schematic,
    chamunda_run_borescope_inspection,
    chamunda_get_multibranch_overview,
    chamunda_transfer_branch_inventory,
)
from app import app


@pytest.fixture
def client():
    return TestClient(app)


# =========================================================================
# 1. 3D Engine Schematics & Factory Torque Engine Tests
# =========================================================================
def test_schematics_engine_assemblies():
    engine = get_schematics_3d_engine()
    assemblies = engine.get_assemblies()
    assert len(assemblies) >= 4

    ids = [a["assembly_id"] for a in assemblies]
    assert "ASM-J350-HEAD" in ids
    assert any(x in ids for x in ["ASM-TWIN650-CLUTCH", "ASM-650-CLUTCH"])
    assert any(x in ids for x in ["ASM-VINTAGE-CRANK", "ASM-CI350-CRANK"])
    assert any(x in ids for x in ["ASM-SHERPA450-COOLING", "ASM-SHERPA-COOLING"])

    # Test alias resolution
    assert engine.get_assembly_by_id("ASM-650-CLUTCH") is not None
    assert engine.get_assembly_by_id("ASM-TWIN650-CLUTCH") is not None



def test_schematics_engine_lookup_assembly():
    engine = get_schematics_3d_engine()
    j_head = engine.get_assembly_by_id("ASM-J350-HEAD")
    assert j_head is not None
    assert "J-Series" in j_head["title"]
    assert len(j_head["components"]) >= 5

    # Check torque specs
    torques = [c.get("torque_nm", "") for c in j_head["components"]]
    assert any("45 Nm" in t for t in torques)  # Cylinder Head Studs

    # Check Master Tech Ramesh advice
    advice = [c.get("master_tech_advice", "") for c in j_head["components"]]
    assert any("Master Tech Ramesh" in a for a in advice)


def test_schematics_engine_not_found():
    engine = get_schematics_3d_engine()
    res = engine.get_assembly_by_id("ASM-NONEXISTENT")
    assert res is None


# =========================================================================
# 2. AI Borescope Combustion Chamber Inspection Engine Tests
# =========================================================================
def test_borescope_engine_default_inspections():
    engine = get_borescope_engine()
    inspections = engine.get_inspections()
    assert isinstance(inspections, list)
    assert len(inspections) >= 1


def test_borescope_inspection_heavy_carbon():
    engine = get_borescope_engine()
    res = engine.inspect_combustion_chamber(
        bike_model="Classic 350 (Reborn)",
        registration_no="GJ-02-BQ-1234",
        odometer_km=16500,
        scenario="heavy_carbon_crust"
    )
    assert res["inspection_id"].startswith("BORE-")
    assert res["piston_crown"]["carbon_crust_thickness_mm"] >= 0.9
    assert res["combustion_health_score"] <= 70
    assert "Grade C" in res["chamber_grade"]
    assert "Liqui Moly" in res["prescribed_treatment"]
    assert res["cost_estimate_inr"] > 0
    assert "માસ્ટર ટેક રમેશ" in res["master_tech_verdict_gu"]
    assert "Master Tech Ramesh" in res["master_tech_verdict_en"]


def test_borescope_inspection_pristine():
    engine = get_borescope_engine()
    res = engine.inspect_combustion_chamber(
        bike_model="Hunter 350",
        registration_no="GJ-01-XX-9999",
        odometer_km=1200,
        scenario="pristine_showroom"
    )
    assert res["combustion_health_score"] >= 90
    assert "Grade A" in res["chamber_grade"]
    assert res["cost_estimate_inr"] == 0
    assert res["piston_crown"]["carbon_crust_thickness_mm"] <= 0.2


def test_borescope_inspection_bore_score():
    engine = get_borescope_engine()
    res = engine.inspect_combustion_chamber(
        bike_model="Himalayan 450",
        registration_no="GJ-02-ZZ-4567",
        odometer_km=32000,
        scenario="bore_score_damage"
    )
    assert res["cylinder_wall"]["micro_scratch_detected"] is True
    assert "Grade D" in res["chamber_grade"]
    assert res["combustion_health_score"] <= 45


# =========================================================================
# 3. Multi-Branch Cloud Network Engine Tests
# =========================================================================
def test_multibranch_branches_list():
    engine = get_multibranch_engine()
    branches = engine.get_branches()
    assert len(branches) >= 5

    branch_ids = [b["branch_id"] for b in branches]
    assert "HQ-MEHSANA" in branch_ids
    assert "BR-PATAN-01" in branch_ids
    assert "BR-VISN-02" in branch_ids
    assert "BR-UNJHA-03" in branch_ids
    assert "BR-PALAN-04" in branch_ids


def test_multibranch_overview():
    engine = get_multibranch_engine()
    ov = engine.get_branches_overview()
    assert ov["total_branches"] >= 5
    assert ov["total_active_bays"] >= 15
    assert ov["total_jobs_today"] >= 60
    assert ov["total_revenue_today_inr"] >= 150000
    assert ov["total_inventory_valuation_inr"] > 5000000
    assert "HQ-MEHSANA" in ov["hq_branch"]


def test_multibranch_stock_transfer():
    engine = get_multibranch_engine()
    res = engine.transfer_stock(
        from_branch="HQ-MEHSANA",
        to_branch="BR-VISN-02",
        part_number="574050/C",
        quantity=5,
        requested_by="Pravin Solanki",
        part_name="Genuine Oil Filter Element",
        unit_mrp=210.0,
        notes="Express replenish for evening express bays"
    )
    assert res["success"] is True
    assert res["transfer"]["from_branch"] == "HQ-MEHSANA"
    assert res["transfer"]["to_branch"] == "BR-VISN-02"
    assert res["transfer"]["quantity"] == 5
    assert res["transfer"]["status"] == "In-Transit"
    assert "વિસનગર" in res["message_gu"]


def test_multibranch_transfer_validation():
    engine = get_multibranch_engine()
    # Same source and destination
    with pytest.raises(ValueError):
        engine.transfer_stock(
            from_branch="HQ-MEHSANA",
            to_branch="HQ-MEHSANA",
            part_number="574012/A",
            quantity=1
        )
    # Invalid branch
    with pytest.raises(ValueError):
        engine.transfer_stock(
            from_branch="HQ-MEHSANA",
            to_branch="BR-LONDON-01",
            part_number="574012/A",
            quantity=1
        )


# =========================================================================
# 4. AgentCommander Directives Tests
# =========================================================================
def test_commander_trinetra_directives():
    cmdr = AgentCommander()

    # 3D Schematic directive
    sch_res = cmdr.execute_schematic_lookup_directive(assembly_id="ASM-650-CLUTCH")
    assert sch_res["found"] is True
    assert "650" in sch_res["assembly"]["title"]

    # Borescope directive
    bore_res = cmdr.execute_borescope_directive(
        bike_model="Classic 350",
        registration_no="GJ-02-BQ-1234",
        odometer_km=15000,
        scenario="moderate_carbon"
    )
    assert bore_res["inspection_id"].startswith("BORE-")
    assert "Grade B" in bore_res["chamber_grade"]

    # Multi-branch transfer directive
    trf_res = cmdr.execute_branch_transfer_directive(
        from_branch="HQ-MEHSANA",
        to_branch="BR-UNJHA-03",
        part_number="RAM00008/B",
        quantity=2,
        requested_by="Haresh Chaudhari",
        notes="Urgent front brake overhaul stock"
    )
    assert trf_res["success"] is True
    assert trf_res["transfer"]["to_branch"] == "BR-UNJHA-03"


# =========================================================================
# 5. Chamunda CEO Tools Integration Tests
# =========================================================================
def test_ceo_tools_schematics():
    out = chamunda_lookup_3d_engine_schematic("ASM-J350-HEAD")
    assert "Chamunda 3D Schematics" in out
    assert "J-Series 350 SOHC" in out
    assert "Factory Torque" in out
    assert "Master Tech Ramesh" in out


def test_ceo_tools_borescope():
    out = chamunda_run_borescope_inspection(
        bike_model="Classic 350 (Reborn)",
        registration_no="GJ-02-BQ-1234",
        odometer_km=15000,
        scenario="heavy_carbon_crust"
    )
    assert "Borescope Combustion Chamber Diagnostic Report" in out
    assert "+91 78747 19139" in out
    assert "માસ્ટર ટેક રમેશ" in out


def test_ceo_tools_multibranch():
    out_ov = chamunda_get_multibranch_overview()
    assert "Multi-Branch Franchise Network Overview" in out_ov
    assert "HQ-MEHSANA" in out_ov
    assert "BR-PATAN-01" in out_ov

    out_trf = chamunda_transfer_branch_inventory(
        from_branch="HQ-MEHSANA",
        to_branch="BR-PALAN-04",
        part_number="KXA00310",
        quantity=3,
        requested_by="Dhaval Vaghela",
        notes="Highway SOS spares buffer"
    )
    assert "Intra-Branch Stock Transfer Dispatched" in out_trf
    assert "+91 78747 19139" in out_trf


# =========================================================================
# 6. FastAPI REST API Endpoints Tests
# =========================================================================
def test_api_schematics_endpoints(client):
    # List assemblies
    resp = client.get("/api/schematics/assemblies")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 4

    # Single assembly
    resp2 = client.get("/api/schematics/assembly/ASM-J350-HEAD")
    assert resp2.status_code == 200
    asm = resp2.json()
    assert asm["assembly_id"] == "ASM-J350-HEAD"

    # Not found
    resp3 = client.get("/api/schematics/assembly/ASM-INVALID")
    assert resp3.status_code == 404


def test_api_borescope_endpoints(client):
    # Inspect
    payload = {
        "bike_model": "Classic 350 (Reborn)",
        "registration_no": "GJ-02-BQ-1234",
        "odometer_km": 15000,
        "scenario": "heavy_carbon_crust"
    }
    resp = client.post("/api/borescope/inspect", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["inspection_id"].startswith("BORE-")
    assert data["combustion_health_score"] <= 70

    # History
    resp2 = client.get("/api/borescope/inspections")
    assert resp2.status_code == 200
    assert len(resp2.json()) >= 1


def test_api_multibranch_endpoints(client):
    # Overview
    resp = client.get("/api/branches/overview")
    assert resp.status_code == 200
    ov = resp.json()
    assert ov["total_branches"] == 5

    # List
    resp2 = client.get("/api/branches/list")
    assert resp2.status_code == 200
    assert len(resp2.json()) == 5

    # Transfer
    trf_payload = {
        "from_branch": "HQ-MEHSANA",
        "to_branch": "BR-PATAN-01",
        "part_number": "574012/A",
        "quantity": 2,
        "requested_by": "Jignesh Prajapati",
        "notes": "Emergency test transfer"
    }
    resp3 = client.post("/api/branches/transfer-stock", json=trf_payload)
    assert resp3.status_code == 200
    trf_res = resp3.json()
    assert trf_res["success"] is True

    # Bad transfer
    bad_payload = {
        "from_branch": "HQ-MEHSANA",
        "to_branch": "HQ-MEHSANA",
        "part_number": "574012/A",
        "quantity": 2
    }
    resp4 = client.post("/api/branches/transfer-stock", json=bad_payload)
    assert resp4.status_code == 400


def test_api_dashboard_html_contains_trinetra_tabs(client):
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text

    # Tab navigation buttons
    assert 'id="schematics-tab"' in html
    assert 'id="borescope-tab"' in html
    assert 'id="multibranch-tab"' in html

    # Tab content panes
    assert 'id="engine-schematics"' in html
    assert 'id="borescope-inspection"' in html
    assert 'id="multibranch-hub"' in html

    # JavaScript function presence
    assert 'loadSchematicAssembly' in html
    assert 'runBorescopeInspection' in html
    assert 'loadMultiBranchOverview' in html
    assert 'submitBranchTransfer' in html
