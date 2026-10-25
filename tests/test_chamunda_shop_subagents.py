"""
Automated Test Suite for Chamunda Automobile Executive Sub-Agents Management Engine.
Validates the 5 specialized departmental sub-agents under CEO Aradhya:
1. bay_chief (Master Workshop & Bay Chief - Master Tech Ramesh)
2. parts_specialist (Inventory & OEM Parts Specialist - Jayeshbhai)
3. customer_receptionist (24/7 Front-Desk & WhatsApp Receptionist - Priya)
4. social_growth_manager (Omnichannel Brand & Growth Manager - Kabir)
5. accounts_controller (Billing & Finance Accounts Controller - Hasmukhbhai)
"""

import sys
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

RE_DIR = Path("/home/alpesh/chamunda_re_enterprise")
JARVIS_DIR = Path("/home/alpesh/jarvis-agent")

if str(RE_DIR) not in sys.path:
    sys.path.insert(0, str(RE_DIR))
if str(JARVIS_DIR) not in sys.path:
    sys.path.insert(0, str(JARVIS_DIR))

from shop_subagents_engine import ChamundaShopSubagentsManager
from core.agent_commander import AgentCommander
from tools.chamunda_ceo_tools import (
    chamunda_list_shop_subagents,
    chamunda_delegate_shop_task,
    chamunda_get_subagents_status,
    chamunda_execute_written_command,
    chamunda_heal_shop_subagent,
    chamunda_get_subagents_growth_telemetry
)
from app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_subagents_initialization():
    """Verify all 5 departmental sub-agents exist with proper leads and capabilities."""
    sub_mgr = ChamundaShopSubagentsManager()
    agents = sub_mgr.list_subagents()
    agent_ids = [a["agent_id"] for a in agents]

    assert len(agents) >= 5
    assert "bay_chief" in agent_ids
    assert "parts_specialist" in agent_ids
    assert "customer_receptionist" in agent_ids
    assert "social_growth_manager" in agent_ids
    assert "accounts_controller" in agent_ids

    # Verify specific details
    bay = sub_mgr.get_subagent("bay_chief")
    assert "Ramesh" in bay["designated_head"]

    parts = sub_mgr.get_subagent("parts_specialist")
    assert "Jayesh" in parts["designated_head"]

    rec = sub_mgr.get_subagent("customer_receptionist")
    assert "+91 78747 19139" in rec["status"]
    assert "Priya" in rec["designated_head"]

    soc = sub_mgr.get_subagent("social_growth_manager")
    assert "Kabir" in soc["designated_head"]

    acc = sub_mgr.get_subagent("accounts_controller")
    assert "Hasmukh" in acc["designated_head"]


def test_delegate_to_bay_chief():
    """Verify task delegation to Workshop & Bay Chief."""
    sub_mgr = ChamundaShopSubagentsManager()
    res = sub_mgr.delegate_task(
        agent_id="bay_chief",
        task_title="Classic 350 Valve Tappet Calibration",
        task_description="Verify intake 0.08 mm, exhaust 0.18 mm clearances on Hunter 350."
    )
    assert res["success"] is True
    assert "DEL-" in res["delegation_id"]
    assert "Ramesh" in res["designated_head"]
    assert res["delegation"]["status"] == "Completed"


def test_delegate_to_parts_specialist():
    """Verify task delegation to Spares Specialist."""
    sub_mgr = ChamundaShopSubagentsManager()
    res = sub_mgr.delegate_task(
        agent_id="parts_specialist",
        task_title="Audit Genuine Oil Filter Stock",
        task_description="Check shelf stock of Genuine Element Filter and Motul 15W-50 barrels."
    )
    assert res["success"] is True
    assert "Jayesh" in res["designated_head"]
    assert res["delegation"]["execution_details"]["active_skus"] >= 4000


def test_delegate_to_customer_receptionist():
    """Verify task delegation to 24/7 Front-Desk Receptionist."""
    sub_mgr = ChamundaShopSubagentsManager()
    res = sub_mgr.delegate_task(
        agent_id="customer_receptionist",
        task_title="Confirm Advance Service Bay Slot",
        task_description="Reserve Bay 1 for GJ-01-RE-2026 and dispatch WhatsApp confirmation."
    )
    assert res["success"] is True
    assert "Priya" in res["designated_head"]
    assert "+91 78747 19139" in res["delegation"]["execution_details"]["channel"]


def test_delegate_to_social_and_accounts():
    """Verify task delegation to Social Growth Manager and Accounts Controller."""
    sub_mgr = ChamundaShopSubagentsManager()

    # Social
    soc_res = sub_mgr.delegate_task(
        agent_id="social_growth_manager",
        task_title="Launch Thump Tuning Reel & YouTube Short",
        task_description="Syndicate video across all 5 channels with +91 78747 19139 CTA."
    )
    assert soc_res["success"] is True
    assert "Kabir" in soc_res["designated_head"]

    # Accounts
    acc_res = sub_mgr.delegate_task(
        agent_id="accounts_controller",
        task_title="Daily Counter UPI Reconciliation",
        task_description="Reconcile daily POS transactions and QR invoices with bank settlement."
    )
    assert acc_res["success"] is True
    assert "Hasmukh" in acc_res["designated_head"]


def test_executive_overview():
    """Verify CEO executive dashboard metrics."""
    sub_mgr = ChamundaShopSubagentsManager()
    ov = sub_mgr.get_executive_overview()
    assert ov["ceo_command"] == "Aradhya (Chief Executive Officer)"
    assert ov["departments_active"] >= 5
    assert ov["executive_suite_status"] == "ALL_DEPARTMENTS_OPERATIONAL"
    assert len(ov["recent_delegations"]) > 0


def test_agent_commander_subagents_integration():
    """Verify JARVIS AgentCommander integrates Chamunda shop subagents."""
    commander = AgentCommander()
    sub_agents = commander.list_subordinate_agents()
    agent_names = [a["name"] for a in sub_agents]

    assert "chamunda_bay_chief" in agent_names
    assert "chamunda_parts_specialist" in agent_names
    assert "chamunda_customer_receptionist" in agent_names

    # Test commanding via AgentCommander
    cmd_res = commander.command_agent(
        agent_name="chamunda_bay_chief",
        task="Audit 50-point inspection quality standards"
    )
    assert cmd_res["success"] is True
    assert "Ramesh" in cmd_res["designated_head"]


def test_ceo_tools_subagents():
    """Verify CEO tools for Aradhya AI agent."""
    list_out = chamunda_list_shop_subagents()
    assert "Executive Suite & Departmental Sub-Agents" in list_out
    assert "Master Workshop & Bay Chief" in list_out
    assert "Aradhya" in list_out

    del_out = chamunda_delegate_shop_task(
        agent_name="bay_chief",
        task="Inspect exhaust acoustic thump on Continental GT 650"
    )
    assert "Executive Directive Dispatched by CEO Aradhya" in del_out
    assert "Ramesh" in del_out

    status_out = chamunda_get_subagents_status()
    assert "CEO Executive Sub-Agents Dashboard" in status_out
    assert "ALL_DEPARTMENTS_OPERATIONAL" in status_out


def test_api_subagents_endpoints(client):
    """Verify all REST API endpoints for shop subagents."""
    # 1. List
    r = client.get("/api/agents/list")
    assert r.status_code == 200
    assert len(r.json()) >= 5

    # 2. Overview
    r = client.get("/api/agents/overview")
    assert r.status_code == 200
    assert r.json()["departments_active"] >= 5

    # 3. Delegate
    r = client.post("/api/agents/delegate", json={
        "agent_id": "parts_specialist",
        "task_title": "Wholesale PO for NGK Spark Plugs",
        "task_description": "Reorder 50 units of genuine spark plugs."
    })
    assert r.status_code == 200
    assert r.json()["success"] is True

    # 4. History
    r = client.get("/api/agents/history")
    assert r.status_code == 200
    assert len(r.json()) > 0

    # 5. Dashboard HTML Tab 12
    r = client.get("/")
    assert r.status_code == 200
    assert 'id="shop-subagents"' in r.text
    assert "Executive Sub-Agents" in r.text
    assert "Master Workshop &amp; Bay Chief" in r.text


def test_parse_written_command_intent():
    """Verify natural language written command parsing in Gujarati and English."""
    sub_mgr = ChamundaShopSubagentsManager()

    # 1. Bay Chief intent (Gujarati)
    p1 = sub_mgr.parse_written_command_intent("રમેશભાઈ Classic 350 એન્જિન સાઉન્ડ અને ટેપેટ ટ્યુનિંગ કરો")
    assert p1["target_agent_id"] == "bay_chief"
    assert p1["entities"].get("motorcycle_model") == "Classic 350"

    # 2. Parts Specialist intent (English + Urgent)
    p2 = sub_mgr.parse_written_command_intent("Urgent: Jayesh, order 50 NGK spark plugs and 20 bottles of Motul 15W50 oil")
    assert p2["target_agent_id"] == "parts_specialist"
    assert p2["priority"] == "Urgent"

    # 3. Customer Receptionist intent (Gujarati)
    p3 = sub_mgr.parse_written_command_intent("પ્રિયા, કસ્ટમર રાહુલને વ્હોટ્સએપ પર સર્વિસ રેડી મેસેજ મોકલો (+91 78747 19139)")
    assert p3["target_agent_id"] == "customer_receptionist"

    # 4. Social Growth Manager intent (English)
    p4 = sub_mgr.parse_written_command_intent("Kabir, publish our customized Himalayan 450 reel on Instagram and YouTube")
    assert p4["target_agent_id"] == "social_growth_manager"

    # 5. Accounts Controller intent (Gujarati + currency)
    p5 = sub_mgr.parse_written_command_intent("હસમુખભાઈ, ₹4,850 નું GST ટેક્સ ઇન્વોઇસ અને ડાયનેમિક UPI QR તૈયાર કરો")
    assert p5["target_agent_id"] == "accounts_controller"
    assert p5["entities"].get("amount") == "4850"


def test_execute_written_command_bay_and_parts():
    """Verify execution of written directives for bay and parts."""
    sub_mgr = ChamundaShopSubagentsManager()

    res_bay = sub_mgr.execute_written_command(
        command_text="રમેશભાઈ, Classic 350 વાલ્વ ટેપેટ ક્લિયરન્સ ચેક કરો",
        sender="Alpesh Sir (Founder & Chairman)",
        priority="High"
    )
    assert res_bay["success"] is True
    assert res_bay["target_agent"] == "bay_chief"
    assert "CMD-" in res_bay["command_id"]
    assert "રમેશભાઈ" in res_bay["response_gu"]
    assert "Ramesh" in res_bay["response_en"]

    res_parts = sub_mgr.execute_written_command(
        command_text="Jayeshbhai, check genuine oil filter stock and generate PO for 20W50 oil",
        sender="Aradhya (CEO)"
    )
    assert res_parts["success"] is True
    assert res_parts["target_agent"] == "parts_specialist"
    assert "જયેશભાઈ" in res_parts["response_gu"]


def test_execute_written_command_reception_social_accounts():
    """Verify execution of written directives for customer desk, social growth, and accounts."""
    sub_mgr = ChamundaShopSubagentsManager()

    # Receptionist
    res_rec = sub_mgr.execute_written_command(
        command_text="Priya, confirm service slot for rider Rahul (+91 78747 19139)",
        sender="Alpesh Sir (Founder & Chairman)"
    )
    assert res_rec["success"] is True
    assert res_rec["target_agent"] == "customer_receptionist"
    assert "+91 78747 19139" in res_rec["response_gu"]

    # Social
    res_soc = sub_mgr.execute_written_command(
        command_text="Kabir, syndicate weekend ride video across all 5 social media channels",
        sender="Aradhya (CEO)"
    )
    assert res_soc["success"] is True
    assert res_soc["target_agent"] == "social_growth_manager"

    # Accounts
    res_acc = sub_mgr.execute_written_command(
        command_text="હસમુખભાઈ, ₹3,200 નું કાઉન્ટર બિલ અને UPI QR કોડ જનરેટ કરો",
        sender="Alpesh Sir (Founder & Chairman)"
    )
    assert res_acc["success"] is True
    assert res_acc["target_agent"] == "accounts_controller"


def test_agent_commander_written_directive():
    """Verify JARVIS AgentCommander executes written directives."""
    commander = AgentCommander()
    res = commander.execute_written_directive(
        command_text="રમેશભાઈ, Continental GT 650 એન્જિન સાઉન્ડ અને એક્ઝોસ્ટ થમ્પ તપાસો",
        sender="Alpesh Sir (Founder & Chairman)"
    )
    assert res["success"] is True
    assert res["target_agent"] == "bay_chief"
    assert "CMD-" in res["command_id"]


def test_ceo_written_command_tool():
    """Verify CEO Aradhya chamunda_execute_written_command tool."""
    out = chamunda_execute_written_command(
        command="જયેશભાઈ, 50 સ્પાર્ક પ્લગ અને બ્રેક પેડનો હોલસેલ ઓર્ડર કરો",
        sender="Alpesh Sir (Founder & Chairman)"
    )
    assert "Executive Written Directive Executed" in out
    assert "Jayeshbhai Patel" in out
    assert "CMD-" in out
    assert "ગુજરાતી પ્રતિભાવ" in out


def test_api_written_command_endpoints(client):
    """Verify REST API endpoints for written commands."""
    # 1. Execute written command via POST
    res = client.post("/api/agents/command", json={
        "command": "રમેશભાઈ, Hunter 350 એન્જિન સાઉન્ડ ટેસ્ટિંગ કરો",
        "sender": "Alpesh Sir (Founder & Chairman)",
        "priority": "High"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["target_agent"] == "bay_chief"

    # 2. Get written commands history via GET
    res_hist = client.get("/api/agents/commands/history")
    assert res_hist.status_code == 200
    history = res_hist.json()
    assert len(history) > 0

    # 3. Verify Written Command Terminal in Dashboard HTML
    res_html = client.get("/")
    assert res_html.status_code == 200
    assert "Executive Written Command Terminal" in res_html.text
    assert "writtenCommandText" in res_html.text
    assert "submitWrittenCommand" in res_html.text


def test_subagent_diagnose_and_heal():
    """Verify all 5 subagents autonomously diagnose issues, synthesize fixes, and award XP."""
    sub_mgr = ChamundaShopSubagentsManager()

    # 1. Bay Chief (Acoustic valve tick)
    h_bay = sub_mgr.diagnose_and_heal_incident("bay_chief", "Abnormal valve tappet tick noise at 2800 RPM on Classic 350")
    assert h_bay["success"] is True
    assert "Hydraulic" in h_bay["new_skill_unlocked"]
    assert h_bay["xp_awarded"] == 50
    assert "રમેશભાઈ" in h_bay["solution_gu"]

    # 2. Parts Specialist (Shortage)
    h_parts = sub_mgr.diagnose_and_heal_incident("parts_specialist", "Out of stock warning for NGK BPR6ES spark plug")
    assert h_parts["success"] is True
    assert "Dual-Vendor" in h_parts["new_skill_unlocked"]
    assert "જયેશભાઈ" in h_parts["solution_gu"]

    # 3. Customer Receptionist (Highway SOS)
    h_cust = sub_mgr.diagnose_and_heal_incident("customer_receptionist", "Stranded rider breakdown SOS on highway near Mehsana")
    assert h_cust["success"] is True
    assert "Highway SOS" in h_cust["new_skill_unlocked"]
    assert "પ્રિયા" in h_cust["solution_gu"]

    # 4. Social Growth Manager (Negative review)
    h_soc = sub_mgr.diagnose_and_heal_incident("social_growth_manager", "Negative 1-star Google Business review on parts delivery")
    assert h_soc["success"] is True
    assert "Google Business" in h_soc["new_skill_unlocked"]
    assert "કબીર" in h_soc["solution_gu"]

    # 5. Accounts Controller (UPI timeout)
    h_acc = sub_mgr.diagnose_and_heal_incident("accounts_controller", "Counter POS dynamic UPI QR transaction timeout")
    assert h_acc["success"] is True
    assert "RRN" in h_acc["new_skill_unlocked"]
    assert "હસમુખભાઈ" in h_acc["solution_gu"]


def test_subagent_xp_and_leveling():
    """Verify XP progression, leveling thresholds, and persistent telemetry."""
    sub_mgr = ChamundaShopSubagentsManager()
    tele = sub_mgr.get_agent_growth_telemetry()

    for aid in ["bay_chief", "parts_specialist", "customer_receptionist", "social_growth_manager", "accounts_controller"]:
        assert aid in tele
        assert tele[aid]["level"] >= 1
        assert tele[aid]["xp"] > 0
        assert tele[aid]["issues_resolved_autonomously"] > 0


def test_auto_update_capabilities():
    """Verify that autonomous self-healing updates capabilities list in shop_subagents.json."""
    sub_mgr = ChamundaShopSubagentsManager()

    # Trigger custom incident with unique skill
    res = sub_mgr.record_growth_and_xp(
        agent_id="bay_chief",
        xp_earned=50,
        skill_learned="Autonomous Test Skill: Advanced Twin-Cylinder Exhaust Tuning",
        problem="Test exhaust rumble anomaly",
        solution="Recalibrated test dual-channel manifold"
    )
    assert res["level"] >= 1

    updated_bay = sub_mgr.get_subagent("bay_chief")
    assert "Autonomous Test Skill: Advanced Twin-Cylinder Exhaust Tuning" in updated_bay.get("capabilities", [])


def test_agent_commander_subagent_healing():
    """Verify JARVIS AgentCommander integrates Chamunda shop subagents healing."""
    commander = AgentCommander()
    heal_out = commander.diagnose_and_heal_subagent(
        agent_name="chamunda_bay_chief",
        error_log="Exhaust thump noise exceeded 88 dB threshold on Hunter 350"
    )
    assert "Chamunda Sub-Agent Autonomous Self-Healing Executed" in heal_out
    assert "Ramesh" in heal_out
    assert "Fix Applied" in heal_out


def test_ceo_heal_and_growth_tools():
    """Verify CEO Aradhya heal and growth telemetry tools."""
    heal_str = chamunda_heal_shop_subagent(
        agent_name="parts_specialist",
        issue="Counterfeit barcode scan detected on shipment batch #RE-990"
    )
    assert "Autonomous Sub-Agent Self-Healing Report" in heal_str
    assert "Jayeshbhai Patel" in heal_str
    assert "Quarantine" in heal_str or "Fix Applied" in heal_str

    growth_str = chamunda_get_subagents_growth_telemetry()
    assert "Sub-Agents Growth & Self-Healing Telemetry" in growth_str
    assert "Level" in growth_str
    assert "Fix Rate" in growth_str


def test_api_growth_and_healing_endpoints(client):
    """Verify REST API endpoints for growth, heal, and simulation."""
    # 1. GET /api/agents/growth
    r_growth = client.get("/api/agents/growth")
    assert r_growth.status_code == 200
    g_data = r_growth.json()
    assert "bay_chief" in g_data
    assert g_data["bay_chief"]["level"] >= 1

    # 2. POST /api/agents/simulate-incident
    r_sim = client.post("/api/agents/simulate-incident", json={
        "agent_id": "bay_chief",
        "incident_type": "Tappet valve noise simulation"
    })
    assert r_sim.status_code == 200
    sim_data = r_sim.json()
    assert sim_data["success"] is True
    assert "Ramesh" in sim_data["designated_head"]

    # 3. POST /api/agents/heal
    r_heal = client.post("/api/agents/heal", json={
        "agent_id": "customer_receptionist",
        "issue": "Highway breakdown SOS signal near Mehsana"
    })
    assert r_heal.status_code == 200
    heal_data = r_heal.json()
    assert heal_data["success"] is True
    assert "Priya" in heal_data["designated_head"]

    # 4. Check UI elements in Dashboard HTML
    r_html = client.get("/")
    assert r_html.status_code == 200
    assert "Autonomous Sub-Agent Growth &amp; Self-Healing Engine" in r_html.text
    assert "subagentGrowthGrid" in r_html.text
    assert "triggerIncidentSimulation" in r_html.text


