"""
Unit and Integration Test Suite for Project Chhaya Universal Mobile Agent Gateway.
Tests single main link directory, dedicated mobile workspaces, dynamic future agent discovery,
bilingual routing, and REST API endpoints across ports 8080 and 8081.

Helpline Compliance: Strictly +91 78747 19139.
"""

import sys
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
sys.path.insert(0, "/home/alpesh/jarvis-agent")

from chhaya_agent_gateway import get_chhaya_agent_gateway, OFFICIAL_WHATSAPP_HELPLINE
from app import app as workshop_app
from cloud_mirror_server import app as cloud_mirror_app


@pytest.fixture
def client_workshop():
    return TestClient(workshop_app)


@pytest.fixture
def client_mirror():
    return TestClient(cloud_mirror_app)


# =============================================================================
# 1. CORE GATEWAY REGISTRY & DISCOVERY TESTS
# =============================================================================

def test_gateway_loads_all_standard_and_discovered_agents():
    gw = get_chhaya_agent_gateway()
    agents = gw.list_all_agents()
    agent_ids = [a["agent_id"] for a in agents]

    # Verify minimum 16 agents
    assert len(agents) >= 16

    # 10 Dealership Officers
    dealership_officers = [
        "aradhya_ceo", "bay_chief", "parts_specialist", "customer_receptionist",
        "social_growth_manager", "accounts_controller", "devang_billing",
        "neha_crm_marketing", "vikram_sales", "ananya_qc_csat"
    ]
    for do in dealership_officers:
        assert do in agent_ids, f"Missing dealership officer: {do}"

    # System Engineering Agents
    assert "jarvis_master" in agent_ids
    assert "web2apk_agent" in agent_ids
    assert "web2ipa_agent" in agent_ids

    # Media & Creative Agents
    assert "youtube_agent" in agent_ids
    assert "book_publishing_agent" in agent_ids
    assert "game_studio_agent" in agent_ids


def test_gateway_category_filtering():
    gw = get_chhaya_agent_gateway()

    dealership = gw.list_all_agents(category="DEALERSHIP_OFFICER")
    assert len(dealership) >= 10
    for a in dealership:
        assert a["category"] == "DEALERSHIP_OFFICER"

    system = gw.list_all_agents(category="SYSTEM_ENGINEERING")
    assert len(system) >= 3
    for a in system:
        assert a["category"] == "SYSTEM_ENGINEERING"

    media = gw.list_all_agents(category="MEDIA_CREATIVE")
    assert len(media) >= 3
    for a in media:
        assert a["category"] == "MEDIA_CREATIVE"


def test_gateway_agent_metadata_and_quick_chips():
    gw = get_chhaya_agent_gateway()

    vikram = gw.get_agent("vikram_sales")
    assert vikram is not None
    assert "Vikram Singh" in vikram["designated_head"]
    assert len(vikram["capabilities"]) >= 3
    assert len(vikram["quick_chips"]) >= 2

    devang = gw.get_agent("devang_billing")
    assert devang is not None
    assert "Devang Dave" in devang["designated_head"]

    jarvis = gw.get_agent("jarvis_master")
    assert jarvis is not None
    assert "Jarvis Core" in jarvis["designated_head"]


# =============================================================================
# 2. BILINGUAL CHAT & COMMAND DISPATCHING TESTS
# =============================================================================

def test_gateway_chat_with_dealership_officers():
    gw = get_chhaya_agent_gateway()

    # Chat with Vikram Sales
    res_vikram = gw.chat_with_agent("vikram_sales", "Book new Classic 350 for Alpesh Sir")
    assert res_vikram["success"] is True
    assert res_vikram["agent_id"] == "vikram_sales"
    assert "Vikram Singh" in res_vikram["responding_agent"]
    assert len(res_vikram["response_en"]) > 0
    assert len(res_vikram["response_gu"]) > 0
    assert res_vikram["helpline"] == OFFICIAL_WHATSAPP_HELPLINE

    # Chat with Bay Chief Ramesh
    res_ramesh = gw.chat_with_agent("bay_chief", "Check cylinder head torque sequence")
    assert res_ramesh["success"] is True
    assert "Ramesh" in res_ramesh["responding_agent"]

    # Chat with Devang Billing
    res_devang = gw.chat_with_agent("devang_billing", "Generate split GST invoice")
    assert res_devang["success"] is True
    assert "Devang Dave" in res_devang["responding_agent"]

    # Chat with Ananya QC & CSAT
    res_ananya = gw.chat_with_agent("ananya_qc_csat", "Record 5 star CSAT feedback")
    assert res_ananya["success"] is True
    assert "Ananya Joshi" in res_ananya["responding_agent"]


def test_gateway_chat_with_engineering_and_creative_agents():
    gw = get_chhaya_agent_gateway()

    # Chat with Jarvis Master
    res_jarvis = gw.chat_with_agent("jarvis_master", "Run system health check and clean RAM")
    assert res_jarvis["success"] is True
    assert "Jarvis Master" in res_jarvis["response_en"]
    assert "જાર્વિસ" in res_jarvis["response_gu"]

    # Chat with Web2APK
    res_apk = gw.chat_with_agent("web2apk_agent", "Build Android APK package")
    assert res_apk["success"] is True
    assert "Web2APK" in res_apk["response_en"]

    # Chat with YouTube Agent
    res_yt = gw.chat_with_agent("youtube_agent", "Create video script for Himalayan 450")
    assert res_yt["success"] is True
    assert "YouTube" in res_yt["response_en"]


# =============================================================================
# 3. FUTURE AGENT DYNAMIC EXTENSION TESTS
# =============================================================================

def test_gateway_dynamic_future_agent_registration():
    gw = get_chhaya_agent_gateway()

    future_agent_payload = {
        "agent_id": "test_future_drone_agent",
        "name": "Aerial Drone Inspection Agent",
        "name_gu": "ડ્રોન ઇન્સ્પેક્શન એજન્ટ",
        "designated_head": "SkyHawk Drone Controller",
        "department": "Aerial Facility Surveillance",
        "category": "CUSTOM_FUTURE",
        "icon": "fa-solid fa-helicopter",
        "color": "#e056fd",
        "capabilities": ["Aerial Yard Inspection", "Roof Solar Array Audit"],
        "quick_chips": [{"label": "🚁 Drone Survey", "query": "Launch aerial surveillance of workshop"}]
    }

    reg_res = gw.register_future_agent(future_agent_payload)
    assert reg_res["success"] is True
    assert reg_res["agent"]["agent_id"] == "test_future_drone_agent"

    # Verify immediate availability in directory
    retrieved = gw.get_agent("test_future_drone_agent")
    assert retrieved is not None
    assert retrieved["name"] == "Aerial Drone Inspection Agent"

    # Test direct mobile chat with the new future agent
    chat_res = gw.chat_with_agent("test_future_drone_agent", "Scan workshop perimeter")
    assert chat_res["success"] is True
    assert chat_res["agent_id"] == "test_future_drone_agent"
    assert "SkyHawk Drone Controller" in chat_res["responding_agent"]


# =============================================================================
# 4. FASTAPI REST API ENDPOINTS TESTS (Ports 8080 & 8081)
# =============================================================================

def test_fastapi_workshop_chhaya_endpoints(client_workshop):
    # GET /api/chhaya/agents
    res = client_workshop.get("/api/chhaya/agents")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["count"] >= 16

    # GET /api/chhaya/agents/{agent_id}
    res_agent = client_workshop.get("/api/chhaya/agents/vikram_sales")
    assert res_agent.status_code == 200
    data_agent = res_agent.json()
    assert data_agent["success"] is True
    assert data_agent["agent"]["agent_id"] == "vikram_sales"

    # POST /api/chhaya/agents/{agent_id}/chat
    res_chat = client_workshop.post("/api/chhaya/agents/vikram_sales/chat", json={
        "message": "Vikram confirm token receipt for Classic 350"
    })
    assert res_chat.status_code == 200
    data_chat = res_chat.json()
    assert data_chat["success"] is True
    assert "Vikram Singh" in data_chat["responding_agent"]


def test_fastapi_mirror_server_hub_and_workspaces(client_mirror):
    # GET / (Single main link HTML)
    res_home = client_mirror.get("/")
    assert res_home.status_code == 200
    html = res_home.text

    # Must contain Universal Hub, Agent Directory, and Workspace components
    assert "Universal Multi-Agent Command Center" in html
    assert 'id="hubView"' in html
    assert 'id="workspaceView"' in html
    assert 'id="agentsCardsContainer"' in html
    assert 'id="agentQuickDropdown"' in html
    assert 'id="wsChatInput"' in html
    assert "+91 78747 19139" in html

    # GET /api/chhaya/agents on mirror server
    res_agents = client_mirror.get("/api/chhaya/agents")
    assert res_agents.status_code == 200
    assert res_agents.json()["count"] >= 16

    # POST chat with Jarvis on mirror server
    res_jarvis = client_mirror.post("/api/chhaya/agents/jarvis_master/chat", json={
        "message": "Jarvis verify 24/7 background daemons"
    })
    assert res_jarvis.status_code == 200
    assert res_jarvis.json()["success"] is True
