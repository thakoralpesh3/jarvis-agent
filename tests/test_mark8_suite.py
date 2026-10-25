"""
Unit Tests for Mark VIII Next-Generation Capabilities.
"""

import pytest
from core.ecu_obd_bridge import REECUDiagnosticBridge
from ui.engine_torque_visualizer import EngineTorqueVisualizer
from core.predictive_health import REPredictiveHealthEngine
from core.whatsapp_receptionist import WhatsAppServiceReceptionist
from core.market_intelligence import REMarketIntelligenceEngine
from core.self_optimizer import SelfOptimizerEngine
from core.workshop_iot import WorkshopIoTController
from tools.mark8_tools import (
    read_re_ecu_telemetry,
    scan_re_ecu_dtc_codes,
    clear_re_ecu_dtc_codes,
    get_re_factory_torque_specs,
    predict_re_bike_health_score,
    book_whatsapp_service_appointment,
    get_daily_re_market_intelligence,
    run_jarvis_self_optimization,
    control_workshop_iot_device
)


def test_ecu_telemetry_and_dtc():
    bridge = REECUDiagnosticBridge()
    telem = bridge.read_live_telemetry("Classic 350")
    assert "report" in telem
    assert "Target Platform" in telem["report"] or "Port" in telem["report"]

    dtc = bridge.scan_dtc_fault_codes("P0505")
    assert dtc["found"] is True
    assert "P0505" in dtc["dtc_code"]

    clear_msg = bridge.clear_dtc_codes()
    assert len(clear_msg) > 5


def test_engine_torque_visualizer():
    viz = EngineTorqueVisualizer()
    res = viz.get_torque_spec_sheet("J-Series 350")
    assert len(res["specs"]) > 4
    assert "40 Nm" in res["report"]


def test_predictive_health_engine():
    health = REPredictiveHealthEngine()
    res = health.evaluate_bike_health("Hunter 350", current_odometer_km=18000, km_since_last_service=2900)
    assert 20 <= res["health_score"] <= 100
    assert res["oil_wear_pct"] > 80


def test_whatsapp_service_receptionist():
    recep = WhatsAppServiceReceptionist()
    res = recep.handle_incoming_inquiry(
        customer_name="Test Rider",
        phone="+91 97000 00000",
        bike_model="Continental GT 650",
        requested_slot="Saturday 11:00 AM",
        customer_message="Clutch slip at high RPM and oil change"
    )
    assert "BOOK-CAPS-" in res["booking_id"]
    assert "CONFIRMED" in res["whatsapp_reply"]


def test_market_intelligence_engine():
    intel = REMarketIntelligenceEngine()
    res = intel.generate_daily_intelligence_digest()
    assert "ROYAL ENFIELD" in res["report"] or "Technical" in res["report"]


def test_self_optimizer_and_iot():
    tune = SelfOptimizerEngine()
    t_res = tune.run_self_benchmark_and_tuning()
    assert t_res["dispatch_latency_ms"] >= 0

    iot = WorkshopIoTController()
    st = iot.get_hardware_status()
    assert "Air Compressor" in st["report"]
    toggle_msg = iot.toggle_device("air compressor", "ON")
    assert "ON" in toggle_msg
