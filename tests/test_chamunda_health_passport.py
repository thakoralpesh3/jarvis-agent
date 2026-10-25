"""
Test Suite for Chamunda Automobile Digital Acoustic Health Passport.
Verifies acoustic telemetry analysis, HTML certificate generation,
CEO tools integration, and Gujarati/English offline commander support.
"""

import os
import json
import pytest
from pathlib import Path

import sys
sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
from acoustic_health_passport import (
    ChamundaHealthPassportGenerator,
    get_platform_specs,
    FACTORY_SPECS,
    PASSPORTS_DIR,
)

from tools.chamunda_ceo_tools import chamunda_generate_health_passport
from core.offline_commander import OfflineCommander


@pytest.fixture
def generator(tmp_path):
    return ChamundaHealthPassportGenerator(
        data_dir=tmp_path / "data",
        passports_dir=tmp_path / "passports"
    )


def test_platform_specs_detection():
    """Verify factory tolerance specifications across all Royal Enfield platforms."""
    hunter_spec = get_platform_specs("Hunter 350")
    assert "J-Series" in hunter_spec["platform"]
    assert "0.08 mm" in hunter_spec["inlet_clearance"]
    assert "0.18 mm" in hunter_spec["exhaust_clearance"]

    gt650_spec = get_platform_specs("Continental GT 650")
    assert "Parallel Twin" in gt650_spec["platform"]
    assert "0.10 mm" in gt650_spec["inlet_clearance"]

    himalayan450_spec = get_platform_specs("Himalayan 450")
    assert "Sherpa" in himalayan450_spec["platform"]
    assert "11.5 : 1" in himalayan450_spec["compression_ratio"]


def test_acoustic_telemetry_analysis(generator):
    """Verify multi-harmonic acoustic analysis across all 5 engine dimensions."""
    res = generator.analyze_acoustic_telemetry(bike_model="Classic 350 Reborn", odometer_km=12000)
    assert 90.0 <= res["overall_score"] <= 100.0
    assert res["status_text"] in ["PASSED - SHOWROOM SPECIFICATION", "PASSED - EXCELLENT TUNE"]

    breakdown = res["acoustic_breakdown"]
    assert "tappet_valve_clearance" in breakdown
    assert "timing_chain_resonance" in breakdown
    assert "cylinder_compression_beat" in breakdown
    assert "exhaust_backpressure" in breakdown
    assert "primary_drive" in breakdown


def test_health_passport_generation(generator):
    """Verify HTML certificate generation, JSON record persistence, and WhatsApp copies."""
    rec = generator.generate_health_passport(
        customer_name="Sanjay Raval",
        phone="+91 98980 11223",
        bike_model="Meteor 350 Supernova",
        registration_no="GJ-01-RE-9999",
        odometer_km=14500,
        service_notes="Periodic Service + Tappet Calibration"
    )

    assert rec["passport_id"].startswith("CHAMUNDA-HP-2026-")
    assert rec["overall_score"] >= 90.0
    assert Path(rec["html_path"]).exists()

    html_content = Path(rec["html_path"]).read_text(encoding="utf-8")
    assert "Chamunda Automobile" in html_content
    assert "DIGITAL ACOUSTIC HEALTH PASSPORT" in html_content
    assert "Sanjay Raval" in html_content
    assert "GJ-01-RE-9999" in html_content

    # WhatsApp copies
    assert "ચામુંડા ઓટોમોબાઇલ" in rec["whatsapp_gujarati"]
    assert "CHAMUNDA AUTOMOBILE" in rec["whatsapp_english"]


def test_chamunda_generate_health_passport_tool():
    """Verify CEO tool chamunda_generate_health_passport produces executive report."""
    output = chamunda_generate_health_passport(
        customer_name="Kishore Vala",
        phone="+91 98250 44556",
        bike_model="Interceptor 650 Canyon Red",
        registration_no="GJ-03-RE-6500",
        odometer_km=9200
    )

    assert "Chamunda Automobile • Digital Acoustic Health Passport" in output
    assert "Interceptor 650 Canyon Red" in output
    assert "GJ-03-RE-6500" in output
    assert "Overall Engine Health Score" in output
    assert "CHAMUNDA-HP-2026-" in output


def test_offline_commander_health_passport_routing():
    """Verify OfflineCommander routes health passport queries with closure protocol."""
    commander = OfflineCommander()

    # Gujarati command
    resp_gu = commander.execute_offline_turn("ચામુંડા એકોસ્ટિક હેલ્થ પાસપોર્ટ બનાવો Hunter 350 GJ-01-RE-8888 5000 km")
    assert "ચામુંડા ઓટોમોબાઇલ ડિજિટલ એકોસ્ટિક હેલ્થ પાસપોર્ટ" in resp_gu
    assert "કામ સફળતાપૂર્વક પૂર્ણ થઈ ગયું છે" in resp_gu
    assert "બીજું કોઈ કામ છે" in resp_gu
    assert "નવો આઈડિયા/સજેશન" in resp_gu

    # English command
    commander.config.language = "english"
    resp_en = commander.execute_offline_turn("generate health passport for Classic 350 GJ-01-RE-1234 10000 km")
    assert "Chamunda Automobile Digital Acoustic Health Passport generated successfully" in resp_en
    assert "Work completed successfully" in resp_en
    assert "Is there any other work for me" in resp_en
