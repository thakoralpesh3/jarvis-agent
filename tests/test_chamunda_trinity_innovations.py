"""
Tests for Chamunda Automobile Parts & Service Trinity Innovations:
1. 24/7 Customer WhatsApp Bot & Real-Time Job Card Tracker
2. Royal Enfield Iconic Thump Tuner & Acoustic Resonance Calibrator
3. Smart Barcode / Camera Parts Scanner & Instant Dynamic UPI QR Countertop POS
"""

import sys
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add paths
SYS_PATH_ENTERPRISE = "/home/alpesh/chamunda_re_enterprise"
SYS_PATH_JARVIS = "/home/alpesh/jarvis-agent"
if SYS_PATH_ENTERPRISE not in sys.path:
    sys.path.insert(0, SYS_PATH_ENTERPRISE)
if SYS_PATH_JARVIS not in sys.path:
    sys.path.insert(0, SYS_PATH_JARVIS)

from customer_bot_engine import ChamundaCustomerBot, SERVICE_STAGES
from thump_tuner_engine import ChamundaThumpTuner, THUMP_PRESETS
from counter_pos_engine import ChamundaCounterPOS
from tools.chamunda_ceo_tools import (
    chamunda_track_customer_service_status,
    chamunda_tune_engine_thump,
    chamunda_create_quick_counter_pos_sale
)
from core.offline_commander import OfflineCommander
from config.settings import JarvisConfig
from app import app


@pytest.fixture
def bot_engine():
    return ChamundaCustomerBot()


@pytest.fixture
def thump_engine():
    return ChamundaThumpTuner()


@pytest.fixture
def pos_engine():
    return ChamundaCounterPOS()


@pytest.fixture
def test_client():
    return TestClient(app)


# ---------------------------------------------------------------------
# 1. Test Customer WhatsApp Bot & Live Job Card Tracker
# ---------------------------------------------------------------------
def test_customer_bot_tracking(bot_engine):
    res = bot_engine.track_service_status("GJ-01-AB-1234")
    assert res["found"] is True
    assert res["job_card_id"] == "JOB-20260908-001"
    assert "Rajeshbhai" in res["customer_name"]
    assert res["progress_pct"] in [15, 35, 65, 85, 100]
    assert "message_gu" in res
    assert "message_en" in res
    assert "ચામુંડા ઓટોમોબાઇલ" in res["message_gu"]


def test_customer_bot_booking(bot_engine):
    res = bot_engine.book_service_slot(
        customer_name="Maheshbhai Vaghela",
        phone="9825199999",
        bike_model="Classic 350 Reborn",
        registration_no="GJ-01-EF-5678",
        preferred_date="Tomorrow 11:00 AM",
        customer_issues="Periodic Engine Service & Tappet Check"
    )
    assert res["success"] is True
    assert res["booking_id"].startswith("BK-RE-")
    assert "Priority Bay" in res["booking"]["bay_allocated"]
    assert "ચામુંડા ઓટોમોબાઇલ" in res["message_gu"]


def test_customer_bot_conversational_chat(bot_engine):
    # Tracking message
    chat1 = bot_engine.process_customer_message("મારી બાઇક ક્યાં પહોંચી? GJ-01-AB-1234")
    assert chat1["intent"] == "STATUS_TRACKING"
    assert "Rajeshbhai" in chat1["reply"]

    # Parts message
    chat2 = bot_engine.process_customer_message("Hunter 350 brake pad ભાવ શું છે?")
    assert chat2["intent"] == "PARTS_INQUIRY"
    assert "૪,૪૬૯+" in chat2["reply"]

    # General greeting
    chat3 = bot_engine.process_customer_message("હેલો કેમ છો?")
    assert chat3["intent"] == "GENERAL_GREETING"
    assert "ચામુંડા AI" in chat3["reply"]


# ---------------------------------------------------------------------
# 2. Test Royal Enfield Authentic Thump Tuner & Acoustic Calibrator
# ---------------------------------------------------------------------
def test_thump_tuner_synthetic_generation(thump_engine):
    audio = thump_engine.generate_synthetic_thump("Classic 350", "deep_vintage_chug", duration_sec=1.5)
    assert len(audio) > 0
    assert audio.dtype.name == "float32"


def test_thump_tuner_analysis(thump_engine):
    for preset in ["deep_vintage_chug", "factory_oem_clean", "cruiser_bass_rumble", "sherpa_highland_growl", "twin_270_crossplane_roar"]:
        res = thump_engine.analyze_exhaust_thump(bike_model="Classic 350", preset_key=preset)
        assert res["bike_model"] == "Classic 350"
        assert 0.0 <= res["thump_score"] <= 100.0
        assert res["dominant_bass_hz"] > 0
        assert res["estimated_db"] <= 85.0
        assert res["rto_legal_compliant"] is True
        assert len(res["mechanic_directives"]) >= 4
        assert "Cold Valve Lash Calibration" in res["mechanic_directives"][0]
        assert "સારાંશ" in res["summary_gu"]


# ---------------------------------------------------------------------
# 3. Test Smart Barcode Scanner & Dynamic UPI QR Countertop POS
# ---------------------------------------------------------------------
def test_pos_scan_lookup(pos_engine):
    part = pos_engine.scan_or_lookup_part("574050/C")
    assert part is not None
    assert "574050/C" in part.get("part_number", part.get("oem_number", ""))
    assert part.get("mrp", 0) > 0

    # Search dropdown
    results = pos_engine.search_counter_parts("oil filter", limit=5)
    assert len(results) > 0


def test_pos_dynamic_upi_link(pos_engine):
    upi_data = pos_engine.generate_upi_payment_link(amount=450.00, receipt_no="POS-TEST-001")
    assert "upi://pay?" in upi_data["upi_uri"]
    assert "pa=chamunda.re@okicici" in upi_data["upi_uri"]
    assert "am=450.00" in upi_data["upi_uri"]
    assert "data:image/png;base64," in upi_data["qr_code_base64"]


def test_pos_counter_sale_checkout(pos_engine):
    sale = pos_engine.create_counter_sale(
        cart_items=[{"part_id": "574050/C", "qty": 1}],
        customer_name="Sureshbhai Patel",
        phone="9825011111",
        discount_amount=10.0
    )
    assert sale["receipt_no"].startswith("POS-")
    assert sale["customer_name"] == "Sureshbhai Patel"
    assert sale["net_amount"] == sale["subtotal"] - 10.0
    assert "upi_uri" in sale
    assert "qr_code_base64" in sale
    assert Path(sale["receipt_file"]).exists()
    assert "CHAMUNDA AUTOMOBILE" in Path(sale["receipt_file"]).read_text(encoding="utf-8")


# ---------------------------------------------------------------------
# 4. Test CEO Tools
# ---------------------------------------------------------------------
def test_chamunda_ceo_tools():
    # 1. Live stage tracking
    track_str = chamunda_track_customer_service_status("GJ-01-AB-1234")
    assert "Live Service Stage Tracking" in track_str
    assert "Overall Progress" in track_str

    # 2. Thump tuning
    thump_str = chamunda_tune_engine_thump("Classic 350", "deep_vintage_chug")
    assert "Iconic Thump Tuner" in thump_str
    assert "Thump Score" in thump_str
    assert "Cold Valve Lash" in thump_str

    # 3. Counter POS sale
    pos_str = chamunda_create_quick_counter_pos_sale("574050/C", "Dineshbhai")
    assert "Instant Counter POS Sale Completed" in pos_str
    assert "Dynamic UPI Pay URI" in pos_str


# ---------------------------------------------------------------------
# 5. Test Offline Commander Natural Language Routing
# ---------------------------------------------------------------------
def test_offline_commander_trinity_routing():
    commander = OfflineCommander(config=JarvisConfig(language="gu"))

    # Thump command
    thump_res = commander.execute_offline_turn("Classic 350 નું થમ્પ ટ્યુનર બતાવો અને અવાજ ચેક કરો")
    assert "Thump" in thump_res or "ડુગ" in thump_res

    # Live service tracking command
    track_res = commander.execute_offline_turn("GJ-01-AB-1234 ગાડી ક્યાં પહોંચી? સર્વિસ સ્ટેટસ આપો")
    assert "સ્ટેટસ" in track_res or "Stage" in track_res

    # Counter POS command
    pos_res = commander.execute_offline_turn("કાઉન્ટર પર 574050/C પાર્ટ વેચો અને UPI QR બનાવો")
    assert "POS" in pos_res or "UPI" in pos_res


# ---------------------------------------------------------------------
# 6. Test FastAPI Web Portal Endpoints
# ---------------------------------------------------------------------
def test_fastapi_endpoints(test_client):
    # 1. Thump endpoint
    r = test_client.post("/api/thump/analyze", json={"bike_model": "Interceptor 650", "preset_key": "twin_270_crossplane_roar"})
    assert r.status_code == 200
    assert r.json()["dominant_bass_hz"] > 0

    # 2. Customer bot chat endpoint
    r = test_client.post("/api/bot/chat", json={"message": "સર્વિસ બુકિંગ કરવી છે Classic 350"})
    assert r.status_code == 200
    assert "reply" in r.json()

    # 3. Track endpoint
    r = test_client.get("/api/bot/track/GJ-01-AB-1234")
    assert r.status_code == 200
    assert r.json()["found"] is True

    # 4. Job stage update endpoint
    r = test_client.post("/api/jobcard/update-stage", json={"job_card_id": "JOB-20260908-001", "stage_name": "Ready for Delivery"})
    assert r.status_code == 200
    assert r.json()["success"] is True

    # 5. POS scan & checkout
    r = test_client.post("/api/pos/scan", json={"code_or_query": "574050/C"})
    assert r.status_code == 200
    assert r.json()["found"] is True

    r = test_client.post("/api/pos/checkout", json={
        "items": [{"part_id": "574050/C", "qty": 2}],
        "customer_name": "API Test Customer",
        "phone": "9825000000"
    })
    assert r.status_code == 200
    rec_no = r.json()["receipt_no"]

    # 6. View POS thermal receipt
    r = test_client.get(f"/pos/receipt/{rec_no}")
    assert r.status_code == 200
    assert "CHAMUNDA AUTOMOBILE" in r.text
