"""
Unit and Integration Test Suite for Project Chhaya (પ્રોજેક્ટ છાયા).
Architecture 1: Cloud Shadow Mirroring & Offline Agent Access.
Validates:
1. Cloud Shadow State Snapshotting & Telemetry
2. Offline Remote Query Resolution across 6 Autonomous Cloud Replica Agents
3. Mutation Queuing & Reconnection Reconciliation
4. AgentCommander Cloud Shadow Directives & Natural Language Routing
5. Chamunda CEO Tools Integration
6. FastAPI REST API Endpoints & Standalone Cloud Mirror Server
7. Strict Customer Helpline Compliance (+91 78747 19139)
"""

import sys
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
sys.path.insert(0, "/home/alpesh/jarvis-agent")

from cloud_shadow_engine import get_cloud_shadow_manager, ChamundaCloudShadowManager, OFFICIAL_WHATSAPP_HELPLINE
from core.agent_commander import AgentCommander
from tools.chamunda_ceo_tools import (
    chamunda_get_cloud_shadow_telemetry,
    chamunda_simulate_offline_agent_query,
    chamunda_trigger_cloud_shadow_sync,
)
from app import app
from cloud_mirror_server import app as cloud_mirror_app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def cloud_client():
    return TestClient(cloud_mirror_app)


# =========================================================================
# 1. Cloud Shadow State Snapshotting & Telemetry Tests
# =========================================================================
def test_cloud_shadow_telemetry_and_cluster_status():
    mgr = get_cloud_shadow_manager()
    st = mgr.get_shadow_telemetry()

    assert st["cluster_name"] == "CHAMUNDA-CLOUD-SHADOW-HQ"
    assert st["cloud_region"] == "asia-south1 (Mumbai Cloud Mirror)"
    assert st["whatsapp_helpline"] == "+91 78747 19139"
    assert "snapshot_data" in st
    assert len(st["cloud_replicas"]) >= 6

    # Verify all 6 agents exist
    replicas = st["cloud_replicas"]
    assert "aradhya_ceo" in replicas
    assert "ramesh_bay" in replicas
    assert "jayesh_parts" in replicas
    assert "priya_reception" in replicas
    assert "kabir_social" in replicas
    assert "hasmukh_accounts" in replicas


def test_cloud_shadow_snapshot_generation():
    mgr = get_cloud_shadow_manager()
    res = mgr.generate_state_snapshot()

    assert res["success"] is True
    assert "snapshot" in res
    snap = res["snapshot"]
    assert snap["total_parts_skus"] >= 4469
    assert snap["inventory_valuation_inr"] > 0
    assert snap["active_subagents"] == 6


# =========================================================================
# 2. Offline Remote Query Resolution Tests (All 6 Agents)
# =========================================================================
def test_offline_query_jayesh_parts():
    mgr = get_cloud_shadow_manager()
    res = mgr.process_remote_offline_query("Classic 350 clutch plate stock and price check karo")

    assert res["success"] is True
    assert "Jayesh" in res["responding_agent"]
    assert "Parts Specialist" in res["assigned_role"]
    assert "4,469" in res["response_en"] or "574012" in res["response_en"]
    assert "જયેશ" in res["response_gu"]
    assert res["whatsapp_helpline"] == "+91 78747 19139"
    assert res["execution_environment"] == "CLOUD_SHADOW_STANDBY"


def test_offline_query_ramesh_torque():
    mgr = get_cloud_shadow_manager()
    res = mgr.process_remote_offline_query("J-Series 350 cylinder head factory tightening torque sequence")

    assert res["success"] is True
    assert "Ramesh" in res["responding_agent"]
    assert "Bay Chief" in res["assigned_role"]
    assert "45 Nm" in res["response_en"]
    assert "રમેશ" in res["response_gu"]


def test_offline_query_priya_job_status():
    mgr = get_cloud_shadow_manager()
    res = mgr.process_remote_offline_query("વર્કશોપમાં સર્વિસ બાઇક્સ અને જોબ કાર્ડ સ્ટેટસ શું છે?")

    assert res["success"] is True
    assert "Priya" in res["responding_agent"]
    assert "Customer Experience" in res["assigned_role"]
    assert "motorcycles" in res["response_en"] or "workflow" in res["response_en"]
    assert "પ્રિયા" in res["response_gu"]


def test_offline_query_hasmukh_accounts():
    mgr = get_cloud_shadow_manager()
    res = mgr.process_remote_offline_query("આજનું કુલ કેશલેસ યુપીઆઈ કલેક્શન અને હિસાબ કેટલો થયો?")

    assert res["success"] is True
    assert "Hasmukh" in res["responding_agent"]
    assert "Accounts Controller" in res["assigned_role"]
    assert "₹" in res["response_gu"] or "હસમુખ" in res["response_gu"]


def test_offline_query_kabir_social():
    mgr = get_cloud_shadow_manager()
    res = mgr.process_remote_offline_query("લેટેસ્ટ યુટ્યુબ શોર્ટ્સ અને વાયરલ વિડીયો અપડેટ આપો")

    assert res["success"] is True
    assert "Kabir" in res["responding_agent"]
    assert "Social Growth" in res["assigned_role"]
    assert "Short" in res["response_en"] or "views" in res["response_en"]


def test_offline_query_aradhya_ceo_fallback():
    mgr = get_cloud_shadow_manager()
    res = mgr.process_remote_offline_query("સાહેબ, કોઈ જનરલ સજેશન આપો")

    assert res["success"] is True
    assert "Aradhya" in res["responding_agent"]
    assert "CEO" in res["assigned_role"]
    assert "Cloud Shadow" in res["response_en"]


# =========================================================================
# 3. Mutation Queuing & Reconnection Reconciliation Tests
# =========================================================================
def test_cloud_shadow_mutation_queuing_and_reconciliation():
    mgr = get_cloud_shadow_manager()

    # Queue an offline event
    queue_res = mgr.queue_offline_mutation(
        mutation_type="EMERGENCY_LOCKER_BOOKING",
        payload={"box_id": "BOX-01", "customer": "Touring Rider", "phone": "+91 98250 12345"}
    )
    assert queue_res["success"] is True
    assert "MUT-SHADOW-" in queue_res["mutation_id"]

    st = mgr.get_shadow_telemetry()
    assert st["queued_mutations_count"] >= 1

    # Reconcile when laptop is reconnected
    recon_res = mgr.reconcile_sync()
    assert recon_res["success"] is True
    assert recon_res["mutations_applied"] >= 1
    assert "zero data loss" in recon_res["message_en"]
    assert "સફળતાપૂર્વક" in recon_res["message_gu"]

    # Verify queue is drained
    st2 = mgr.get_shadow_telemetry()
    assert st2["queued_mutations_count"] == 0


# =========================================================================
# 4. AgentCommander Directives & Natural Language Routing Tests
# =========================================================================
def test_agent_commander_cloud_shadow_directives():
    commander = AgentCommander()

    # Status
    st_res = commander.execute_cloud_shadow_directive(action="status")
    assert st_res["cluster_name"] == "CHAMUNDA-CLOUD-SHADOW-HQ"

    # Snapshot
    snap_res = commander.execute_cloud_shadow_directive(action="snapshot")
    assert snap_res["success"] is True

    # Query
    q_res = commander.execute_cloud_shadow_directive(action="query", query_text="Classic 350 clutch plate stock")
    assert q_res["success"] is True
    assert "Jayesh" in q_res["responding_agent"]

    # Reconcile
    rec_res = commander.execute_cloud_shadow_directive(action="reconcile")
    assert rec_res["success"] is True


def test_agent_commander_natural_language_routing_cloud_shadow():
    commander = AgentCommander()

    res = commander.execute_written_directive(
        command_text="લેપટોપ ઓફલાઇન હોય ત્યારે ક્લાઉડ શેડો અને એજન્ટ્સ સ્ટેટસ તપાસો",
        sender="Master Tech Alpesh",
        priority="High"
    )
    assert res["success"] is True
    assert "cloud_shadow_engine" in res["target_agent"]
    assert "Project Chhaya" in res["directive"]


# =========================================================================
# 5. Chamunda CEO Tools Integration Tests
# =========================================================================
def test_chamunda_ceo_tools_cloud_shadow():
    # Telemetry
    tel_str = chamunda_get_cloud_shadow_telemetry()
    assert "CHAMUNDA-CLOUD-SHADOW-HQ" in tel_str
    assert "4,469" in tel_str
    assert "+91 78747 19139" in tel_str

    # Simulate query
    sim_str = chamunda_simulate_offline_agent_query("Classic 350 clutch plate stock check karo")
    assert "Jayesh" in sim_str
    assert "+91 78747 19139" in sim_str

    # Trigger sync
    sync_str = chamunda_trigger_cloud_shadow_sync()
    assert "Successful" in sync_str or "snapshot" in sync_str


# =========================================================================
# 6. FastAPI REST API Endpoints Tests
# =========================================================================
def test_api_cloud_shadow_endpoints(client):
    # GET status
    res = client.get("/api/cloud-shadow/status")
    assert res.status_code == 200
    data = res.json()
    assert data["cluster_name"] == "CHAMUNDA-CLOUD-SHADOW-HQ"
    assert data["whatsapp_helpline"] == "+91 78747 19139"

    # POST sync
    res_sync = client.post("/api/cloud-shadow/sync", json={"mode": "full"})
    assert res_sync.status_code == 200
    sync_data = res_sync.json()
    assert sync_data["success"] is True

    # POST query
    res_query = client.post("/api/cloud-shadow/query", json={
        "query": "J-Series 350 cylinder head torque sequence",
        "sender": "Alpesh Sir Mobile"
    })
    assert res_query.status_code == 200
    query_data = res_query.json()
    assert query_data["success"] is True
    assert "Ramesh" in query_data["responding_agent"]

    # POST reconcile
    res_rec = client.post("/api/cloud-shadow/reconcile")
    assert res_rec.status_code == 200
    rec_data = res_rec.json()
    assert rec_data["success"] is True


def test_standalone_cloud_mirror_server_endpoints(cloud_client):
    # GET / (HTML Landing)
    res_home = cloud_client.get("/")
    assert res_home.status_code == 200
    assert "CHAMUNDA-CLOUD-SHADOW-HQ" in res_home.text
    assert "+91 78747 19139" in res_home.text

    # GET /api/health
    res_health = cloud_client.get("/api/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "HEALTHY_HOT_STANDBY"

    # GET /api/telemetry
    res_tel = cloud_client.get("/api/telemetry")
    assert res_tel.status_code == 200
    assert res_tel.json()["cluster_name"] == "CHAMUNDA-CLOUD-SHADOW-HQ"

    # POST /api/query
    res_q = cloud_client.post("/api/query", json={"query": "Classic 350 clutch plate stock"})
    assert res_q.status_code == 200
    assert "Jayesh" in res_q.json()["responding_agent"]
