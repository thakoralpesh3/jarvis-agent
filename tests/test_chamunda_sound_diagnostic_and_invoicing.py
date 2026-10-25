"""
Unit & Integration Tests for Chamunda AI:
Live Engine Sound Diagnostics & Service Invoicing with QR-Embedded Health Passports.
"""

import os
import sys
import json
import pytest
from pathlib import Path

# Ensure paths are set
SYS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SYS_DIR))
sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")

from acoustic_sound_diagnostic import ChamundaSoundDiagnosticEngine, FAULT_PROFILES
from acoustic_health_passport import ChamundaHealthPassportGenerator, generate_qr_base64
from billing_engine import ChamundaBillingManager, generate_invoice_qr
from service_engine import ChamundaServiceManager
from tools.chamunda_ceo_tools import (
    chamunda_diagnose_engine_sound,
    chamunda_complete_job_and_invoice,
)
from core.offline_commander import OfflineCommander


@pytest.fixture
def temp_dirs(tmp_path):
    recordings_dir = tmp_path / "recordings"
    passports_dir = tmp_path / "passports"
    invoices_dir = tmp_path / "invoices"
    recordings_dir.mkdir()
    passports_dir.mkdir()
    invoices_dir.mkdir()
    return {
        "recordings": recordings_dir,
        "passports": passports_dir,
        "invoices": invoices_dir,
        "tmp": tmp_path
    }


def test_synthetic_wave_generation(temp_dirs):
    """Verify high-fidelity Royal Enfield idle wave generation."""
    eng = ChamundaSoundDiagnosticEngine(data_dir=temp_dirs["tmp"])
    wave_path = str(temp_dirs["recordings"] / "test_idle.wav")
    out = eng.generate_synthetic_wave(wave_path, duration_sec=2.0)
    
    assert os.path.exists(out)
    assert os.path.getsize(out) > 5000  # Non-empty PCM audio


def test_fft_spectral_analysis(temp_dirs):
    """Verify Fast Fourier Transform decomposition on engine sound."""
    eng = ChamundaSoundDiagnosticEngine(data_dir=temp_dirs["tmp"])
    wave_path = str(temp_dirs["recordings"] / "test_fft.wav")
    eng.generate_synthetic_wave(wave_path, duration_sec=2.0)
    
    spectrum = eng.analyze_audio_spectrum(wave_path)
    assert spectrum["duration_sec"] == 2.0
    assert spectrum["dominant_freq_hz"] > 0
    assert spectrum["estimated_db"] > 60.0
    assert "tappet_valve_noise" in spectrum["bands_power"]
    assert "timing_chain_slack" in spectrum["bands_power"]


def test_anomaly_detection_healthy(temp_dirs):
    """Verify healthy engine sound produces 0 anomalies and high health score."""
    eng = ChamundaSoundDiagnosticEngine(data_dir=temp_dirs["tmp"])
    rep = eng.diagnose_engine_sound(bike_model="Classic 350", inject_simulation="healthy")
    
    assert rep["health_score"] >= 95.0
    assert "HEALTHY" in rep["health_status"]
    assert len(rep["anomalies_detected"]) == 0


def test_anomaly_detection_tappet(temp_dirs):
    """Verify injected tappet noise is detected with high confidence."""
    eng = ChamundaSoundDiagnosticEngine(data_dir=temp_dirs["tmp"])
    rep = eng.diagnose_engine_sound(bike_model="Hunter 350", inject_simulation="tappet_valve_noise")
    
    assert rep["health_score"] < 70.0
    assert len(rep["anomalies_detected"]) >= 1
    top_fault = rep["anomalies_detected"][0]
    assert top_fault["fault_key"] == "tappet_valve_noise"
    assert top_fault["confidence_pct"] >= 80.0


def test_anomaly_detection_timing_chain(temp_dirs):
    """Verify injected timing chain rattle is detected with high confidence."""
    eng = ChamundaSoundDiagnosticEngine(data_dir=temp_dirs["tmp"])
    rep = eng.diagnose_engine_sound(bike_model="Meteor 350", inject_simulation="timing_chain_slack")
    
    assert len(rep["anomalies_detected"]) >= 1
    fault_keys = [a["fault_key"] for a in rep["anomalies_detected"]]
    assert "timing_chain_slack" in fault_keys


def test_anomaly_detection_clutch_whine(temp_dirs):
    """Verify injected clutch whine is detected with high confidence."""
    eng = ChamundaSoundDiagnosticEngine(data_dir=temp_dirs["tmp"])
    rep = eng.diagnose_engine_sound(bike_model="Interceptor 650", inject_simulation="clutch_primary_whine")
    
    assert len(rep["anomalies_detected"]) >= 1
    fault_keys = [a["fault_key"] for a in rep["anomalies_detected"]]
    assert "clutch_primary_whine" in fault_keys


def test_oem_parts_recommendation_from_4469_catalog(temp_dirs):
    """Verify diagnosed faults map to real OEM spare parts from Chamunda catalog."""
    eng = ChamundaSoundDiagnosticEngine(data_dir=temp_dirs["tmp"])
    rep = eng.diagnose_engine_sound(bike_model="Hunter 350", inject_simulation="tappet_valve_noise")
    
    assert len(rep["parts_recommendations"]) >= 1
    parts = rep["parts_recommendations"][0]["matched_oem_parts"]
    assert len(parts) > 0
    # Check parts structure
    p = parts[0]
    assert "part_number" in p and p["part_number"]
    assert "mrp" in p and p["mrp"] > 0
    assert "bin_location" in p


def test_health_passport_qr_code_generation():
    """Verify QR code generator generates Base64 data URL and embeds into HTML."""
    qr_b64 = generate_qr_base64("https://chamunda-re.internal/verify/TEST-1234")
    assert qr_b64.startswith("data:image/png;base64,")
    assert len(qr_b64) > 500

    gen = ChamundaHealthPassportGenerator()
    rec = gen.generate_health_passport(
        customer_name="Suresh Kumar",
        phone="+919898989898",
        bike_model="Classic 350",
        registration_no="GJ-01-SK-3500",
        odometer_km=5000
    )
    assert "qr_code_base64" in rec
    assert rec["qr_code_base64"].startswith("data:image/png;base64,")
    
    # Check HTML file contains QR code
    html_text = Path(rec["html_path"]).read_text(encoding="utf-8")
    assert "data:image/png;base64," in html_text
    assert "SCAN TO VERIFY" in html_text


def test_billing_engine_with_passport_and_qr():
    """Verify billing manager embeds QR code and links health passport."""
    bm = ChamundaBillingManager()
    passport_data = {
        "passport_id": "CHAMUNDA-HP-2026-9999-ABCDEF",
        "overall_score": 98.2,
        "grade": "GOLD MINT (Showroom Specification)",
        "html_path": "/fake/path/passport.html"
    }
    inv = bm.generate_invoice_html(
        job_card_id="JOB-20260908-999",
        customer_name="Ketan Shah",
        phone="+919825012345",
        bike_model="Hunter 350",
        registration_no="GJ-01-KS-9999",
        odometer_km=6000,
        parts=[{"name": "Motul Engine Oil", "price": 2450.0, "qty": 1}],
        labor_charges=500.0,
        passport_data=passport_data
    )
    
    assert inv["invoice_no"].startswith("CAPS-")
    assert inv["grand_total"] > 2950.0
    assert inv["passport_id"] == "CHAMUNDA-HP-2026-9999-ABCDEF"
    assert inv["qr_code_base64"].startswith("data:image/png;base64,")
    assert "CHAMUNDA-HP-2026-9999-ABCDEF" in inv["whatsapp_message"]
    assert "CHAMUNDA-HP-2026-9999-ABCDEF" in inv["whatsapp_message_gujarati"]
    
    # Check invoice HTML content
    inv_html = Path(inv["invoice_file"]).read_text(encoding="utf-8")
    assert "VERIFIED ACOUSTIC ENGINE HEALTH PASSPORT ATTACHED" in inv_html
    assert "data:image/png;base64," in inv_html


def test_service_engine_complete_job_and_generate_invoice():
    """Verify complete_job_and_generate_invoice executes end-to-end lifecycle."""
    sm = ChamundaServiceManager()
    job = sm.create_job_card(
        customer_name="Maheshbhai",
        phone="+919999988888",
        bike_model="Bullet 350",
        registration_no="GJ-05-RE-1111",
        odometer_km=12000,
        customer_issues="Full service"
    )
    sm.add_parts_to_job(job["job_card_id"], "Genuine Spark Plug", 1, 180.0)

    res = sm.complete_job_and_generate_invoice(job["job_card_id"])
    assert res["status"] == "Completed"
    assert res["invoice_no"].startswith("CAPS-")
    assert res["passport_id"].startswith("CHAMUNDA-HP-")
    assert os.path.exists(res["invoice_file"])
    assert os.path.exists(res["passport_file"])
    assert res["health_score"] >= 90.0
    assert len(res["qr_code_base64"]) > 500


def test_ceo_tool_diagnose_engine_sound():
    """Verify CEO tool chamunda_diagnose_engine_sound produces markdown report."""
    output = chamunda_diagnose_engine_sound(
        bike_model="Hunter 350",
        simulate_fault="tappet"
    )
    assert "Chamunda Automobile • Engine Sound Diagnostic Report" in output
    assert "Excessive Tappet / Valve Clearance Clatter" in output
    assert "Recommended Genuine OEM Spare Parts" in output


def test_ceo_tool_complete_job_and_invoice():
    """Verify CEO tool chamunda_complete_job_and_invoice produces executive report."""
    sm = ChamundaServiceManager()
    job = sm.create_job_card(
        customer_name="Pankaj Dave",
        phone="+919879879870",
        bike_model="Himalayan 450",
        registration_no="GJ-01-HM-4500",
        odometer_km=4200,
        customer_issues="Periodic service"
    )
    output = chamunda_complete_job_and_invoice(job_card_id=job["job_card_id"])
    assert "Service Completed & GST Invoice Issued" in output
    assert "Tax Invoice (HTML with QR Code)" in output
    assert "Digital Health Passport Certificate" in output
    assert "WhatsApp Dispatch (Gujarati)" in output


def test_offline_commander_sound_and_invoice_routing():
    """Verify natural language routing for sound diagnostics and invoices in Gujarati & English."""
    oc = OfflineCommander()
    
    # Sound Diagnostic Route (Gujarati)
    resp_sound_gu = oc.execute_offline_turn("Hunter 350 એન્જિન સાઉન્ડ ટેસ્ટ કરો tappet ખામી")
    assert "એન્જિન સાઉન્ડ ડાયગ્નોસિસ સફળતાપૂર્વક પૂર્ણ થયું છે" in resp_sound_gu
    assert "Excessive Tappet" in resp_sound_gu

    # Invoice Completion Route (Gujarati)
    resp_inv_gu = oc.execute_offline_turn("સર્વિસ પૂર્ણ થઈ ગઈ છે, બિલ અને ઇન્વોઇસ બનાવો")
    assert "સર્વિસ જોબ કાર્ડ" in resp_inv_gu
    assert "GST ઇન્વોઇસ" in resp_inv_gu
