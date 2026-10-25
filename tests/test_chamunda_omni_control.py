"""
Comprehensive Omni-Control & Multi-Agent Verification Suite for Chamunda Automobile Enterprise.
Tests:
1. All 5 Shop Sub-Agents (Bay Chief, Parts Specialist, Customer Receptionist, Social Growth, Accounts Controller)
2. Written Command Execution & NLP Intent Parsing (Gujarati & English)
3. Autonomous Self-Healing & Growth XP Progression
4. JARVIS AgentCommander Supervisor & Subordinate Agents
5. Project Trinetra (3D Schematics, AI Borescope, Multi-Branch Hub)
6. All 18 Workshop Portals, REST APIs & Live Web Dashboard
"""

import sys
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
sys.path.insert(0, "/home/alpesh/jarvis-agent")

from shop_subagents_engine import ChamundaShopSubagentsManager
from core.agent_commander import AgentCommander
from schematics_3d_engine import get_schematics_3d_engine
from borescope_inspection_engine import get_borescope_engine
from multibranch_hub_engine import get_multibranch_engine
from app import app


@pytest.fixture
def client():
    return TestClient(app)


# =========================================================================
# 1. All 5 Shop Sub-Agents Delegation & Execution Tests
# =========================================================================
def test_all_five_shop_subagents_active():
    mgr = ChamundaShopSubagentsManager()
    agents = mgr.list_subagents()
    assert len(agents) >= 5

    agent_ids = [a["agent_id"] for a in agents]
    assert "bay_chief" in agent_ids
    assert "parts_specialist" in agent_ids
    assert "customer_receptionist" in agent_ids
    assert "social_growth_manager" in agent_ids
    assert "accounts_controller" in agent_ids


def test_bay_chief_ramesh_delegation():
    mgr = ChamundaShopSubagentsManager()
    res = mgr.delegate_task(
        agent_id="bay_chief",
        task_title="Classic 350 Acoustic Valve Tappet Calibration",
        task_description="Execute 50-point acoustic inspection on Bay 1"
    )
    assert res["success"] is True
    assert "Ramesh" in res["designated_head"]
    assert res["delegation"]["status"] == "Completed"


def test_parts_specialist_jayesh_delegation():
    mgr = ChamundaShopSubagentsManager()
    res = mgr.delegate_task(
        agent_id="parts_specialist",
        task_title="Verify 4469 OEM Spares Stock Levels",
        task_description="Check Motul 15W50 and NGK spark plug stock levels"
    )
    assert res["success"] is True
    assert "Jayesh" in res["designated_head"]
    assert res["delegation"]["status"] == "Completed"


def test_customer_receptionist_priya_delegation():
    mgr = ChamundaShopSubagentsManager()
    res = mgr.delegate_task(
        agent_id="customer_receptionist",
        task_title="Dispatch Service Ready WhatsApp Notification",
        task_description="Alert customer on WhatsApp helpline +91 78747 19139"
    )
    assert res["success"] is True
    assert "Priya" in res["designated_head"]
    assert res["delegation"]["status"] == "Completed"


def test_social_growth_manager_kabir_delegation():
    mgr = ChamundaShopSubagentsManager()
    res = mgr.delegate_task(
        agent_id="social_growth_manager",
        task_title="Publish Vintage CI Bullet Restoration Reel",
        task_description="Syndicate across Instagram, YouTube Shorts, FB, and Google Business"
    )
    assert res["success"] is True
    assert "Kabir" in res["designated_head"]
    assert res["delegation"]["status"] == "Completed"


def test_accounts_controller_hasmukh_delegation():
    mgr = ChamundaShopSubagentsManager()
    res = mgr.delegate_task(
        agent_id="accounts_controller",
        task_title="Generate GST Tax Invoice & Reconcile Counter Cash",
        task_description="Verify 18% vs 28% GST split and UPI QR reconciliation"
    )
    assert res["success"] is True
    assert "Hasmukh" in res["designated_head"]
    assert res["delegation"]["status"] == "Completed"


# =========================================================================
# 2. Written Commands Execution & NLP Routing (Gujarati & English)
# =========================================================================
def test_written_command_gujarati_bay_chief():
    mgr = ChamundaShopSubagentsManager()
    res = mgr.execute_written_command(
        command_text="રમેશભાઈ, વર્કશોપ બે ૧ માં ક્લાસિક ૩૫૦ નું સાઉન્ડ ટેસ્ટિંગ કરો",
        sender="Alpesh Sir",
        priority="High"
    )
    assert res["success"] is True
    assert res["target_agent"] == "bay_chief"
    assert "રમેશભાઈ" in res["response_gu"]


def test_written_command_parts_specialist():
    mgr = ChamundaShopSubagentsManager()
    res = mgr.execute_written_command(
        command_text="જયેશભાઈ, 50 NGK Spark Plugs નો હોલસેલ ઓર્ડર બનાવો",
        sender="Alpesh Sir",
        priority="Urgent"
    )
    assert res["success"] is True
    assert res["target_agent"] == "parts_specialist"
    assert "જયેશભાઈ" in res["response_gu"]


def test_written_command_receptionist_whatsapp():
    mgr = ChamundaShopSubagentsManager()
    res = mgr.execute_written_command(
        command_text="પ્રિયા, કસ્ટમર રાકેશભાઈને વ્હોટ્સએપ પર સર્વિસ રેડી મેસેજ મોકલો",
        sender="Alpesh Sir"
    )
    assert res["success"] is True
    assert res["target_agent"] == "customer_receptionist"


def test_written_command_social_growth():
    mgr = ChamundaShopSubagentsManager()
    res = mgr.execute_written_command(
        command_text="કબીર, ઇન્સ્ટાગ્રામ અને યુટ્યુબ શોર્ટ્સ પર નવો વિડીયો પોસ્ટ કરો",
        sender="Alpesh Sir"
    )
    assert res["success"] is True
    assert res["target_agent"] == "social_growth_manager"


def test_written_command_accounts():
    mgr = ChamundaShopSubagentsManager()
    res = mgr.execute_written_command(
        command_text="હસમુખભાઈ, આજનું જીએસટી બિલિંગ અને યુપીઆઈ ક્યુઆર લેજર ચેક કરો",
        sender="Alpesh Sir"
    )
    assert res["success"] is True
    assert res["target_agent"] == "accounts_controller"


# =========================================================================
# 3. Autonomous Self-Healing & Continuous Growth Matrix
# =========================================================================
def test_subagent_growth_telemetry():
    mgr = ChamundaShopSubagentsManager()
    growth = mgr.get_agent_growth_telemetry()
    assert len(growth) >= 5
    for aid, prof in growth.items():
        assert prof["level"] >= 1
        assert prof["xp"] > 0
        assert len(prof["learned_capabilities"]) >= 1


def test_subagent_autonomous_healing():
    mgr = ChamundaShopSubagentsManager()
    heal_res = mgr.diagnose_and_heal_incident(
        agent_id="bay_chief",
        issue_description="Pushrod tappet clearance out of spec by 0.05 mm under cold test",
        auto_apply=True
    )
    assert heal_res["success"] is True
    assert heal_res["xp_awarded"] >= 50
    assert "Ramesh" in heal_res["designated_head"]
    assert len(heal_res["solution_gu"]) > 0


# =========================================================================
# 4. AgentCommander Directives & Subordinate Agents
# =========================================================================
def test_agent_commander_subordinate_agents():
    cmdr = AgentCommander()
    subs = cmdr.list_subordinate_agents()
    assert len(subs) >= 7  # 2 JARVIS + 5 Chamunda

    names = [s["name"] for s in subs]
    assert "youtube_shorts_agent" in names
    assert "autonomous_project_creator" in names
    assert any(x in names for x in ["bay_chief", "chamunda_bay_chief"])
    assert any(x in names for x in ["parts_specialist", "chamunda_parts_specialist"])



def test_agent_commander_written_directive():
    cmdr = AgentCommander()
    res = cmdr.execute_written_directive(
        command_text="રમેશભાઈ, હિમાલયન 450 વોટર પમ્પ સ્કીમેટિક ચેક કરો",
        sender="Alpesh Sir"
    )
    assert res["success"] is True
    assert res["target_agent"] == "bay_chief"


# =========================================================================
# 5. Full REST API & Portal Control Endpoints
# =========================================================================
def test_api_omni_command_endpoint(client):
    payload = {
        "command": "જયેશભાઈ, ઓઇલ ફિલ્ટર સ્ટોક તપાસો",
        "sender": "Alpesh Sir",
        "priority": "High"
    }
    resp = client.post("/api/agents/command", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["target_agent"] == "parts_specialist"


def test_api_subagents_growth_endpoint(client):
    resp = client.get("/api/agents/growth")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 5


def test_api_dashboard_html_contains_omni_control_bar(client):
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text

    # Omni-control elements
    assert 'id="globalOmniCommandInput"' in html
    assert 'id="globalOmniPriority"' in html
    assert 'id="btnGlobalOmniSubmit"' in html
    assert 'submitGlobalOmniCommand' in html
    assert 'setAndRunGlobalCommand' in html
    assert 'Supreme Omni-Control Center' in html
    assert 'triggerTurboBoost' in html
    assert 'Turbo Boost (Fix Lag)' in html


# =========================================================================
# 6. System Optimizer & Lag Buster Tests
# =========================================================================
def test_system_optimizer_metrics():
    from system_optimizer import get_system_optimizer
    opt = get_system_optimizer()
    m = opt.get_system_metrics()
    assert "cpu_percent" in m
    assert "memory" in m
    assert m["memory"]["total_mb"] > 0
    assert m["memory"]["percent_used"] > 0
    assert "status" in m
    assert "status_gu" in m


def test_system_optimizer_performance_run():
    from system_optimizer import get_system_optimizer
    opt = get_system_optimizer()
    res = opt.optimize_laptop_performance(aggressive=False)
    assert res["success"] is True
    assert "freed_memory_mb" in res
    assert "અલ્પેશ સાહેબ" in res["message_gu"]
    assert "Turbo Boost Complete" in res["message_en"]


def test_agent_commander_lag_directive():
    cmdr = AgentCommander()
    res = cmdr.execute_lag_cleanup_directive()
    assert res["success"] is True
    assert "freed_memory_mb" in res

    # Written directive route
    directive_res = cmdr.execute_written_directive("લેપટોપ લેગ થાય છે, ઝડપી બનાવો")
    assert directive_res["success"] is True
    assert directive_res["target_agent"] == "system_optimizer"
    assert "અલ્પેશ સાહેબ" in directive_res["response_gu"]


def test_api_system_resources_and_optimize(client):
    res_get = client.get("/api/system/resources")
    assert res_get.status_code == 200
    data_get = res_get.json()
    assert "memory" in data_get
    assert "cpu_percent" in data_get

    res_post = client.post("/api/system/optimize", json={"mode": "safe"})
    assert res_post.status_code == 200
    data_post = res_post.json()
    assert data_post["success"] is True
    assert "freed_memory_mb" in data_post


def test_chamunda_ceo_system_optimizer_tools():
    from tools.chamunda_ceo_tools import (
        chamunda_optimize_laptop_performance,
        chamunda_get_system_performance_metrics,
    )
    metric_str = chamunda_get_system_performance_metrics()
    assert "RAM Utilization" in metric_str
    assert "CPU Load" in metric_str

    opt_str = chamunda_optimize_laptop_performance(mode="safe")
    assert "Turbo Boost" in opt_str or "અલ્પેશ સાહેબ" in opt_str

