"""
Tests for Aradhya 24/7 Cloud Sentinel & Mobile Access Bridge.
"""

import os
import sys
import json
import time
import pytest
from fastapi.testclient import TestClient

from config.settings import load_config
from cloud_mobile_bridge.mobile_agent_server import (
    CloudMobileAgent,
    app,
    QUEUE_FILE,
    HEARTBEAT_FILE,
)
from core.cloud_sync import CloudSyncManager
from core.agent import JarvisAgent
from core.offline_commander import OfflineCommander


@pytest.fixture
def agent():
    return CloudMobileAgent()


@pytest.fixture
def client():
    return TestClient(app)


def test_cloud_mobile_agent_commands(agent):
    # Test /ceo command
    ceo_res = agent.process_command("/ceo")
    assert "CHAMUNDA" in ceo_res
    assert "Stock" in ceo_res

    # Test /parts command
    parts_res = agent.process_command("/parts Hunter 350")
    assert "Royal Enfield Spares" in parts_res or "રોયલ એનફિલ્ડ" in parts_res

    # Test /diag command
    diag_res = agent.process_command("/diag tappet noise")
    assert "valve clearance" in diag_res.lower() or "tappet" in diag_res.lower()


def test_cloud_mobile_agent_laptop_offline_task_queuing(agent):
    # Ensure laptop is marked offline by removing heartbeat or setting timestamp to past
    HEARTBEAT_FILE.write_text(json.dumps({"timestamp": time.time() - 500, "info": {}}), encoding="utf-8")
    assert agent.is_laptop_online() is False

    # When laptop is off, issuing a laptop directive must queue the task into cloud mailbox
    res = agent.process_command("લેપટોપ સ્પીડ બૂસ્ટ ચલાવો")
    assert res.get("task_queued") is True
    assert "task_id" in res
    assert "બંધ" in str(res) or "Offline" in str(res)

    # Verify task exists in pending queue
    pending = agent.get_pending_tasks()
    task_ids = [t["id"] for t in pending]
    assert res["task_id"] in task_ids


def test_cloud_mobile_agent_heartbeat_and_telemetry(agent):
    # Send live heartbeat
    heartbeat_payload = {
        "hostname": "alpesh-laptop",
        "battery_percent": 92,
        "power_plugged": True,
        "cpu_percent": 14.5,
        "ram_percent": 48.0,
        "agent_status": "ONLINE"
    }
    hb_res = agent.record_heartbeat(heartbeat_payload)
    assert hb_res["status"] == "ok"
    assert agent.is_laptop_online() is True

    # Check telemetry
    telem = agent.get_laptop_telemetry()
    assert telem["is_online"] is True
    assert "ONLINE" in telem["status_label"]
    assert telem["details"]["battery_percent"] == 92


def test_cloud_mobile_task_completion(agent):
    task = agent.queue_laptop_task("ls -la /home/alpesh", source="test")
    task_id = task["id"]

    # Verify it is in pending
    pending_ids = [t["id"] for t in agent.get_pending_tasks()]
    assert task_id in pending_ids

    # Complete the task
    success = agent.complete_task(task_id, result="Directory listing finished", success=True)
    assert success is True

    # Verify it is no longer pending
    pending_ids_after = [t["id"] for t in agent.get_pending_tasks()]
    assert task_id not in pending_ids_after


def test_fastapi_endpoints(client):
    # 1. GET / - Mobile Web Portal
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert "AROHI 24/7 CLOUD SENTINEL" in res_root.text

    # 2. POST /api/chat - Chat with Cloud Sentinel
    res_chat = client.post("/api/chat", json={"message": "લેપટોપ સ્ટેટસ શું છે?"})
    assert res_chat.status_code == 200
    chat_data = res_chat.json()
    assert "reply" in chat_data
    assert len(chat_data["reply"]) > 10

    # 3. POST /api/heartbeat
    res_hb = client.post("/api/heartbeat", json={"hostname": "test-laptop", "battery_percent": 85})
    assert res_hb.status_code == 200
    assert res_hb.json().get("status") == "ok"

    # 4. GET /api/status
    res_st = client.get("/api/status")
    assert res_st.status_code == 200
    st_data = res_st.json()
    assert st_data["agent_name"] == "Aradhya"
    assert st_data["cloud_sentinel_online"] is True

    # 5. POST /api/tasks/queue and GET /api/tasks/pending
    res_q = client.post("/api/tasks/queue", json={"message": "run security audit"})
    assert res_q.status_code == 200
    q_data = res_q.json()
    task_id = q_data["task"]["id"]

    res_pending = client.get("/api/tasks/pending")
    assert res_pending.status_code == 200
    pending_list = [t["id"] for t in res_pending.json()["tasks"]]
    assert task_id in pending_list

    # 6. POST /api/tasks/complete
    res_comp = client.post("/api/tasks/complete", json={"task_id": task_id, "result": "Audit complete", "success": True})
    assert res_comp.status_code == 200
    assert res_comp.json()["success"] is True


def test_wake_on_lan_packet():
    # Valid MAC address
    valid_res = CloudSyncManager.send_wake_on_lan("00:11:22:33:44:55")
    assert valid_res["success"] is True
    assert "magic packet successfully transmitted" in valid_res["message"].lower()

    # Invalid MAC address format
    invalid_res = CloudSyncManager.send_wake_on_lan("invalid-mac")
    assert invalid_res["success"] is False
    assert "invalid mac" in invalid_res["message"].lower()


def test_agent_registered_cloud_tools():
    cfg = load_config()
    agent = JarvisAgent(cfg)
    expected_tools = [
        "check_cloud_sentinel_status",
        "sync_cloud_task_queue",
        "send_wake_on_lan_signal",
    ]
    for tool_name in expected_tools:
        assert tool_name in agent.registry.tools, f"Tool '{tool_name}' missing from agent registry"


def test_offline_commander_cloud_intents():
    cfg = load_config()
    commander = OfflineCommander(cfg)

    # Gujarati intent
    res_gu = commander.execute_offline_turn("ક્લાઉડ સ્ટેટસ શું છે?")
    assert "ક્લાઉડ" in res_gu or "Cloud" in res_gu

    # English intent
    cfg.language = "english"
    commander_en = OfflineCommander(cfg)
    res_en = commander_en.execute_offline_turn("cloud status")
    assert "Cloud" in res_en or "Sentinel" in res_en
