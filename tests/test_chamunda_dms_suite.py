"""
Unit and Integration Test Suite for Royal Enfield Dealer Management System (RE-DMS Suite).
Covers Split GST Invoicing, FSC Warranty Claims, Double-Entry Daybook, Marketing CRM,
Showroom Vehicle Bookings, 30-Point Digital PDI Certificates, Ride Sure Extended Warranty,
Accidental Insurance Surveyor Estimates, Post-Service PSF & CSAT Auditing,
Autonomous 10-Officer Dealership Fleet, AgentCommander Directives,
Chamunda CEO Executive Tools, and FastAPI Endpoints.

Helpline Compliance: Strictly +91 78747 19139.
"""

import sys
import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
sys.path.insert(0, "/home/alpesh/jarvis-agent")

from dms_enterprise_suite_engine import (
    get_dms_suite_engine,
    ChamundaDMSEnterpriseSuite,
    OFFICIAL_WHATSAPP_HELPLINE,
    WORKSHOP_GSTIN
)
from shop_subagents_engine import get_shop_subagents_manager
from core.agent_commander import AgentCommander
from tools.chamunda_ceo_tools import (
    chamunda_get_dms_executive_telemetry,
    chamunda_create_dms_billing_invoice,
    chamunda_file_oem_warranty_claim,
    chamunda_launch_marketing_campaign,
    chamunda_get_dms_financial_daybook,
    chamunda_create_vehicle_booking,
    chamunda_generate_pdi_certificate,
    chamunda_issue_ride_sure_warranty,
    chamunda_record_psf_csat_feedback,
    chamunda_get_dms_csat_qc_telemetry
)
from app import app


@pytest.fixture
def client():
    return TestClient(app)


# =============================================================================
# 1. CORE DMS SUITE ENGINE TESTS
# =============================================================================

def test_dms_overview_telemetry():
    dms = get_dms_suite_engine()
    tel = dms.get_dms_overview_telemetry()

    assert tel["dealership_code"] == "RE-GJ02-CHAMUNDA-HQ"
    assert "Chamunda Automobile" in tel["dealership_name"]
    assert tel["gstin"] == WORKSHOP_GSTIN
    assert tel["helpline"] == OFFICIAL_WHATSAPP_HELPLINE
    assert tel["whatsapp_helpline"] == OFFICIAL_WHATSAPP_HELPLINE
    assert tel["total_invoices_generated"] >= 1
    assert tel["total_warranty_claims"] >= 1
    assert tel["active_campaigns_count"] >= 1
    assert tel["active_leads_count"] >= 1
    assert "accounting_summary" in tel
    assert "showroom_summary" in tel
    assert "csat_summary" in tel


def test_dms_split_gst_invoice_creation():
    dms = get_dms_suite_engine()
    parts = [
        {"part_no": "RL-ENG-OIL-15W50", "name": "Motul 7100 15W50", "hsn": "2710", "qty": 2, "rate": 875.0, "amount": 1750.0},
        {"part_no": "574050/C", "name": "OEM RE Oil Filter Element", "hsn": "8714", "qty": 1, "rate": 185.0, "amount": 185.0}
    ]
    labor = [
        {"sac": "998729", "description": "Periodic Paid Service & 50-Point Inspection", "amount": 650.0},
        {"sac": "998729", "description": "Brake System Servicing", "amount": 250.0}
    ]
    res = dms.create_split_gst_invoice(
        customer_name="Maheshbhai Prajapati",
        phone="+91 98250 55667",
        bike_model="Classic 350 (Reborn)",
        registration_no="GJ-02-EE-9988",
        parts_items=parts,
        labor_items=labor,
        discount_amount=100.0,
        payment_mode="UPI (Instant)"
    )

    assert res["success"] is True
    inv = res["invoice"]
    assert inv["customer_name"] == "Maheshbhai Prajapati"
    assert inv["registration_no"] == "GJ-02-EE-9988"
    assert inv["parts_subtotal"] == 1935.0
    assert inv["labor_subtotal"] == 900.0
    assert inv["taxable_amount"] == 2735.0
    assert inv["cgst_amount"] == 246.15
    assert inv["sgst_amount"] == 246.15
    assert inv["grand_total"] == 3227.30
    assert inv["gate_pass_code"].startswith("GP-")
    assert inv["qr_code_uri"].startswith("data:image/png;base64,")
    assert "Devang Dave" in inv["biller"]


def test_dms_oem_warranty_claim_filing():
    dms = get_dms_suite_engine()
    res = dms.file_oem_warranty_claim(
        coupon_type="2nd Free Service Coupon (5,000 km)",
        chassis_no="ME3J350NR77665",
        engine_no="J350-2025-1122",
        bike_model="Meteor 350 Fireball",
        customer_name="Sunil Vaghela",
        phone="+91 97230 88990",
        kilometers=4950,
        defective_components="Periodic Coupon Redemption - Oil, Filter & Spark Plug Inspection",
        claim_amount=1650.0
    )

    assert res["success"] is True
    claim = res["claim"]
    assert claim["claim_id"].startswith("WAR-RE-2026-")
    assert claim["coupon_type"] == "2nd Free Service Coupon (5,000 km)"
    assert claim["re_approval_status"] == "APPROVED"
    assert claim["re_credit_note_no"].startswith("CN-RE-INDIA-")
    assert claim["claim_amount"] == 1650.0
    assert "Devang Dave" in claim["filed_by"]


def test_dms_accounting_daybook():
    dms = get_dms_suite_engine()
    daybook = dms.get_dms_accounting_daybook()

    assert daybook["dealership_code"] == "RE-GJ02-CHAMUNDA-HQ"
    assert daybook["gstin"] == WORKSHOP_GSTIN
    assert daybook["total_credits"] > 0
    assert daybook["total_debits"] > 0
    assert len(daybook["accounts_receivable"]) >= 3
    assert daybook["total_ar_outstanding"] > 0
    assert len(daybook["accounts_payable"]) >= 3
    assert daybook["total_ap_due"] > 0
    assert "pnl_summary" in daybook
    assert "gstr1_summary" in daybook
    assert daybook["gstr1_summary"]["total_gst_liability"] > 0


def test_dms_marketing_and_predictive_reminders():
    dms = get_dms_suite_engine()
    c_res = dms.create_marketing_campaign(
        name="Royal Enfield Heritage Desert Ride Camp",
        target_audience="Himalayan 450 & Scram 411 Owners",
        offer_title="Free Terrain Prep Inspection",
        offer_details="Complimentary spokes tension check & 10% off touring accessories"
    )
    assert c_res["success"] is True
    assert c_res["campaign"]["name"] == "Royal Enfield Heritage Desert Ride Camp"
    assert "Neha Trivedi" in c_res["campaign"]["campaign_lead"]

    r_res = dms.dispatch_service_reminder_broadcast()
    assert r_res["success"] is True
    assert r_res["reminders_count"] >= 3
    assert r_res["helpline"] == OFFICIAL_WHATSAPP_HELPLINE
    assert "+91 78747 19139" in r_res["message_gu"]


# =============================================================================
# 2. SHOWROOM SALES, PDI, RIDE SURE & CSAT TESTS
# =============================================================================

def test_dms_showroom_booking():
    dms = get_dms_suite_engine()
    res = dms.create_vehicle_booking(
        customer_name="Pravinbhai Thakor",
        phone="+91 98251 22334",
        bike_model="Himalayan 450 Sherpa",
        colorway="Kamet White",
        booking_amount=15000.0,
        payment_mode="UPI (Instant)",
        finance_bank="HDFC Two Wheeler Finance",
        tentative_delivery_date="2026-10-15"
    )

    assert res["success"] is True
    bk = res["booking"]
    assert bk["booking_id"].startswith("BK-RE-2026-")
    assert bk["customer_name"] == "Pravinbhai Thakor"
    assert bk["booking_amount"] == 15000.0
    assert bk["token_receipt_no"].startswith("RCP-BK-")
    assert bk["payment_status"] == "CONFIRMED"
    assert "Vikram Singh" in bk["sales_manager"]


def test_dms_digital_pdi_inspection():
    dms = get_dms_suite_engine()
    res = dms.generate_pdi_inspection(
        chassis_no="ME3H450SHERPA7711",
        engine_no="E450-8822",
        bike_model="Himalayan 450",
        customer_name="Pravinbhai Thakor",
        battery_voltage=12.9,
        idle_rpm=1050,
        toolkit_handed_over=True
    )

    assert res["success"] is True
    pdi = res["pdi_certificate"]
    assert pdi["pdi_id"].startswith("PDI-CERT-2026-")
    assert pdi["pdi_clearance"] == "FACTORY_PASSED_CERTIFIED"
    assert pdi["status"] == "READY_FOR_DELIVERY"
    assert pdi["battery_voltage"] == 12.9
    assert pdi["idle_rpm"] == 1050
    assert pdi["toolkit_handed_over"] is True


def test_dms_ride_sure_warranty():
    dms = get_dms_suite_engine()
    res = dms.issue_ride_sure_warranty(
        customer_name="Pravinbhai Thakor",
        phone="+91 98251 22334",
        bike_model="Himalayan 450",
        registration_no="GJ-02-RE-7711",
        chassis_no="ME3H450SHERPA7711",
        coverage_years=4,
        plan_type="Ride Sure Premium (Extended Warranty + 24/7 Roadside Assistance)",
        premium_amount=3850.0
    )

    assert res["success"] is True
    pol = res["policy"]
    assert pol["policy_no"].startswith("RE-RS-2026-")
    assert pol["coverage_years"] == 4
    assert pol["emergency_helpline"] == OFFICIAL_WHATSAPP_HELPLINE
    assert pol["status"] == "ACTIVE_POLICY"
    assert "Vikram Singh" in pol["issued_by"]


def test_dms_accidental_insurance_estimate():
    dms = get_dms_suite_engine()
    res = dms.create_insurance_claim_estimate(
        customer_name="Jayesh Patel",
        phone="+91 98250 11223",
        bike_model="Classic 350",
        registration_no="GJ-02-CD-5678",
        insurance_company="ICICI Lombard General Insurance",
        surveyor_name="M. K. Trivedi (IRDAI Surveyor)",
        parts_estimate=15000.0,
        labor_estimate=5000.0,
        salvage_deduction=250.0,
        compulsory_deductible=100.0
    )

    assert res["success"] is True
    est = res["insurance_estimate"]
    assert est["claim_id"].startswith("INS-EST-2026-")
    assert est["insurance_company"] == "ICICI Lombard General Insurance"
    assert est["net_insurer_liability"] > 0
    assert est["delivery_order_status"] == "DO_ISSUANCE_APPROVED"


def test_dms_psf_csat_feedback():
    dms = get_dms_suite_engine()
    res = dms.record_post_service_feedback(
        invoice_no="INV-RE-2026-001",
        customer_name="Alpesh Sir",
        phone="+91 98250 12345",
        bike_model="Continental GT 650",
        rating_1_to_5=5,
        feedback_notes="Twin cylinder throttle response is exceptionally smooth and crisp.",
        issues_resolved=True
    )

    assert res["success"] is True
    fb = res["feedback"]
    assert fb["psf_id"].startswith("PSF-2026-")
    assert fb["rating"] == 5
    assert fb["csat_status"] == "DELIGHTED"
    assert fb["issues_resolved"] is True
    assert "Ananya Joshi" in fb["auditor"]

    # Telemetry
    csat = dms.get_csat_and_qc_telemetry()
    assert csat["dealership_csat_percentage"] >= 90.0
    assert csat["csat_benchmark_status"] == "OEM_EXCELLENCE_GREEN"


# =============================================================================
# 3. SUBAGENTS EXPANSION & ROUTING TESTS (10 Dealership Officers)
# =============================================================================

def test_subagents_fleet_10_officers():
    sub_mgr = get_shop_subagents_manager()
    subagents = sub_mgr.list_subagents()
    agent_ids = [sa["agent_id"] for sa in subagents]

    # Verify all 9 subagents exist
    assert "devang_billing" in agent_ids
    assert "neha_crm_marketing" in agent_ids
    assert "vikram_sales" in agent_ids
    assert "ananya_qc_csat" in agent_ids
    assert "bay_chief" in agent_ids
    assert "parts_specialist" in agent_ids
    assert "customer_receptionist" in agent_ids
    assert "social_growth_manager" in agent_ids
    assert "accounts_controller" in agent_ids
    assert len(subagents) == 9

    vikram = sub_mgr.get_subagent("vikram_sales")
    assert "Vikram Singh" in vikram["designated_head"]
    assert any("PDI" in c or "Booking" in c for c in vikram["capabilities"])

    ananya = sub_mgr.get_subagent("ananya_qc_csat")
    assert "Ananya Joshi" in ananya["designated_head"]
    assert any("CSAT" in c or "Quality" in c for c in ananya["capabilities"])


def test_subagents_written_command_routing_10_officers():
    sub_mgr = get_shop_subagents_manager()

    # Vikram Sales Routing
    res_vikram = sub_mgr.execute_written_command("Vikram book new Classic 350 with HDFC finance")
    assert res_vikram["target_agent"] == "vikram_sales"
    assert "Vikram Singh" in res_vikram["designated_head"]
    assert "Vikram Singh" in res_vikram["response_en"]
    assert "બુકિંગ" in res_vikram["response_gu"] or "બાઈક" in res_vikram["response_gu"]

    # Ananya QC & CSAT Routing
    res_ananya = sub_mgr.execute_written_command("Ananya record 5 star CSAT feedback for service")
    assert res_ananya["target_agent"] == "ananya_qc_csat"
    assert "Ananya Joshi" in res_ananya["designated_head"]
    assert "Ananya Joshi" in res_ananya["response_en"]
    assert "સંતોષ" in res_ananya["response_gu"] or "CSAT" in res_ananya["response_gu"]

    # Devang Billing Routing
    res_devang = sub_mgr.execute_written_command("Devang bhai generate split GST invoice for Classic 350")
    assert res_devang["target_agent"] == "devang_billing"
    assert "Devang Dave" in res_devang["designated_head"]

    # Neha CRM Marketing Routing
    res_neha = sub_mgr.execute_written_command("Neha run WhatsApp campaign for service camp")
    assert res_neha["target_agent"] == "neha_crm_marketing"
    assert "Neha Trivedi" in res_neha["designated_head"]


# =============================================================================
# 4. AGENT COMMANDER DIRECTIVES TESTS
# =============================================================================

def test_commander_dms_directives_all():
    cmd = AgentCommander()

    # Overview
    ov = cmd.execute_dms_directive(action="overview")
    assert ov["success"] is True
    assert "Chamunda Automobile" in ov["overview"]["dealership_name"]

    # Create Booking
    bk_res = cmd.execute_dms_directive(
        action="create_booking",
        params={
            "customer_name": "Bharat Patel",
            "phone": "+91 98255 66778",
            "bike_model": "Hunter 350 Dapper Grey",
            "booking_amount": 10000.0
        }
    )
    assert bk_res["success"] is True
    assert bk_res["booking"]["customer_name"] == "Bharat Patel"

    # Generate PDI
    pdi_res = cmd.execute_dms_directive(
        action="generate_pdi",
        params={
            "chassis_no": "ME3H350HUNTER01",
            "engine_no": "H350-1100",
            "bike_model": "Hunter 350",
            "customer_name": "Bharat Patel"
        }
    )
    assert pdi_res["success"] is True
    assert pdi_res["pdi_certificate"]["pdi_clearance"] == "FACTORY_PASSED_CERTIFIED"

    # Issue Ride Sure
    rs_res = cmd.execute_dms_directive(
        action="issue_ride_sure",
        params={
            "customer_name": "Bharat Patel",
            "phone": "+91 98255 66778",
            "bike_model": "Hunter 350",
            "registration_no": "GJ-02-BK-9911",
            "chassis_no": "ME3H350HUNTER01",
            "coverage_years": 5
        }
    )
    assert rs_res["success"] is True
    assert rs_res["policy"]["coverage_years"] == 5

    # Insurance Claim
    ins_res = cmd.execute_dms_directive(
        action="create_insurance_claim",
        params={
            "customer_name": "Bharat Patel",
            "phone": "+91 98255 66778",
            "bike_model": "Hunter 350",
            "registration_no": "GJ-02-BK-9911",
            "insurance_company": "Go Digit General Insurance",
            "surveyor_name": "R. K. Sharma",
            "parts_estimate": 8000.0,
            "labor_estimate": 2500.0
        }
    )
    assert ins_res["success"] is True
    assert ins_res["insurance_estimate"]["insurance_company"] == "Go Digit General Insurance"

    # Record PSF
    psf_res = cmd.execute_dms_directive(
        action="record_psf",
        params={
            "invoice_no": "INV-091",
            "customer_name": "Bharat Patel",
            "phone": "+91 98255 66778",
            "bike_model": "Hunter 350",
            "rating_1_to_5": 5,
            "feedback_notes": "Very prompt service"
        }
    )
    assert psf_res["success"] is True
    assert psf_res["feedback"]["rating"] == 5

    # CSAT & Showroom Telemetry
    assert cmd.execute_dms_directive(action="csat_telemetry")["success"] is True
    assert cmd.execute_dms_directive(action="showroom_telemetry")["success"] is True


# =============================================================================
# 5. CHAMUNDA CEO EXECUTIVE TOOLS TESTS
# =============================================================================

def test_ceo_dms_tools_all():
    # 1. Telemetry
    tel_str = chamunda_get_dms_executive_telemetry()
    assert "Chamunda Royal Enfield Dealer Management System" in tel_str
    assert "+91 78747 19139" in tel_str
    assert "24AAPCC4469R1Z8" in tel_str

    # 2. Vehicle Booking
    bk_str = chamunda_create_vehicle_booking(
        customer_name="Kishorbhai Prajapati",
        phone="+91 98250 99881",
        bike_model="Super Meteor 650",
        booking_amount=25000.0,
        finance_bank="HDFC Two Wheeler Finance"
    )
    assert "Booking Confirmed" in bk_str
    assert "Kishorbhai Prajapati" in bk_str
    assert "Super Meteor 650" in bk_str
    assert "Vikram Singh" in bk_str

    # 3. PDI Certificate
    pdi_str = chamunda_generate_pdi_certificate(
        chassis_no="ME3SM650NR001",
        engine_no="SM650-9911",
        bike_model="Super Meteor 650",
        customer_name="Kishorbhai Prajapati"
    )
    assert "30-Point PDI Delivery Passport" in pdi_str
    assert "READY_FOR_DELIVERY" in pdi_str
    assert "Vikram Singh" in pdi_str

    # 4. Ride Sure Warranty
    rs_str = chamunda_issue_ride_sure_warranty(
        customer_name="Kishorbhai Prajapati",
        phone="+91 98250 99881",
        bike_model="Super Meteor 650",
        registration_no="GJ-02-SM-6500",
        chassis_no="ME3SM650NR001",
        coverage_years=5
    )
    assert "Ride Sure" in rs_str and "Extended Warranty" in rs_str
    assert "+91 78747 19139" in rs_str

    # 5. PSF CSAT Feedback
    psf_str = chamunda_record_psf_csat_feedback(
        invoice_no="INV-SM-001",
        customer_name="Kishorbhai Prajapati",
        phone="+91 98250 99881",
        bike_model="Super Meteor 650",
        rating_1_to_5=5,
        feedback_notes="Flawless showroom delivery and first service experience."
    )
    assert "Post-Service Feedback" in psf_str
    assert "Ananya Joshi" in psf_str

    # 6. CSAT Telemetry
    csat_str = chamunda_get_dms_csat_qc_telemetry()
    assert "Quality Control & CSAT" in csat_str
    assert "Ananya Joshi" in csat_str


# =============================================================================
# 6. FASTAPI REST API ENDPOINTS TESTS (App Tab 26 Integration)
# =============================================================================

def test_fastapi_dms_endpoints_all(client):
    # GET /api/dms/overview (must return all 10 officers)
    res_ov = client.get("/api/dms/overview")
    assert res_ov.status_code == 200
    data_ov = res_ov.json()
    assert data_ov["success"] is True
    assert "overview" in data_ov
    assert len(data_ov["fleet"]) == 10
    agent_ids = [sa["agent_id"] for sa in data_ov["fleet"]]
    assert "aradhya_ceo" in agent_ids
    assert "vikram_sales" in agent_ids
    assert "ananya_qc_csat" in agent_ids

    # POST /api/dms/booking
    res_bk = client.post("/api/dms/booking", json={
        "customer_name": "Jigneshbhai Dave",
        "phone": "+91 98250 77889",
        "bike_model": "Classic 350 (Reborn)",
        "colorway": "Halcyon Green",
        "booking_amount": 10000.0,
        "payment_mode": "UPI (Instant)",
        "finance_bank": "HDFC Two Wheeler Finance"
    })
    assert res_bk.status_code == 200
    assert res_bk.json()["success"] is True
    assert res_bk.json()["booking"]["customer_name"] == "Jigneshbhai Dave"

    # POST /api/dms/pdi
    res_pdi = client.post("/api/dms/pdi", json={
        "chassis_no": "ME3J350NR887766",
        "engine_no": "J350-2026-3344",
        "bike_model": "Classic 350",
        "customer_name": "Jigneshbhai Dave",
        "battery_voltage": 12.8,
        "toolkit_handed_over": True
    })
    assert res_pdi.status_code == 200
    assert res_pdi.json()["success"] is True
    assert res_pdi.json()["pdi_certificate"]["pdi_clearance"] == "FACTORY_PASSED_CERTIFIED"

    # POST /api/dms/ride-sure
    res_rs = client.post("/api/dms/ride-sure", json={
        "customer_name": "Jigneshbhai Dave",
        "phone": "+91 98250 77889",
        "bike_model": "Classic 350",
        "registration_no": "GJ-02-JD-3500",
        "chassis_no": "ME3J350NR887766",
        "coverage_years": 4
    })
    assert res_rs.status_code == 200
    assert res_rs.json()["success"] is True
    assert res_rs.json()["policy"]["coverage_years"] == 4

    # POST /api/dms/insurance-estimate
    res_ins = client.post("/api/dms/insurance-estimate", json={
        "customer_name": "Jigneshbhai Dave",
        "phone": "+91 98250 77889",
        "bike_model": "Classic 350",
        "registration_no": "GJ-02-JD-3500",
        "insurance_company": "HDFC ERGO General Insurance",
        "surveyor_name": "P. B. Vaghela",
        "parts_estimate": 12000.0,
        "labor_estimate": 3500.0
    })
    assert res_ins.status_code == 200
    assert res_ins.json()["success"] is True
    assert res_ins.json()["insurance_estimate"]["delivery_order_status"] == "DO_ISSUANCE_APPROVED"

    # POST /api/dms/psf-feedback
    res_psf = client.post("/api/dms/psf-feedback", json={
        "invoice_no": "INV-0099",
        "customer_name": "Jigneshbhai Dave",
        "phone": "+91 98250 77889",
        "bike_model": "Classic 350",
        "rating_1_to_5": 5,
        "feedback_notes": "Prompt delivery and courteous staff.",
        "issues_resolved": True
    })
    assert res_psf.status_code == 200
    assert res_psf.json()["success"] is True
    assert res_psf.json()["feedback"]["rating"] == 5

    # GET /api/dms/csat-telemetry
    res_csat = client.get("/api/dms/csat-telemetry")
    assert res_csat.status_code == 200
    assert res_csat.json()["success"] is True

    # GET /api/dms/showroom-telemetry
    res_sh = client.get("/api/dms/showroom-telemetry")
    assert res_sh.status_code == 200
    assert res_sh.json()["success"] is True
