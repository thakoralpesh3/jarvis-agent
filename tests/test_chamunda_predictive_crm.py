"""
Unit & Integration Tests for Chamunda AI:
Predictive Service CRM & Automated WhatsApp Reminder Engine
(with One-Click Wholesale Stock Replenishment PO Generator).
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
from crm_engine import ChamundaCRMManager
from core.wholesale_po_engine import WholesalePOEngine, PO_DIR
from tools.chamunda_ceo_tools import (
    chamunda_get_predictive_service_reminders,
    chamunda_generate_wholesale_po
)
from core.offline_commander import OfflineCommander
from config.settings import JarvisConfig


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def crm_mgr():
    return ChamundaCRMManager()


@pytest.fixture
def po_engine():
    return WholesalePOEngine()


# ---------------------------------------------------------------------------
# 1. CRM ENGINE TESTS
# ---------------------------------------------------------------------------
def test_crm_predictive_reminders_structure(crm_mgr):
    """Verify predictive CRM returns correctly structured metrics and fleet categorization."""
    data = crm_mgr.get_predictive_service_reminders()
    assert isinstance(data, dict)
    assert "total_fleet_tracked" in data
    assert "due_now_count" in data
    assert "upcoming_count" in data
    assert "recent_count" in data
    assert data["total_fleet_tracked"] >= 3

    # Check due now customers
    if data["due_now_customers"]:
        c = data["due_now_customers"][0]
        assert "customer_name" in c
        assert "registration_no" in c
        assert "days_elapsed" in c
        assert c["days_elapsed"] >= 80 or (c["projected_odometer_km"] - c["base_odometer_km"] >= 2800)
        assert c["urgency"] == "DUE_NOW"
        assert "whatsapp_gujarati" in c
        assert "whatsapp_english" in c


def test_crm_whatsapp_reminder_bilingual(crm_mgr):
    """Verify high-conversion WhatsApp reminder copy in both Gujarati and English."""
    customer = {
        "customer_name": "Alpesh Sir",
        "bike_model": "Hunter 350 Dapper Ash",
        "registration_no": "GJ-01-RE-2026",
    }
    # Gujarati copy
    gu_msg = crm_mgr.generate_whatsapp_reminder(
        customer=customer,
        days_elapsed=88,
        projected_odo=11500,
        health_score=97.5,
        lang="gu"
    )
    assert "નમસ્તે શ્રી Alpesh Sir જી!" in gu_msg
    assert "Hunter 350" in gu_msg
    assert "GJ-01-RE-2026" in gu_msg
    assert "88 દિવસ" in gu_msg
    assert "97.5/100" in gu_msg
    assert "ચામુંડા ઓટોમોબાઇલ" in gu_msg

    # English copy
    en_msg = crm_mgr.generate_whatsapp_reminder(
        customer=customer,
        days_elapsed=88,
        projected_odo=11500,
        health_score=97.5,
        lang="en"
    )
    assert "Namaste Alpesh Sir ji!" in en_msg
    assert "Hunter 350" in en_msg
    assert "88 days" in en_msg
    assert "97.5/100" in en_msg
    assert "Chamunda Automobile" in en_msg


def test_crm_mark_reminder_sent(crm_mgr):
    """Verify recording customer WhatsApp reminder dispatches."""
    reg = "GJ-01-TEST-9999"
    res = crm_mgr.mark_reminder_sent(reg)
    assert res["success"] is True
    assert res["registration_no"] == reg
    assert "sent_at" in res


# ---------------------------------------------------------------------------
# 2. WHOLESALE PURCHASE ORDER ENGINE TESTS
# ---------------------------------------------------------------------------
def test_wholesale_po_generation(po_engine):
    """Verify automated purchase order generation for low stock spares."""
    po = po_engine.generate_low_stock_purchase_order(supplier_name="Royal Enfield Authentic Distribution")
    assert "po_number" in po
    assert po["po_number"].startswith("PO-CAPS-")
    assert po["total_outlay_inr"] > 0
    assert len(po["items"]) > 0
    assert Path(po["po_file"]).exists()
    
    html_content = Path(po["po_file"]).read_text(encoding="utf-8")
    assert "CHAMUNDA AUTOMOBILE PARTS & SERVICE" in html_content
    assert po["po_number"] in html_content
    assert "Royal Enfield Authentic Distribution" in html_content


# ---------------------------------------------------------------------------
# 3. WEB PORTAL & REST ENDPOINTS TESTS
# ---------------------------------------------------------------------------
def test_portal_tab_6_rendered(client):
    """Verify Tab 6 'Smart Reminders & CRM' renders with counters, tables, and modal triggers."""
    res = client.get("/")
    assert res.status_code == 200
    html = res.text
    assert "Smart Reminders & CRM" in html
    assert "crm-reminders" in html
    assert "Due Now (Urgent)" in html
    assert "Upcoming Due" in html
    assert "1-Click Wholesale Stock PO" in html
    assert "whatsappModal" in html
    assert "poModal" in html


def test_api_crm_reminders_endpoint(client):
    """Verify REST API /api/crm/reminders returns live CRM metrics."""
    res = client.get("/api/crm/reminders")
    assert res.status_code == 200
    data = res.json()
    assert "total_fleet_tracked" in data
    assert "due_now_customers" in data


def test_api_crm_mark_sent_endpoint(client):
    """Verify REST API /api/crm/mark-sent successfully records dispatch."""
    payload = {"registration_no": "GJ-01-RE-3500"}
    res = client.post("/api/crm/mark-sent", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["registration_no"] == "GJ-01-RE-3500"


def test_api_po_generate_and_view_endpoint(client):
    """Verify REST API /api/po/generate creates PO and /po/{po_number} serves the HTML."""
    payload = {"supplier_name": "Royal Enfield Genuine OEM Hub"}
    res = client.post("/api/po/generate", json=payload)
    assert res.status_code == 200
    po_data = res.json()
    po_no = po_data["po_number"]
    assert po_no.startswith("PO-CAPS-")

    # View PO HTML endpoint
    res_view = client.get(f"/po/{po_no}")
    assert res_view.status_code == 200
    assert po_no in res_view.text


# ---------------------------------------------------------------------------
# 4. CEO EXECUTIVE TOOLS TESTS
# ---------------------------------------------------------------------------
def test_ceo_tool_predictive_service_reminders():
    """Verify chamunda_get_predictive_service_reminders tool formatting."""
    rep = chamunda_get_predictive_service_reminders()
    assert "Chamunda AI • Predictive Service CRM & Reminder Intelligence" in rep
    assert "Fleet Monitored:" in rep
    assert "URGENT: Service Due Now" in rep


def test_ceo_tool_generate_wholesale_po():
    """Verify chamunda_generate_wholesale_po tool formatting."""
    rep = chamunda_generate_wholesale_po("Royal Enfield OEM Distributor")
    assert "Official Wholesale Purchase Order Generated" in rep
    assert "PO Number:" in rep
    assert "Total Reorder SKUs:" in rep
    assert "Total Wholesale Outlay:" in rep


# ---------------------------------------------------------------------------
# 5. OFFLINE COMMANDER INTENT ROUTING TESTS
# ---------------------------------------------------------------------------
def test_offline_commander_crm_and_po_english():
    """Verify OfflineCommander natural language routing in English."""
    commander = OfflineCommander(config=JarvisConfig(language="en"))
    
    # CRM Reminder routing
    res_crm = commander.execute_offline_turn("show me the service reminder list")
    assert "Predictive Service CRM" in res_crm
    assert "Fleet Monitored" in res_crm

    # Wholesale PO routing
    res_po = commander.execute_offline_turn("generate wholesale purchase order for low stock")
    assert "Purchase Order" in res_po
    assert "Total Reorder SKUs" in res_po


def test_offline_commander_crm_and_po_gujarati():
    """Verify OfflineCommander natural language routing in Gujarati."""
    commander = OfflineCommander(config=JarvisConfig(language="gu"))
    
    # CRM Reminder routing (Gujarati)
    res_crm = commander.execute_offline_turn("ગ્રાહકો માટે સર્વિસ રિમાઇન્ડર લિસ્ટ બતાવો")
    assert "ચામુંડા ઓટોમોબાઇલ પ્રેડિક્ટિવ સર્વિસ CRM" in res_crm
    assert "સફળતાપૂર્વક પૂર્ણ" in res_crm

    # Wholesale PO routing (Gujarati)
    res_po = commander.execute_offline_turn("સ્પેરપાર્ટ્સ સ્ટોક માટે પીઓ બનાવો")
    assert "Purchase Order (PO)" in res_po
    assert "સફળતાપૂર્વક પૂર્ણ" in res_po
