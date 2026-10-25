"""
Automated Test Suite for Chamunda Automobile 24/7 WhatsApp AI Bot Number Configuration.
Verifies phone number 7874719139 (+91 78747 19139, raw 7874719139, wa.me/917874719139)
is correctly configured and active across all engines, API endpoints, receptionist, and tools.
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

import customer_bot_engine
from customer_bot_engine import (
    ChamundaCustomerBot,
    WHATSAPP_BOT_NUMBER,
    WHATSAPP_BOT_RAW,
    WHATSAPP_BOT_LINK
)
from core.whatsapp_receptionist import (
    WhatsAppServiceReceptionist,
    BOT_PHONE,
    BOT_RAW_NUMBER,
    BOT_WHATSAPP_LINK
)
from tools.chamunda_ceo_tools import chamunda_track_customer_service_status
from app import app


@pytest.fixture
def test_client():
    return TestClient(app)


def test_customer_bot_constants():
    """Verify official WhatsApp bot number constants in customer_bot_engine."""
    assert WHATSAPP_BOT_NUMBER == "+91 78747 19139"
    assert WHATSAPP_BOT_RAW == "7874719139"
    assert WHATSAPP_BOT_LINK == "https://wa.me/917874719139"


def test_customer_bot_contact_info_method():
    """Verify get_bot_contact_info returns accurate dictionary."""
    bot = ChamundaCustomerBot()
    info = bot.get_bot_contact_info()
    assert info["phone"] == "+91 78747 19139"
    assert info["raw_number"] == "7874719139"
    assert info["whatsapp_url"] == "https://wa.me/917874719139"
    assert "Alpesh" in info["operator"]


def test_track_service_status_includes_bot_number():
    """Verify tracking messages and payload contain WhatsApp bot contact info."""
    bot = ChamundaCustomerBot()
    res = bot.track_service_status("GJ-01-RE-3500")
    assert res["found"] is True
    assert res["bot_phone"] == "+91 78747 19139"
    assert res["bot_whatsapp_url"] == "https://wa.me/917874719139"
    assert "+91 78747 19139" in res["message_gu"]
    assert "+91 78747 19139" in res["message_en"]
    assert "https://wa.me/917874719139" in res["message_gu"]


def test_book_service_slot_includes_bot_number():
    """Verify advance booking confirmations contain official WhatsApp bot details."""
    bot = ChamundaCustomerBot()
    res = bot.book_service_slot(
        customer_name="Parthivbhai",
        phone="+91 98250 99999",
        bike_model="Meteor 350",
        registration_no="GJ-01-RE-7788"
    )
    assert res["success"] is True
    assert res["bot_phone"] == "+91 78747 19139"
    assert res["bot_whatsapp_url"] == "https://wa.me/917874719139"
    assert "+91 78747 19139" in res["message_gu"]
    assert "+91 78747 19139" in res["message_en"]


def test_customer_bot_chat_router_with_bot_number():
    """Verify greeting and workshop info responses include WhatsApp number & link."""
    bot = ChamundaCustomerBot()
    # Greeting
    greet = bot.process_customer_message("નમસ્તે")
    assert "+91 78747 19139" in greet["reply_gu"]
    assert "https://wa.me/917874719139" in greet["reply_gu"]

    # Workshop info
    info_res = bot.process_customer_message("સરનામું અને સમય જણાવો")
    assert "+91 78747 19139" in info_res["reply_gu"]
    assert info_res["data"]["whatsapp_bot"] == "+91 78747 19139"
    assert info_res["data"]["raw_number"] == "7874719139"


def test_whatsapp_receptionist_number():
    """Verify WhatsAppServiceReceptionist uses 7874719139 and generates proper link."""
    assert BOT_PHONE == "+91 78747 19139"
    assert BOT_RAW_NUMBER == "7874719139"
    assert BOT_WHATSAPP_LINK == "https://wa.me/917874719139"

    receptionist = WhatsAppServiceReceptionist()
    details = receptionist.get_receptionist_contact_info()
    assert details["phone"] == "+91 78747 19139"
    assert details["whatsapp_link"] == "https://wa.me/917874719139"

    inquiry_res = receptionist.handle_incoming_inquiry(
        customer_name="Jayesh Patel",
        phone="+91 98250 11223",
        bike_model="Classic 350",
        requested_slot="Tomorrow 11:00 AM",
        customer_message="Periodic engine sound inspection"
    )
    assert inquiry_res["bot_phone"] == "+91 78747 19139"
    assert "+91 78747 19139" in inquiry_res["whatsapp_reply"]
    assert "https://wa.me/917874719139" in inquiry_res["whatsapp_reply"]


def test_ceo_tool_tracking_output():
    """Verify chamunda_track_customer_service_status tool displays WhatsApp bot number."""
    out = chamunda_track_customer_service_status("GJ-01-RE-3500")
    assert "+91 78747 19139" in out
    assert "https://wa.me/917874719139" in out


def test_api_bot_info_endpoint(test_client):
    """Verify GET /api/bot/info returns status 200 and official contact info."""
    res = test_client.get("/api/bot/info")
    assert res.status_code == 200
    data = res.json()
    assert data["phone"] == "+91 78747 19139"
    assert data["raw_number"] == "7874719139"
    assert data["whatsapp_url"] == "https://wa.me/917874719139"


def test_portal_html_contains_bot_number(test_client):
    """Verify portal root page includes direct WhatsApp button with 7874719139."""
    res = test_client.get("/")
    assert res.status_code == 200
    assert "7874719139" in res.text
    assert "https://wa.me/917874719139" in res.text
