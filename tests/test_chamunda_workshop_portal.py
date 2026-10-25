"""
Unit & Integration Tests for Chamunda AI:
Interactive Workshop Web Portal & Live Mobile QR Viewer.
"""

import sys
import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure paths
SYS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SYS_DIR))
sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")

from app import app
from tools.chamunda_ceo_tools import chamunda_launch_workshop_portal
from core.offline_commander import OfflineCommander


@pytest.fixture
def client():
    return TestClient(app)


def test_portal_main_page_rendering(client):
    """Verify main dashboard renders with luxury dark/gold theme and all 5 tabs."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    assert "CHAMUNDA AUTOMOBILE" in html
    assert "Executive Overview" in html
    assert "Live Sound Diagnostic Bay" in html
    assert "4,469 Parts Dynamic Filter" in html
    assert "Service Bays & QR Invoicing" in html
    assert "New Bike Intake" in html
    assert "waveformCanvas" in html


def test_api_parts_filter(client):
    """Verify dynamic multi-parameter catalog search endpoint."""
    res = client.get("/api/parts/filter?query=brake+pad&model=Hunter+350&limit=10")
    assert res.status_code == 200
    parts = res.json()
    assert isinstance(parts, list)
    assert len(parts) > 0
    first = parts[0]
    assert "part_number" in first or "oem_number" in first
    assert "mrp" in first


def test_api_sound_diagnose(client):
    """Verify REST endpoint for live/simulated FFT sound diagnostics."""
    payload = {
        "bike_model": "Hunter 350",
        "simulate_fault": "tappet"
    }
    res = client.post("/api/sound-diagnose", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "diagnostic_id" in data
    assert data["health_score"] < 70.0
    assert len(data["anomalies_detected"]) > 0
    assert data["anomalies_detected"][0]["fault_key"] == "tappet_valve_noise"
    assert len(data["parts_recommendations"]) > 0


def test_api_jobcard_and_billing_lifecycle(client):
    """Verify full REST job card creation, parts allocation, and one-click QR invoicing."""
    # 1. Create Job Card
    create_payload = {
        "customer_name": "Haresh Dave",
        "phone": "+919876500000",
        "bike_model": "Classic 350",
        "registration_no": "GJ-01-HD-9999",
        "odometer_km": 11000,
        "customer_issues": "Periodic master service and valve clearance audit"
    }
    r_create = client.post("/api/jobcard", json=create_payload)
    assert r_create.status_code == 200
    job = r_create.json()
    job_id = job["job_card_id"]
    assert job_id.startswith("JOB-")

    # 2. Add Part to Job
    part_payload = {
        "job_card_id": job_id,
        "part_name": "Motul 7100 15W-50 4T Fully Synthetic (2.5L)",
        "qty": 1,
        "price": 2450.0
    }
    r_part = client.post("/api/jobcard/add-part", json=part_payload)
    assert r_part.status_code == 200
    assert r_part.json()["success"] is True

    # 3. Complete and Generate QR Invoice & Passport
    complete_payload = {
        "job_card_id": job_id,
        "technician": "Master Tech Alpesh (Chamunda Automobile)"
    }
    r_comp = client.post("/api/jobcard/complete-and-bill", json=complete_payload)
    assert r_comp.status_code == 200
    bill_data = r_comp.json()
    assert bill_data["status"] == "Completed"
    assert bill_data["invoice_no"].startswith("CAPS-")
    assert bill_data["passport_id"].startswith("CHAMUNDA-HP-")
    assert bill_data["grand_total"] > 2500
    assert "data:image/png;base64," in bill_data["qr_code_base64"]

    # 4. View Customer Passport
    r_pass = client.get(f"/passport/{bill_data['passport_id']}")
    assert r_pass.status_code == 200
    assert "CHAMUNDA AI" in r_pass.text
    assert bill_data["passport_id"] in r_pass.text

    # 5. View Tax Invoice
    r_inv = client.get(f"/invoice/{bill_data['invoice_no']}")
    assert r_inv.status_code == 200
    assert "TAX INVOICE" in r_inv.text
    assert bill_data["invoice_no"] in r_inv.text


def test_ceo_tool_launch_workshop_portal():
    """Verify CEO tool chamunda_launch_workshop_portal returns active status and URLs."""
    report = chamunda_launch_workshop_portal()
    assert "Chamunda AI • Interactive Workshop Web Portal" in report
    assert "Active & Online" in report
    assert "http://127.0.0.1:8080" in report
    assert "Live Engine Sound Diagnostic Bay" in report


def test_offline_commander_portal_route():
    """Verify natural language routing for workshop portal in Gujarati & English."""
    from config.settings import JarvisConfig

    oc_gu = OfflineCommander()
    resp_gu = oc_gu.execute_offline_turn("ચામુંડા વર્કશોપ વેબ પોર્ટલ ચાલુ કરો")
    assert "ઇન્ટરેક્ટિવ વર્કશોપ વેબ પોર્ટલ લાઈવ છે" in resp_gu
    assert "http://127.0.0.1:8080" in resp_gu

    oc_en = OfflineCommander(config=JarvisConfig(language="en"))
    resp_en = oc_en.execute_offline_turn("open workshop dashboard portal")
    assert "Interactive Workshop Web Portal is active and online" in resp_en
    assert "http://127.0.0.1:8080" in resp_en
