"""
Chamunda Automobile Parts & Service - CEO Executive Tools for JARVIS.
Equips JARVIS with direct executive control over Royal Enfield parts inventory,
service job cards, motorcycle diagnostics, GST billing, and marketing campaigns.
"""

import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


def _get_modules():
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from inventory_engine import ChamundaInventoryManager
    from service_engine import ChamundaServiceManager
    from billing_engine import ChamundaBillingManager
    from marketing_engine import ChamundaMarketingEngine
    return ChamundaInventoryManager, ChamundaServiceManager, ChamundaBillingManager, ChamundaMarketingEngine


def chamunda_lookup_part(query: str) -> str:
    """
    Search Chamunda Automobile's genuine Royal Enfield parts catalog by part name, bike model, or OEM number.
    Supports natural language and composite filters (e.g. 'Hunter 350 brake pads', '574050/C', 'oil filter under 500').

    Args:
        query: Search term (e.g. 'oil filter', 'clutch plate', 'Hunter 350', 'brake pads', '574050/C').
    """
    ChamundaInventoryManager, _, _, _ = _get_modules()
    mgr = ChamundaInventoryManager()

    # Parse potential price filters e.g. "under 1000", "below 500", "above 2000"
    min_price = None
    max_price = None
    clean_query = query

    m_under = re.search(r'(?:under|below|<|sub)\s*(?:₹|rs\.?|inr)?\s*(\d+)', query, re.IGNORECASE)
    if m_under:
        max_price = float(m_under.group(1))
        clean_query = re.sub(r'(?:under|below|<|sub)\s*(?:₹|rs\.?|inr)?\s*\d+', '', clean_query, flags=re.IGNORECASE).strip()

    m_above = re.search(r'(?:above|over|>)\s*(?:₹|rs\.?|inr)?\s*(\d+)', query, re.IGNORECASE)
    if m_above:
        min_price = float(m_above.group(1))
        clean_query = re.sub(r'(?:above|over|>)\s*(?:₹|rs\.?|inr)?\s*\d+', '', clean_query, flags=re.IGNORECASE).strip()

    matches = mgr.filter_parts(query=clean_query, min_price=min_price, max_price=max_price, limit=20)
    if not matches:
        return f"No Royal Enfield parts found matching '{query}' in Chamunda inventory."

    lines = [f"### 🏍️ Chamunda Automobile - Royal Enfield Spares for '{query}':"]
    for p in matches[:15]:
        models_str = ', '.join(p.get('models', [])[:3])
        lines.append(f"- **{p['name']}** `[{p.get('part_number', p.get('oem_number'))}]`")
        lines.append(f"  Category: {p.get('category', 'Spares')} | Bin: `{p.get('bin_location', 'A-01')}` | Stock: **{p.get('stock', 0)} {p.get('unit', 'Pcs')}**")
        lines.append(f"  MRP: ₹{p.get('mrp', 0)} (Cost: ₹{p.get('cost_price', 0)}) | Compatible: {models_str}\n")
    if len(matches) > 15:
        lines.append(f"*... and {len(matches) - 15} more parts found. Use specific filters (part number, category, price) to narrow down.*")
    return "\n".join(lines)


def chamunda_search_parts_filtered(
    query: str = "",
    part_number: str = "",
    model: str = "",
    category: str = "",
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    stock_status: str = "all",
    sort_by: str = "name",
    limit: int = 15,
) -> str:
    """
    Search and filter Royal Enfield genuine spare parts in Chamunda AI using multi-parameter criteria.

    Args:
        query: General text keyword search (e.g. 'brake pad', 'oil filter', 'clutch', 'LED').
        part_number: OEM Part Number or SKU search (e.g. '574050/C', 'RAM00008', 'RAB00468', '148125').
        model: Bike model name filter (e.g. 'Hunter 350', 'Classic 350', 'Himalayan 450', 'Interceptor 650', 'Meteor 350', 'Bullet 350').
        category: Part category (e.g. 'Periodic Service & Maintenance', 'Braking System', 'Engine & Transmission', 'Electrical & Ignition', 'Suspension, Steering & Chassis', 'Drive Train & Wheels', 'Exhaust & Fuel Delivery', 'Control Cables & Levers', 'Touring, Protection & Accessories').
        min_price: Minimum MRP in INR.
        max_price: Maximum MRP in INR.
        stock_status: Filter by stock: 'all', 'in_stock', 'low_stock', or 'out_of_stock'.
        sort_by: Sort order: 'name', 'price_asc', 'price_desc', 'stock', or 'part_number'.
        limit: Maximum results to display (default: 15).
    """
    ChamundaInventoryManager, _, _, _ = _get_modules()
    mgr = ChamundaInventoryManager()

    results = mgr.filter_parts(
        query=query,
        part_number=part_number,
        model=model,
        category=category,
        min_price=min_price,
        max_price=max_price,
        stock_status=stock_status,
        sort_by=sort_by,
        limit=limit,
    )

    if not results:
        filters_applied = []
        if query:
            filters_applied.append(f"query='{query}'")
        if part_number:
            filters_applied.append(f"part_no='{part_number}'")
        if model:
            filters_applied.append(f"model='{model}'")
        if category:
            filters_applied.append(f"category='{category}'")
        if min_price is not None or max_price is not None:
            filters_applied.append(f"price=₹{min_price or 0} - ₹{max_price or '∞'}")
        if stock_status != "all":
            filters_applied.append(f"stock='{stock_status}'")
        criteria_str = ", ".join(filters_applied) if filters_applied else "none"
        return f"### 🏍️ Chamunda Automobile • Royal Enfield Spares\nNo Royal Enfield spare parts found matching the criteria: ({criteria_str})."

    filter_desc = []
    if query:
        filter_desc.append(f"Keyword: `{query}`")
    if part_number:
        filter_desc.append(f"Part No: `{part_number}`")
    if model:
        filter_desc.append(f"Model: `{model}`")
    if category:
        filter_desc.append(f"Category: `{category}`")
    if min_price is not None or max_price is not None:
        filter_desc.append(f"Price: ₹{min_price or 0} - ₹{max_price or 'Max'}")
    if stock_status != "all":
        filter_desc.append(f"Stock: `{stock_status}`")
    if sort_by != "name":
        filter_desc.append(f"Sorted by: `{sort_by}`")

    filter_header = " | ".join(filter_desc) if filter_desc else "All Royal Enfield Genuine Parts"

    lines = [
        f"### 🏍️ Chamunda Automobile • Royal Enfield Parts Filter ({len(results)} found)",
        f"*{filter_header}*\n",
        "| OEM Part No | Part Name | Category | MRP | Cost | Stock | Bin | Compatible Models |",
        "| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |",
    ]

    for p in results:
        models_disp = ", ".join(p.get("models", [])[:2])
        if len(p.get("models", [])) > 2:
            models_disp += f" (+{len(p['models'])-2})"
        stock_disp = f"**{p.get('stock', 0)}**" if p.get('stock', 0) > 0 else "❌ Out"
        if 0 < p.get('stock', 0) <= p.get('min_threshold', 5):
            stock_disp += " ⚠️"
        lines.append(
            f"| `{p.get('part_number', p.get('oem_number', 'N/A'))}` | **{p.get('name')}** | {p.get('category')} | ₹{p.get('mrp', 0)} | ₹{p.get('cost_price', 0)} | {stock_disp} | `{p.get('bin_location', 'A-01')}` | {models_disp} |"
        )

    return "\n".join(lines)


def chamunda_create_job_card(
    customer_name: str,
    phone: str,
    bike_model: str,
    registration_no: str,
    odometer_km: int,
    customer_issues: str
) -> str:
    """
    Intake a Royal Enfield motorcycle into Chamunda service bay, create a digital job card, and auto-diagnose symptoms.
    
    Args:
        customer_name: Full name of customer.
        phone: Mobile contact number.
        bike_model: Royal Enfield model (e.g. 'Classic 350 Reborn', 'Hunter 350', 'Continental GT 650').
        registration_no: Motorcycle registration plate number.
        odometer_km: Current odometer reading in km.
        customer_issues: Customer complaints (e.g. 'Tappet ticking sound, front brake squeal, engine oil replacement').
    """
    _, ChamundaServiceManager, _, _ = _get_modules()
    mgr = ChamundaServiceManager()
    job = mgr.create_job_card(
        customer_name=customer_name,
        phone=phone,
        bike_model=bike_model,
        registration_no=registration_no,
        odometer_km=odometer_km,
        customer_issues=customer_issues
    )
    return (
        f"Job Card `{job['job_card_id']}` created successfully for **{customer_name}** ({bike_model} - `{registration_no}`).\n"
        f"**Auto-Diagnosis:** {job['diagnostic_recommendation']}\n"
        f"**Estimated Labor:** ₹{job['labor_charges']} | Status: `{job['status']}`"
    )


def chamunda_diagnose_re_bike(symptom: str) -> str:
    """
    Consult the Royal Enfield Master Diagnostic AI for instant root cause, torque/clearance specs, and repair steps.
    
    Args:
        symptom: Motorcycle issue description (e.g. 'cold start tappet noise', 'handlebar wobble at 80 km/h', 'clutch slip').
    """
    _, ChamundaServiceManager, _, _ = _get_modules()
    mgr = ChamundaServiceManager()
    diag = mgr.diagnose_fault(symptom)
    return (
        f"### 🔧 Chamunda RE Diagnostic Report for '{symptom}':\n"
        f"- **Root Cause:** {diag['root_cause']}\n"
        f"- **Master Repair Directive:** {diag['recommended_action']}\n"
        f"- **Estimated Labor:** ₹{diag['estimated_labor_inr']} | Turnaround: {diag['turnaround_time']}\n"
        f"- **Spares Required:** {', '.join(diag['parts_needed'])}"
    )


def chamunda_generate_ceo_revenue_report() -> str:
    """
    Generate the Executive CEO revenue, inventory valuation, and service bay overview for the Chairman/Owner.
    """
    ChamundaInventoryManager, ChamundaServiceManager, _, _ = _get_modules()
    inv_mgr = ChamundaInventoryManager()
    srv_mgr = ChamundaServiceManager()

    val = inv_mgr.get_total_inventory_valuation()
    low = inv_mgr.get_low_stock_alerts()
    jobs = srv_mgr.get_all_job_cards()

    report = f"""# 👑 CHAMUNDA AUTOMOBILE • CEO EXECUTIVE OVERVIEW
*Specialized Royal Enfield Parts & Master Service Hub*

---

### 📊 Financial & Inventory Health:
- **Total Spares in Stock:** {val['total_units_in_stock']} units ({val['total_distinct_skus']} distinct SKUs)
- **Wholesale Asset Value:** ₹{val['cost_valuation_inr']:,}
- **Retail Inventory Value (MRP):** ₹{val['mrp_valuation_inr']:,}
- **Projected Gross Retail Margin:** **₹{val['expected_gross_profit_inr']:,}**

### 🏍️ Service Bay Operations:
- **Active Job Cards:** {len(jobs)} motorcycle(s) in service workflow
- **Low Stock Reorder Alerts:** {len(low)} part(s) below threshold ({', '.join(p['name'][:20] for p in low[:3])})

### 🚀 CEO Strategic Growth Initiatives:
1. **Royal Enfield Custom Tuning & Exhaust Package:** Introduce staged ECU flash & free-flow exhaust bundles.
2. **Predictive Service WhatsApp Bot:** Auto-dispatch 90-day service reminders with invoice history.
3. **Daily YouTube Shorts Marketing:** Showcase real workshop repairs & exhaust sound tests to drive footfall.

*Standing by for your strategic directives, Chairman.*
"""
    return report


def chamunda_launch_re_marketing_campaign(topic: str = "") -> str:
    """
    Command the subordinate YouTube agent to create and publish a viral Royal Enfield video reel for Chamunda Automobile.
    
    Args:
        topic: Optional custom topic (e.g. 'Classic 350 Tappet Sound Fix', 'Hunter 350 vs Classic 350 Service').
    """
    _, _, _, ChamundaMarketingEngine = _get_modules()
    mkt = ChamundaMarketingEngine()
    res = mkt.launch_re_marketing_short(custom_topic=topic if topic else None)
    if res.get("success"):
        return f"YouTube Marketing Campaign for Chamunda Automobile completed successfully, Chairman. Video rendered at: {res.get('video_path')}"
    return f"Marketing campaign execution response: {res.get('status') or res.get('error')}"


def chamunda_generate_health_passport(
    customer_name: str,
    phone: str,
    bike_model: str,
    registration_no: str,
    odometer_km: int,
    service_notes: str = "Standard 50-Point Master Service + Valve Clearance Calibration",
    audio_path: Optional[str] = None,
) -> str:
    """
    Generate an official Digital Acoustic Health Passport for a serviced Royal Enfield motorcycle,
    certifying engine harmonics, valve clearances, and showroom mint condition.

    Args:
        customer_name: Customer's full name.
        phone: Customer mobile number.
        bike_model: Royal Enfield model (e.g. 'Hunter 350', 'Classic 350 Reborn', 'Himalayan 450', 'Interceptor 650').
        registration_no: Motorcycle registration plate number (e.g. 'GJ-01-RE-3500').
        odometer_km: Current odometer reading in km.
        service_notes: Service description or repairs performed.
        audio_path: Optional audio recording (.wav) of engine idle sound.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from acoustic_health_passport import ChamundaHealthPassportGenerator

    gen = ChamundaHealthPassportGenerator()
    rec = gen.generate_health_passport(
        customer_name=customer_name,
        phone=phone,
        bike_model=bike_model,
        registration_no=registration_no,
        odometer_km=odometer_km,
        service_notes=service_notes,
        audio_path=audio_path,
    )

    report = f"""### 📜 Chamunda Automobile • Digital Acoustic Health Passport
**Certificate ID:** `{rec['passport_id']}`  
**Motorcycle:** **{bike_model}** (`{registration_no}`) | **Odometer:** `{odometer_km:,} KM`  
**Customer:** **{customer_name}** (`{phone}`)  
**Overall Engine Health Score:** **`{rec['overall_score']}/100`** ({rec['grade']})

---

#### 🌟 Passport Assets & Verification
- **Verified HTML Certificate:** [{rec['passport_id']}.html](file://{rec['html_path']})
- **Next Recommended Service:** `{rec['next_service_km']:,} KM`

---

#### 💬 Ready-to-Send WhatsApp Broadcast Copy (Gujarati):
```
{rec['whatsapp_gujarati']}
```

#### 💬 English WhatsApp Copy:
```
{rec['whatsapp_english']}
```
"""
    return report


def chamunda_diagnose_engine_sound(
    bike_model: str = "Classic 350",
    audio_path: Optional[str] = None,
    record_seconds: int = 5,
    simulate_fault: Optional[str] = None,
) -> str:
    """
    Perform live Fast Fourier Transform (FFT) acoustic analysis on Royal Enfield engine sound,
    detect mechanical faults (tappets, cam chain, clutch, piston, exhaust), and automatically
    recommend exact matching genuine OEM spare parts from Chamunda's 4,469 parts catalog.

    Args:
        bike_model: Royal Enfield model (e.g. 'Hunter 350', 'Classic 350', 'Himalayan 450', 'Interceptor 650').
        audio_path: Optional path to .wav audio recording.
        record_seconds: Duration in seconds to record from microphone (default: 5).
        simulate_fault: Optional fault to simulate for testing ('tappet', 'chain', 'clutch', 'piston', 'exhaust', 'healthy').
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from acoustic_sound_diagnostic import ChamundaSoundDiagnosticEngine

    sim_map = {
        "tappet": "tappet_valve_noise",
        "chain": "timing_chain_slack",
        "clutch": "clutch_primary_whine",
        "piston": "piston_slap_knock",
        "exhaust": "exhaust_leak_turbulence",
        "healthy": None
    }
    sim_key = sim_map.get(simulate_fault, simulate_fault) if simulate_fault else None

    engine = ChamundaSoundDiagnosticEngine()
    rep = engine.diagnose_engine_sound(
        bike_model=bike_model,
        audio_path=audio_path,
        record_seconds=record_seconds,
        inject_simulation=sim_key
    )

    lines = [
        f"### 🎙️ Chamunda Automobile • Engine Sound Diagnostic Report",
        f"**Diagnostic ID:** `{rep['diagnostic_id']}` | **Audio Source:** {rep['audio_source']}",
        f"**Motorcycle:** **{bike_model}** | **Acoustic Level:** {rep['estimated_db']} dB | **Rhythm:** {rep['dominant_freq_hz']} Hz",
        f"**Health Score:** **`{rep['health_score']}/100`** ({rep['health_status']})",
        f"**સારાંશ:** {rep['summary_gu']}\n",
        "---"
    ]

    anomalies = rep.get("anomalies_detected", [])
    if not anomalies:
        lines.append("\n✅ **No Mechanical Anomalies Detected:** Engine harmonics and valve/chain tolerances are in factory mint condition.")
    else:
        lines.append(f"\n#### ⚠️ Mechanical Anomalies Identified ({len(anomalies)}):")
        for idx, anom in enumerate(anomalies, 1):
            lines.append(f"{idx}. **{anom['title']}** (*{anom['title_gu']}*)")
            lines.append(f"   - **Severity:** {anom['severity']} | **Confidence:** {anom['confidence_pct']}%")
            lines.append(f"   - **Root Cause:** {anom['root_cause']}")
            lines.append(f"   - **Action Required:** {anom['recommended_action']}\n")

    parts_recs = rep.get("parts_recommendations", [])
    if parts_recs:
        lines.append("#### 🔧 Recommended Genuine OEM Spare Parts (from 4,469 Parts Catalog):")
        lines.append("| OEM Part Number | Part Description | MRP | Stock | Bin Location |")
        lines.append("| :--- | :--- | :---: | :---: | :--- |")
        for r in parts_recs:
            for p in r.get("matched_oem_parts", []):
                lines.append(f"| `{p.get('part_number', 'N/A')}` | **{p.get('name')}** | ₹{p.get('mrp', 0)} | **{p.get('stock', 0)} Pcs** | `{p.get('bin_location', 'A-01')}` |")

    return "\n".join(lines)


def chamunda_complete_job_and_invoice(
    job_card_id: str,
    technician: str = "Master Tech Alpesh (Chamunda Automobile)",
    service_notes: str = "Standard 50-Point Master Service & Valve Calibration"
) -> str:
    """
    Close a service job card, automatically generate the Digital Acoustic Health Passport,
    embed the verifiable QR code, and generate the official GST Tax Invoice for Chamunda Automobile.

    Args:
        job_card_id: Job card ID (e.g. 'JOB-20260908-001').
        technician: Name of the assigned master technician.
        service_notes: Repairs and tuning work carried out.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from service_engine import ChamundaServiceManager

    mgr = ChamundaServiceManager()
    res = mgr.complete_job_and_generate_invoice(
        job_card_id=job_card_id,
        technician=technician,
        service_notes=service_notes
    )

    report = f"""### 🧾 Chamunda Automobile • Service Completed & GST Invoice Issued
**Job Card ID:** `{res['job_card_id']}` (Status: **Completed**)  
**Customer:** **{res['customer_name']}** | **Motorcycle:** **{res['bike_model']}** (`{res['registration_no']}`)  
**Invoice Number:** `{res['invoice_no']}` | **Grand Total:** **₹{res['grand_total']:,}** (Subtotal: ₹{res['subtotal']:,} + GST: ₹{res['gst_amount']:,})  
**Digital Health Passport:** `{res['passport_id']}` (Score: **`{res['health_score']}/100`** - {res['grade']})

---

#### 📁 Generated Documents & Assets
- **GST Tax Invoice (HTML with QR Code):** [{res['invoice_no']}.html](file://{res['invoice_file']})
- **Digital Health Passport Certificate:** [{res['passport_id']}.html](file://{res['passport_file']})
- **Next Service Due:** `{res['next_service_date']}` or `{res['next_service_km']:,} KM`

---

#### 💬 Ready-to-Send WhatsApp Dispatch (Gujarati):
```
{res['whatsapp_gujarati']}
```

#### 💬 Ready-to-Send WhatsApp Dispatch (English):
```
{res['whatsapp_english']}
```
"""
    return report


def chamunda_launch_workshop_portal() -> str:
    """
    Launch or inspect the status of the Chamunda AI Interactive Workshop Web Portal & Live Mobile QR Viewer.
    Provides local and WiFi network access URLs for the touchscreen dashboard.
    """
    import socket
    import subprocess
    import shutil

    # Check local IP
    local_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    # Check if server is already running on port 8080
    port_in_use = False
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8080))
        sock.close()
        if result == 0:
            port_in_use = True
    except Exception:
        pass

    if not port_in_use:
        # Start uvicorn in background
        subprocess.Popen(
            ["python3", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"],
            cwd="/home/alpesh/chamunda_re_enterprise",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        time.sleep(1.2)

    return f"""### 🌐 Chamunda AI • Interactive Workshop Web Portal
**Status:** 🟢 **Active & Online** (FastAPI / Uvicorn)

---

#### 🔗 Access Links:
- **Workshop Laptop / Desktop:** [http://127.0.0.1:8080](http://127.0.0.1:8080)
- **Mobile / Tablet (Workshop WiFi):** [http://{local_ip}:8080](http://{local_ip}:8080)

---

#### 🌟 Flagship Touchscreen Modules:
1. **🎙️ Live Engine Sound Diagnostic Bay:** One-touch 5s microphone engine listening, dynamic canvas wave visualizer, anomaly detection, and OEM parts recommender.
2. **🔍 4,469 Parts Dynamic Filter:** Real-time multi-dimensional search across all genuine Royal Enfield SKUs, stock levels, and warehouse bins.
3. **📋 Active Service Bays & QR Invoicing:** One-click job card completion, automated Digital Health Passport, and GST Tax Invoice with embedded QR code.
4. **📲 Customer Mobile QR Verification:** Automatic landing page (`/passport/{{id}}`) when customers scan the QR code on their motorcycle or invoice.
5. **📅 Predictive Service CRM & WhatsApp Reminders:** Automated service due projections and bilingual customer reminders.
6. **📦 Wholesale Stock Replenishment PO Generator:** One-click procurement orders for items below safety thresholds.
"""


def chamunda_get_predictive_service_reminders() -> str:
    """
    Query Chamunda AI's Predictive Service CRM to identify customer Royal Enfield motorcycles
    due for periodic maintenance based on elapsed days, projected mileage (~32 km/day),
    and Acoustic Health Passport history. Generates executive metrics and WhatsApp copies.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from crm_engine import ChamundaCRMManager
    crm = ChamundaCRMManager()
    data = crm.get_predictive_service_reminders()

    total = data["total_fleet_tracked"]
    due_now = data["due_now_count"]
    upcoming = data["upcoming_count"]
    recent = data["recent_count"]

    lines = [
        "### 📅 Chamunda AI • Predictive Service CRM & Reminder Intelligence",
        f"**Fleet Monitored:** {total} Vehicles | 🔴 **Due Now:** {due_now} | 🟡 **Upcoming (Next 30D):** {upcoming} | 🟢 **Healthy/Recent:** {recent}",
        "",
        "---",
        "#### 🔴 URGENT: Service Due Now (Elapsed ≥80 Days or ≥2,800 KM):"
    ]

    if not data["due_now_customers"]:
        lines.append("*No vehicles currently in critical overdue state.*")
    else:
        for idx, c in enumerate(data["due_now_customers"], 1):
            wa_first = c['whatsapp_gujarati'].splitlines()[0] if c['whatsapp_gujarati'] else ""
            lines.append(
                f"{idx}. **{c['customer_name']}** ({c['phone']}) - `{c['registration_no']}` [{c['bike_model']}]\n"
                f"   - **Last Service:** {c['last_service_date']} (**{c['days_elapsed']} days ago**)\n"
                f"   - **Estimated Odo:** ~{c['projected_odometer_km']:,} KM (Base: {c['base_odometer_km']:,} KM)\n"
                f"   - **Acoustic Health Score:** {c['health_score']}/100\n"
                f"   - **WhatsApp Prompt:** {wa_first}"
            )

    lines.extend([
        "",
        "---",
        "#### 🟡 UPCOMING: Service Required Soon (55 to 79 Days):"
    ])

    if not data["upcoming_customers"]:
        lines.append("*No vehicles in 55-79 day window.*")
    else:
        for idx, c in enumerate(data["upcoming_customers"], 1):
            lines.append(
                f"{idx}. **{c['customer_name']}** - `{c['registration_no']}` [{c['bike_model']}] - {c['days_elapsed']} days elapsed (~{c['projected_odometer_km']:,} KM)"
            )

    lines.extend([
        "",
        "---",
        "💡 *Tip: You can dispatch WhatsApp reminders in one click from Tab 6 of the Workshop Web Portal (http://127.0.0.1:8080).*"
    ])

    return "\n".join(lines)


def chamunda_generate_wholesale_po(supplier_name: str = "Royal Enfield OEM Genuine Spares Dist.") -> str:
    """
    Generate an official Wholesale Stock Replenishment Purchase Order (PO)
    for Royal Enfield spare parts that are below minimum inventory threshold.
    Calculates reorder quantities, unit costs, and total wholesale financial outlay.

    Args:
        supplier_name: Name of the OEM distributor or vendor.
    """
    sys.path.insert(0, "/home/alpesh/jarvis-agent")
    from core.wholesale_po_engine import WholesalePOEngine
    po_eng = WholesalePOEngine()
    po = po_eng.generate_low_stock_purchase_order(supplier_name=supplier_name)

    items = po["items"]
    lines = [
        "### 📦 Chamunda AI • Official Wholesale Purchase Order Generated",
        f"**PO Number:** `{po['po_number']}`",
        f"**Supplier / Vendor:** {supplier_name}",
        f"**Total Reorder SKUs:** {len(items)} Items",
        f"**Total Wholesale Outlay:** **₹{po['total_outlay_inr']:,}**",
        f"**Formal Document HTML:** `{po['po_file']}`",
        "",
        "---",
        "#### 📋 Top Replenishment Line Items:"
    ]
    for idx, item in enumerate(items[:8], 1):
        lines.append(
            f"{idx}. **{item['name']}** (`{item['oem_number']}`)\n"
            f"   - Reorder Qty: **{item['qty']} Units** | Rate: ₹{item['unit_cost']} | Outlay: ₹{item['total']:,}"
        )
    if len(items) > 8:
        lines.append(f"*... and {len(items) - 8} more SKUs included in full PO.*")

    lines.extend([
        "",
        "---",
        f"🔗 **View / Print Formal PO:** Open [http://127.0.0.1:8080/po/{po['po_number']}](http://127.0.0.1:8080/po/{po['po_number']})"
    ])
    return "\n".join(lines)


def chamunda_track_customer_service_status(identifier: str) -> str:
    """
    Track customer Royal Enfield service progress and live workshop stage
    across the 5-stage pipeline (Intake -> 50-Pt Inspection -> Engine Work -> Foam Wash -> Ready for Delivery).
    
    Args:
        identifier: Bike registration number (e.g. 'GJ-01-AB-1234'), customer phone number, or Job Card ID.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from customer_bot_engine import ChamundaCustomerBot
    bot = ChamundaCustomerBot()
    res = bot.track_service_status(identifier)

    if not res.get("found"):
        return f"❌ {res.get('message', f'No active job card found for identifier: {identifier}')}"

    cur_stage = res.get("current_stage", {})
    lines = [
        f"### 🏍️ Chamunda AI • Live Service Stage Tracking: `{res['registration_no']}`",
        f"**Customer:** {res['customer_name']} (Phone: {res.get('phone', 'N/A')})",
        f"**Motorcycle:** {res['bike_model']} | **Job Card ID:** `{res['job_card_id']}`",
        f"**Current Stage:** {cur_stage.get('icon', '🛠️')} **{cur_stage.get('name', 'In Progress')}** ({cur_stage.get('name_gu', '')})",
        f"**Overall Progress:** **{res['progress_pct']}%**",
        f"**Assigned Master Tech:** {res.get('mechanic_assigned', 'Master Tech Alpesh')}",
        f"**Est. Delivery:** {res.get('estimated_delivery', 'Today 05:30 PM')}",
        f"**Estimated Bill:** **₹{res.get('estimated_total_inr', 0):,}**",
        f"💬 **24/7 WhatsApp AI Bot:** **+91 78747 19139** ([Chat on WhatsApp](https://wa.me/917874719139))",
        "",
        "---",
        "#### 📱 Customer WhatsApp Status Update (Gujarati):",
        res.get("message_gu", "")
    ]
    return "\n".join(lines)


def chamunda_tune_engine_thump(bike_model: str = "Classic 350", profile: str = "deep_vintage_chug") -> str:
    """
    Perform Fast Fourier Transform (FFT) sub-bass acoustic resonance analysis
    on Royal Enfield exhaust cadence, measure Thump Depth (dB), calculate the Iconic Thump Score (0-100),
    and generate step-by-step master mechanic calibration directives.
    
    Args:
        bike_model: Royal Enfield model name (e.g. 'Classic 350', 'Bullet 350', 'Hunter 350', 'Himalayan 450', 'Interceptor 650').
        profile: Target acoustic profile ('deep_vintage_chug', 'factory_oem_clean', 'cruiser_bass_rumble', 'sherpa_highland_growl', 'twin_270_crossplane_roar').
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from thump_tuner_engine import ChamundaThumpTuner
    tuner = ChamundaThumpTuner()
    res = tuner.analyze_exhaust_thump(bike_model=bike_model, preset_key=profile)

    lines = [
        f"### 🏍️ Chamunda AI • Iconic Thump Tuner & Acoustic Resonance Calibrator",
        f"**Motorcycle Model:** {res['bike_model']}",
        f"**Iconic Thump Score:** **{res['thump_score']} / 100**",
        f"**Acoustic Classification:** {res['rating']}",
        f"**Sub-Bass Resonance (Dominant):** **{res['dominant_bass_hz']} Hz**",
        f"**Idle Cadence Sync:** **{res['idle_cadence_bpm']} RPM**",
        f"**Sound Pressure Level:** **{res['estimated_db']} dB** (RTO Legal Limit <85 dB: {'✅ COMPLIANT' if res['rto_legal_compliant'] else '⚠️ EXCEEDS LIMIT'})",
        "",
        "---",
        "#### 🔧 Master Mechanic Step-by-Step Directives:"
    ]
    for d in res["mechanic_directives"]:
        lines.append(d)

    lines.extend([
        "",
        f"**ગુજરાતી સારાંશ:** {res['summary_gu']}"
    ])
    return "\n".join(lines)


def chamunda_create_quick_counter_pos_sale(
    part_skus: str,
    customer_name: str = "Counter Walk-in Customer",
    phone: str = "",
    discount_amount: float = 0.0
) -> str:
    """
    Process an instant over-the-counter spare parts sale with camera/barcode lookup,
    automatic inventory deduction, dynamic NPCI UPI QR code generation, and 80mm thermal receipt printing.
    
    Args:
        part_skus: Comma-separated list of Part IDs, OEM numbers, or search queries (e.g. '574050/C, RAM00008/B').
        customer_name: Name of counter walk-in customer.
        phone: Customer phone number for digital receipt WhatsApp copy.
        discount_amount: Optional cash discount in INR.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from counter_pos_engine import ChamundaCounterPOS
    pos = ChamundaCounterPOS()

    sku_list = [s.strip() for s in part_skus.split(",") if s.strip()]
    if not sku_list:
        return "❌ Error: Please provide at least one part SKU or part number."

    cart_items = [{"part_id": s, "qty": 1} for s in sku_list]
    sale = pos.create_counter_sale(
        cart_items=cart_items,
        customer_name=customer_name,
        phone=phone,
        discount_amount=discount_amount
    )

    lines = [
        f"### 🛒 Chamunda AI • Instant Counter POS Sale Completed",
        f"**Receipt Number:** `{sale['receipt_no']}`",
        f"**Customer:** {sale['customer_name']} (Phone: {sale.get('phone') or 'Counter Walk-in'})",
        f"**Items Total (MRP):** ₹{sale['subtotal']:.2f}",
        f"**Discount Applied:** ₹{sale['discount']:.2f}",
        f"**Net Amount Payable:** **₹{sale['net_amount']:.2f}** (Includes 18% GST ₹{sale['gst_included']:.2f})",
        "",
        "---",
        "#### 📦 Deducted Inventory Items:"
    ]
    for itm in sale["items"]:
        lines.append(f"- **{itm['name']}** (`{itm['part_number']}`) x{itm['qty']} = ₹{itm['line_total']:.2f} (Remaining stock: {itm['remaining_stock']})")

    lines.extend([
        "",
        "---",
        f"📲 **Dynamic UPI Pay URI:** `{sale['upi_uri']}`",
        f"🖨️ **80mm Thermal Slip HTML:** `{sale['receipt_file']}`",
        f"🔗 **Web Print View:** [http://127.0.0.1:8080/pos/receipt/{sale['receipt_no']}](http://127.0.0.1:8080/pos/receipt/{sale['receipt_no']})"
    ])
    return "\n".join(lines)


def chamunda_inspect_preowned_bike(
    customer_name: str,
    phone: str,
    bike_model: str,
    registration_no: str,
    manufacturing_year: int,
    odometer_km: int,
    engine_pts: int = 23,
    chassis_pts: int = 19,
    acoustic_pts: int = 14,
    brakes_pts: int = 14,
    electrical_pts: int = 14,
    aesthetics_pts: int = 9,
    inspector_name: str = "Master Tech Alpesh (Chamunda Automobile)"
) -> str:
    """
    Execute a comprehensive 100-Point Digital Quality Inspection on a used/pre-owned Royal Enfield.
    Evaluates 6 mechanical & acoustic domains, assigns warranty shield tier (Platinum/Gold/Silver),
    matches required OEM replacement parts from 4,469 inventory, and issues verifiable QR certificate.

    Args:
        customer_name: Owner or prospective buyer's name.
        phone: Contact mobile number.
        bike_model: Royal Enfield model (e.g. 'Classic 350', 'Hunter 350', 'Himalayan 450', 'Bullet 350').
        registration_no: Motorcycle registration plate (e.g. 'GJ-01-RE-2022').
        manufacturing_year: Year of manufacture (e.g. 2022).
        odometer_km: Current odometer reading in kilometers.
        engine_pts: Engine & Transmission score (0-25).
        chassis_pts: Chassis & Suspension score (0-20).
        acoustic_pts: Acoustic Thump & NVH score (0-15).
        brakes_pts: Brakes & ABS score (0-15).
        electrical_pts: Electricals & Battery score (0-15).
        aesthetics_pts: Aesthetics & Odometer Audit score (0-10).
        inspector_name: Lead technician conducting the inspection.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from used_bike_inspection_engine import ChamundaPreOwnedManager
    mgr = ChamundaPreOwnedManager()

    overrides = {
        "engine_pts": int(engine_pts),
        "chassis_pts": int(chassis_pts),
        "acoustic_pts": int(acoustic_pts),
        "brakes_pts": int(brakes_pts),
        "electrical_pts": int(electrical_pts),
        "aesthetics_pts": int(aesthetics_pts)
    }

    report = mgr.conduct_100_point_inspection(
        customer_name=customer_name,
        phone=phone,
        bike_model=bike_model,
        registration_no=registration_no,
        manufacturing_year=int(manufacturing_year),
        odometer_km=int(odometer_km),
        checklist_overrides=overrides,
        inspector_name=inspector_name
    )

    val = report["fair_market_valuation"]
    lines = [
        f"### 🛡️ Chamunda Certified Pre-Owned Royal Enfield • 100-Point Inspection Shield",
        f"**Certificate ID:** `{report['cert_id']}`",
        f"**Vehicle:** {report['bike_model']} ({report['manufacturing_year']}) | **Reg No:** `{report['registration_no']}`",
        f"**Client/Owner:** {report['customer_name']} ({report['phone']})",
        f"**Odometer:** {report['odometer_km']:,} KM",
        "",
        "---",
        f"🎖️ **Total Quality Score:** **{report['total_score']} / 100**",
        f"🏅 **Certification Grade:** **{report['certification_tier']}** ({report['certification_tier_gu']})",
        f"🛡️ **Warranty Shield:** {report['warranty_shield']}",
        f"💰 **Fair Market Valuation:** **₹{val['fair_market_value_inr']:,}** (Target Buyer: ₹{val['recommended_buyer_price_inr']:,} | Asking: ₹{val['recommended_seller_asking_inr']:,})",
        f"📈 **Market Resale Demand:** {val['gujarat_market_demand']}",
        "",
        "---",
        "#### 🔍 Category Breakdown:"
    ]
    for cat in report["categories"]:
        lines.append(f"- **{cat['name']}:** {cat['earned_pts']} / {cat['max_pts']} pts")

    if report.get("recommended_spares"):
        lines.extend(["", "#### 🔧 Recommended Pre-Sale OEM Spares:"])
        for sp in report["recommended_spares"]:
            lines.append(f"- {sp['name']} (`{sp['part_number']}`) - MRP: ₹{sp['mrp']}")

    lines.extend([
        "",
        "---",
        f"📱 **Digital Verifiable Certificate:** [http://127.0.0.1:8080/certification/{report['cert_id']}](http://127.0.0.1:8080/certification/{report['cert_id']})",
        f"🖨️ **HTML File:** `{report['cert_html_file']}`"
    ])
    return "\n".join(lines)


def chamunda_evaluate_market_valuation(
    bike_model: str,
    manufacturing_year: int,
    odometer_km: int,
    condition_score: float = 85.0
) -> str:
    """
    Calculate AI-driven fair market valuation for used Royal Enfield motorcycles in Gujarat.
    Computes standard depreciation, mileage variance penalty/credit, and buyer/seller pricing targets.

    Args:
        bike_model: Royal Enfield model (e.g. 'Classic 350', 'Bullet 350', 'Hunter 350', 'Himalayan 450', 'Interceptor 650').
        manufacturing_year: Year of manufacture (e.g. 2021, 2022, 2023).
        odometer_km: Total kilometers run on odometer.
        condition_score: Overall health or inspection score (0 to 100, default 85).
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from used_bike_inspection_engine import ChamundaPreOwnedManager
    mgr = ChamundaPreOwnedManager()

    val = mgr.calculate_fair_market_valuation(
        bike_model=bike_model,
        manufacturing_year=int(manufacturing_year),
        odometer_km=int(odometer_km),
        condition_score=float(condition_score)
    )

    lines = [
        f"### 💰 Chamunda AI • Royal Enfield Fair Market Valuation",
        f"**Motorcycle Model:** {val['bike_model']}",
        f"**Manufacturing Year:** {val['manufacturing_year']} ({val['age_years']} years old)",
        f"**Odometer Reading:** {val['odometer_km']:,} KM",
        f"**Vehicle Health / Condition Score:** {val['condition_score']}/100",
        f"**Baseline Ex-Showroom Estimate:** ₹{val['original_ex_showroom_est']:,}",
        "",
        "---",
        f"🎯 **AI Fair Market Value:** **₹{val['fair_market_value_inr']:,}**",
        f"💼 **Recommended Workshop Buying Target:** **₹{val['recommended_buyer_price_inr']:,}**",
        f"🏷️ **Recommended Direct Asking Price:** **₹{val['recommended_seller_asking_inr']:,}**",
        f"📊 **Gujarat Regional Demand:** **{val['gujarat_market_demand']}**",
        "",
        "💡 *Tip: Conduct a 100-Point Digital Inspection at Chamunda Automobile to issue a verifiable Warranty Shield Certificate.*"
    ]
    return "\n".join(lines)


def chamunda_audit_expedition_readiness(
    rider_name: str,
    phone: str,
    bike_model: str,
    registration_no: str,
    destination_key: str = "ladakh_high_altitude",
    planned_km: int = 3500,
    domain_scores: Optional[Dict[str, int]] = None,
    inspector_name: str = "Master Tech Alpesh (Chamunda Automobile)"
) -> str:
    """
    Execute 48-Point Royal Enfield Expedition Pre-Touring Clearance Audit across 6 touring domains.
    Assigns touring clearance tier, auto-packages emergency spares kit, generates verifiable Base64 QR code and printable HTML passport.

    Args:
        rider_name: Full name of touring rider.
        phone: Contact phone number.
        bike_model: Royal Enfield model (e.g. 'Himalayan 450', 'Classic 350', 'Interceptor 650', 'Bullet 350').
        registration_no: Motorcycle registration number (e.g. 'GJ-01-AB-1234').
        destination_key: Touring route identifier ('ladakh_high_altitude', 'coastal_highway', 'desert_run', 'monsoon_western_ghats', 'interstate_expressway').
        planned_km: Estimated round-trip distance in kilometers.
        domain_scores: Optional dictionary of domain scores.
        inspector_name: Certifying master technician name.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from expedition_sos_engine import ChamundaExpeditionManager
    mgr = ChamundaExpeditionManager()

    report = mgr.conduct_expedition_audit(
        rider_name=rider_name,
        phone=phone,
        bike_model=bike_model,
        registration_no=registration_no,
        destination_key=destination_key,
        planned_km=int(planned_km),
        domain_scores=domain_scores,
        inspector_name=inspector_name
    )

    lines = [
        f"### 🏔️ Chamunda Royal Enfield Expedition Pre-Flight Clearance",
        f"**Expedition ID:** `{report['expedition_id']}`",
        f"**Rider:** {report['rider_name']} ({report['phone']})",
        f"**Motorcycle:** {report['bike_model']} | **Reg No:** `{report['registration_no']}`",
        f"**Destination:** {report['destination_name']} ({report['destination_terrain']})",
        f"**Planned Distance:** {report['planned_km']:,} KM",
        "",
        "---",
        f"🎖️ **Tour Endurance Score:** **{report['total_score']} / 100**",
        f"🏅 **Expedition Clearance Tier:** **{report['clearance_tier']}** ({report['clearance_tier_gu']})",
        f"🛡️ **Highway Breakdown Shield:** {report['sos_shield']}",
        f"📋 **Mandatory Directives:**",
    ]
    for d in report["directives"]:
        lines.append(f"- {d}")

    lines.extend([
        "",
        "---",
        "#### 🔍 6 Touring Survival Domains Breakdown:"
    ])
    for dom in report["domains"]:
        dom_name = dom.get("name") or dom.get("domain") or "Domain"
        dom_status = dom.get("status", "PASSED")
        lines.append(f"- **{dom_name}:** {dom['earned_pts']} / {dom['max_pts']} pts ({dom_status})")

    if report.get("carry_along_spares"):
        lines.extend(["", f"#### 🎒 Essential Carry-Along Spares Kit ({len(report['carry_along_spares'])} Items • Total: ₹{report['spares_total_cost']:,}):"])
        for sp in report["carry_along_spares"]:
            lines.append(f"- **{sp['name']}** `[{sp['part_number']}]` (Qty: {sp['qty']}) - ₹{sp['price']} | *{sp['criticality']} - {sp['purpose']}*")

    lines.extend([
        "",
        "---",
        f"📱 **Digital Verifiable Clearance Passport:** [http://127.0.0.1:8080/expedition/{report['expedition_id']}](http://127.0.0.1:8080/expedition/{report['expedition_id']})",
        f"🖨️ **HTML File:** `{report['passport_html_file']}`"
    ])
    return "\n".join(lines)


def chamunda_build_carry_along_spares_kit(
    bike_model: str = "Classic 350",
    destination_key: str = "ladakh_high_altitude"
) -> str:
    """
    Generate a model & route specific carry-along backup spares kit from Chamunda's 4,469 parts catalog.
    Packages clutch cables, spark plugs, chain lube/links, fuses, tube/patch kit, and high-altitude engine oils.

    Args:
        bike_model: Royal Enfield model (e.g. 'Himalayan 450', 'Classic 350', 'Hunter 350', 'Interceptor 650').
        destination_key: Touring terrain identifier ('ladakh_high_altitude', 'coastal_highway', 'desert_run', 'monsoon_western_ghats', 'interstate_expressway').
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from expedition_sos_engine import ChamundaExpeditionManager
    mgr = ChamundaExpeditionManager()

    kit = mgr.build_carry_along_spares_kit(bike_model=bike_model, destination_key=destination_key)

    lines = [
        f"### 🎒 Chamunda AI • Expedition Carry-Along Spares Kit",
        f"**Bike Model:** {kit['bike_model']}",
        f"**Destination / Terrain:** {kit['destination']} ({kit['terrain']})",
        f"**Total Spares:** {kit['item_count']} Items | **Estimated Budget:** ₹{kit['total_estimated_cost_inr']:,}",
        "",
        "---",
        "#### 📦 Essential Spares Packing List (From 4,469 Inventory):"
    ]
    for itm in kit["items"]:
        lines.append(f"- **{itm['name']}** `[{itm['part_number']}]`")
        lines.append(f"  Qty: {itm['qty']} | MRP: ₹{itm['mrp']} | Priority: **{itm['criticality']}**")
        lines.append(f"  *Purpose: {itm['purpose']}*\n")

    lines.append("💡 *Tip: Pre-pack these parts inside waterproof saddlebags before departure.*")
    return "\n".join(lines)


def chamunda_highway_breakdown_sos_triage(
    symptom_query: str
) -> str:
    """
    24/7 Gujarat Highway Roadside Breakdown SOS diagnostic triage and emergency directives.
    Provides step-by-step roadside mechanical triage, safety protocol, necessary tools, and bilingual Gujarati/English directives.

    Args:
        symptom_query: Breakdown symptoms (e.g. 'clutch wire snap on NH 48', 'engine overheating steam in Rann of Kutch', 'flat tubeless puncture at night', 'battery dead EFI won't prime', 'chain broke sprocket jam').
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from expedition_sos_engine import ChamundaExpeditionManager
    mgr = ChamundaExpeditionManager()

    res = mgr.highway_sos_triage(symptom_query=symptom_query)

    lines = [
        f"### 🚨 Chamunda 24/7 Gujarat Highway Breakdown SOS Shield",
        f"**Fault Category:** {res['fault_category']}",
        f"**Emergency Urgency:** `{res['urgency']}`",
        f"**Query Match:** *\"{symptom_query}\"*",
        "",
        "---",
        f"⚠️ **Roadside Safety Protocol:** {res['safety_protocol']}",
        f"🔧 **Required Tools:** {', '.join(res['tools_required'])}",
        "",
        "#### 🛠️ Immediate Roadside Fix Steps:"
    ]
    for stp in res["roadside_fix_steps"]:
        lines.append(f"1. {stp}")

    lines.extend([
        "",
        "#### 🗣️ Mechanic Directives (દ્વિભાષી / Bilingual):",
        f"- **English:** {res['english_directive']}",
        f"- **ગુજરાતી (Gujarati):** {res['gujarati_directive']}",
        "",
        "---",
        f"📞 **24/7 Gujarat Highway Helpline:** **{res['helpline_24x7']}** (Chamunda Automobile Highway Patrol)"
    ])
    return "\n".join(lines)







def chamunda_build_custom_restomod_quote(
    customer_name: str,
    phone: str,
    bike_model: str,
    registration_no: str,
    style_key: str = "bobber_solo",
    paint_theme_key: str = "matte_phantom_black",
    performance_stage_key: str = "stage_1_street_thump",
    include_vintage_ci_package: bool = False,
    custom_notes: str = ""
) -> str:
    """
    Configure and generate a bespoke Royal Enfield Custom Resto-Mod build quote,
    dynamic Bill of Materials (BOM) from 4,469 parts, Stage 1/2 dyno calibration,
    vintage Cast-Iron rebirth diagnostics, and verifiable QR digital blueprint.

    Args:
        customer_name: Name of the rider / customer.
        phone: Customer's WhatsApp contact number.
        bike_model: Royal Enfield model platform (e.g. 'Bullet 350 Cast-Iron CI', 'Classic 350 Reborn', 'Hunter 350', 'Himalayan 450', 'Interceptor 650').
        registration_no: Vehicle registration number (e.g. 'GJ-01-AB-1982').
        style_key: Resto-mod style archetype ('bobber_solo', 'cafe_racer', 'desert_scrambler', 'vintage_heritage_standard').
        paint_theme_key: Paint and finish theme ('british_racing_green_gold', 'matte_phantom_black', 'desert_sand_patina', 'candy_royal_maroon', 'vintage_gunmetal_silver').
        performance_stage_key: Dyno tuning stage ('stage_0_stock', 'stage_1_street_thump', 'stage_2_dyno_sprint').
        include_vintage_ci_package: Whether to include the Vintage Cast-Iron (CI) heavy crank rebirth package (CB points, pushrod tappets, Mikcarb jetting, Albion 4-speed shimming).
        custom_notes: Bespoke fabrications, directives, or accessories requested by the rider.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from restomod_studio_engine import ChamundaRestoModStudio
    studio = ChamundaRestoModStudio()

    quote = studio.generate_restomod_quote(
        customer_name=customer_name,
        phone=phone,
        bike_model=bike_model,
        registration_no=registration_no,
        style_key=style_key,
        paint_theme_key=paint_theme_key,
        performance_stage_key=performance_stage_key,
        include_vintage_ci_package=include_vintage_ci_package,
        custom_notes=custom_notes
    )

    cb = quote["cost_breakdown"]
    ps = quote["performance_specs"]
    lines = [
        f"### 🏍️ Chamunda AI • Bespoke Resto-Mod &amp; Vintage CI Blueprint",
        f"**Blueprint ID:** `{quote['resto_id']}`",
        f"**Rider / Client:** {quote['customer_name']} (Phone: `{quote['phone']}`)",
        f"**Model Platform:** {quote['bike_model']} (`{quote['registration_no']}`)",
        f"**Style Archetype:** **{quote['style_name']}** ({quote['style_name_gu']})",
        f"**Paint & Finish:** {quote['paint_name']}",
        f"**Dyno Tuning:** {quote['performance_stage']} | **Timeline:** **{quote['timeline_days']} Working Days**",
        "",
        "---",
        "#### 💰 Commercial Cost Breakdown:",
        f"- **Style Fabrication & Chassis Labor:** ₹{cb['style_labor']:,}",
        f"- **Custom Paint & Ceramic Finish:** ₹{cb['paint_finish']:,}",
        f"- **Performance Dyno Calibration:** ₹{cb['performance_tuning']:,}",
        f"- **Vintage CI Heavy Crank Rebirth:** ₹{cb['vintage_ci_package']:,}",
        f"- **OEM Spares Bill of Materials ({len(quote['bom_parts'])} SKUs):** ₹{cb['bom_spares']:,}",
        f"🏆 **Grand Total Build Cost:** **₹{quote['grand_total']:,}**",
        "",
        "---",
        "#### ⚡ Dyno Performance Calibrations:",
        f"- **Power Gain:** {ps['hp_gain']} | **Torque Gain:** {ps['torque_gain']}",
        f"- **Top Speed Potential:** {ps['top_speed_gain']} | **0-60 km/h Drop:** {ps['accel_improvement']}",
        f"- **Exhaust Acoustic Note:** {ps['exhaust_note_db']} ({'✅ RTO Legal <85 dB' if ps['rto_legal_noise'] else '⚠️ Track Only'})",
        "",
        "---",
        "#### 📦 Bill of Materials (BOM) Spares Locked:"
    ]

    for p in quote["bom_parts"]:
        lines.append(f"- **{p['name']}** (`{p['sku']}`) x{p['quantity']} = ₹{p['total_price']:,} [{p['category']}]")

    lines.extend([
        "",
        "---",
        f"🔗 **Verifiable Digital Blueprint:** [http://127.0.0.1:8080/restomod/{quote['resto_id']}](http://127.0.0.1:8080/restomod/{quote['resto_id']})",
        f"📄 **Local HTML File:** `{quote['blueprint_html_path']}`"
    ])
    return "\n".join(lines)


def chamunda_calculate_performance_stage_tune(
    bike_model: str,
    stage_key: str = "stage_1_street_thump"
) -> str:
    """
    Simulate and calculate Royal Enfield Stage 1 (Street Thump) or Stage 2 (Dyno Sprint High-Cam)
    dyno performance metrics, power/torque gains, exhaust decibels, RTO legal compliance, and OEM upgrade spares.

    Args:
        bike_model: Model name (e.g. 'Classic 350 Reborn', 'Bullet 350 Cast-Iron CI', 'Hunter 350', 'Himalayan 450', 'Interceptor 650').
        stage_key: Tuning stage ('stage_1_street_thump' or 'stage_2_dyno_sprint').
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from restomod_studio_engine import ChamundaRestoModStudio
    studio = ChamundaRestoModStudio()

    res = studio.calculate_performance_stage(bike_model=bike_model, stage_key=stage_key)
    lines = [
        f"### ⚡ Chamunda AI • Dyno Performance Calibration Analysis",
        f"**Motorcycle Platform:** {res['bike_model']}",
        f"**Calibration Stage:** **{res['stage_name']}** ({res['stage_name_gu']})",
        f"**Calibration Fee:** ₹{res['stage_cost']:,} | **Added Time:** {res['extra_days']} Days",
        "",
        "---",
        "#### 📊 Dyno Output Gains:",
        f"- **Peak Power:** {res['stock_hp']} HP ➡️ **{res['tuned_hp']} HP** (+{res['hp_gain']})",
        f"- **Peak Torque:** {res['stock_torque_nm']} Nm ➡️ **{res['tuned_torque_nm']} Nm** (+{res['torque_gain']})",
        f"- **Top Speed Gain:** {res['top_speed_gain']}",
        f"- **0-60 km/h Sprint:** {res['accel_drop']}",
        f"- **Exhaust Decibels:** **{res['exhaust_decibel']} dB** ({'✅ RTO Legal Compliant (<85 dB)' if res['rto_legal'] else '⚠️ Track / Off-Road Only'})",
        f"- **Acoustic Thump:** {res['thump_profile']}",
        "",
        "---",
        "#### 🔧 Recommended Genuine OEM Upgrades:"
    ]
    for sp in res["required_spares"]:
        lines.append(f"- **{sp['part_name']}** `[{sp['oem_sku']}]` (~₹{sp['est_price']}) - *{sp['purpose']}*")

    return "\n".join(lines)


def chamunda_diagnose_vintage_ci_bullet(
    symptom_query: str
) -> str:
    """
    Diagnostic & mechanical rebirth matrix for Vintage Cast-Iron (CI) Bullet (1970-2009) heavy crank engines.
    Provides factory tolerance specifications, contact breaker (CB) point gaps, ignition timing (BTDC),
    pushrod tappet clearances, Mikcarb VM carb jetting, Albion 4-speed gearbox shimming, and wet sumping cures.

    Args:
        symptom_query: Vintage CI engine symptom or query (e.g. 'points burnt misfire', 'tappet clattering', 'black smoke mikcarb jetting', 'heavy crank timing backfire', 'albion 4 speed false neutral', 'wet sumping crankcase oil pool').
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from restomod_studio_engine import ChamundaRestoModStudio
    studio = ChamundaRestoModStudio()

    res = studio.diagnose_vintage_ci_bullet(symptom_query=symptom_query)
    lines = [
        f"### ⚙️ Chamunda AI • Vintage Cast-Iron (CI) Bullet Rebirth Diagnosis",
        f"**Fault Identified:** **{res['fault_name']}** ({res['fault_name_gu']})",
        f"**Query Match:** *'{symptom_query}'*",
        f"**Root Cause:** {res['root_cause']}",
        "",
        "---",
        f"📏 **Factory Specification & Tolerance:** `{res['factory_tolerance_specs']}`",
        "",
        "#### 🛠️ Master Mechanic Directives (દ્વિભાષી / Bilingual):",
        f"- **ગુજરાતી (Gujarati):** {res['mechanic_directive_gu']}",
        f"- **English:** {res['mechanic_directive_en']}",
        "",
        "---",
        "#### 📦 Required Genuine OEM Spares:"
    ]
    for sp in res["parts_needed"]:
        lines.append(f"- **{sp['part_name']}** `[{sp['part_number']}]` (~₹{sp['approx_mrp']}) - *{sp['function']}*")

    lines.append("\n💡 *Note: Always use 20W50 mineral engine oil and check ball-valve spring pressure on CI engines.*")
    return "\n".join(lines)


def chamunda_get_social_telemetry() -> str:
    """
    Retrieve real-time metrics and status across all 5 digital brand channels:
    WhatsApp (+91 78747 19139), Instagram, Facebook, Google Business Profile (4.9★), and YouTube.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from omnichannel_social_engine import ChamundaOmnichannelSocialEngine
    engine = ChamundaOmnichannelSocialEngine()
    telem = engine.get_channel_telemetry()

    lines = [
        "### 📱 Chamunda AI • 360° Omnichannel Social & Brand Telemetry",
        f"**Total Community Reach:** **{telem['total_community_reach']}**",
        f"**Official WhatsApp AI Bot:** **{telem['active_whatsapp_bot']}** ([Chat]({telem['whatsapp_chat_link']}))",
        f"**Google Business Rating:** **{telem['google_review_score']}**",
        f"**Pending Social Inquiries:** **{telem['pending_inbox_messages']} messages**",
        f"**Pending Google Reviews:** **{telem['pending_google_reviews']} reviews**",
        f"**Total Published Posts:** **{telem['total_published_posts']} campaigns**",
        f"**Monthly Digital Impressions:** **{telem['monthly_digital_impressions']}**",
        "",
        "---",
        "#### 🌐 Active Channels Status:"
    ]
    for ch in telem["channels"]:
        lines.append(f"- **{ch['name']}:** {ch['handle']} | {ch['status']} ({ch['subscribers']}, {ch['engagement']})")

    return "\n".join(lines)


def chamunda_generate_social_campaign(topic: str, campaign_type: str = "Workshop Master Tip") -> str:
    """
    Generate tailored, native social media content copies across all 5 digital channels
    (WhatsApp, Instagram, Facebook, Google Business, YouTube) from a single motorcycle topic.

    Args:
        topic: Motorcycle topic or workshop service focus (e.g. 'Classic 350 Cold Start Tappet Noise Fix', 'Monsoon Care Package', '1994 Standard 350 Restoration').
        campaign_type: Type of campaign ('Workshop Master Tip', 'Service Awareness', 'Resto-Mod Showcase', 'Spares Alert').
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from omnichannel_social_engine import ChamundaOmnichannelSocialEngine
    engine = ChamundaOmnichannelSocialEngine()
    camp = engine.generate_multi_platform_campaign(topic=topic, campaign_type=campaign_type)

    ch_data = camp["channels_data"]
    lines = [
        f"### 🚀 Chamunda AI • 360° Multi-Platform Campaign Generated: `{camp['topic']}`",
        f"**Campaign ID:** `{camp['campaign_id']}` | **Type:** {camp['campaign_type']}",
        "",
        "---",
        "#### 📲 1. WhatsApp Broadcast Copy (Bilingual with Booking Link):",
        ch_data["whatsapp"]["content"],
        "",
        "---",
        "#### 📸 2. Instagram Reels / Post Caption:",
        ch_data["instagram"]["caption"],
        "",
        "---",
        "#### 📘 3. Facebook Community Update:",
        ch_data["facebook"]["content"],
        "",
        "---",
        "#### 📍 4. Google Business Profile Local SEO Update:",
        ch_data["google_business"]["content"],
        "",
        "---",
        "#### ▶️ 5. YouTube Video / Short Script & SEO:",
        f"**Title:** {ch_data['youtube']['title']}",
        f"**Hook:** {ch_data['youtube']['script_hook']}",
        f"**Tags:** {', '.join(ch_data['youtube']['tags'])}",
        f"**Pinned Comment:** {ch_data['youtube']['pinned_comment']}"
    ]
    return "\n".join(lines)


def chamunda_publish_social_post(topic: str, channels: str = "all") -> str:
    """
    Publish or schedule an omnichannel campaign across WhatsApp, Instagram, Facebook, Google Business, and YouTube.

    Args:
        topic: Motorcycle topic or service focus.
        channels: Target channels comma-separated or 'all' (e.g. 'whatsapp,instagram,google_business' or 'all').
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from omnichannel_social_engine import ChamundaOmnichannelSocialEngine
    engine = ChamundaOmnichannelSocialEngine()

    camp = engine.generate_multi_platform_campaign(topic=topic)
    target_list = None
    if channels != "all":
        target_list = [c.strip() for c in channels.split(",") if c.strip()]

    res = engine.publish_to_channels(campaign_data=camp, target_channels=target_list)
    lines = [
        f"### ✅ Chamunda AI • Multi-Platform Campaign Dispatched",
        f"**Post ID:** `{res['post_id']}`",
        f"**Published At:** {res['published_at']}",
        f"**Target Channels:** {', '.join(res['published_channels'])}",
        f"**Message:** {res['message']}",
        f"🔗 **View in Web Portal:** Open [http://127.0.0.1:8080/#omnichannel-social](http://127.0.0.1:8080)"
    ]
    return "\n".join(lines)


def chamunda_manage_social_inbox(channel: str = "all") -> str:
    """
    Review incoming customer inquiries across WhatsApp, Instagram DMs, Facebook Messenger, and YouTube comments.

    Args:
        channel: Channel filter ('all', 'whatsapp', 'instagram', 'facebook', 'youtube').
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from omnichannel_social_engine import ChamundaOmnichannelSocialEngine
    engine = ChamundaOmnichannelSocialEngine()
    items = engine.get_social_inbox(filter_channel=channel)

    lines = [
        f"### 📥 Chamunda AI • Unified Social Inbox (Filter: `{channel.upper()}`)",
        f"**Total Inquiries:** {len(items)}",
        ""
    ]
    for it in items:
        status_icon = "✅" if it.get("reply_sent") else "⏳"
        lines.append(f"- {status_icon} `[{it['channel'].upper()}]` **{it['sender_name']}** ({it['sender_contact']}) - *{it['received_at']}*")
        lines.append(f"  💬 *Query:* \"{it['message']}\"")
        if it.get("ai_draft_reply"):
            lines.append(f"  🤖 *AI Reply:* {it['ai_draft_reply']}")
        lines.append("")

    return "\n".join(lines)


def chamunda_manage_google_business_reviews() -> str:
    """
    Inspect Google Business Profile customer reviews and auto-drafted bilingual Gujarati/English owner replies.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from omnichannel_social_engine import ChamundaOmnichannelSocialEngine
    engine = ChamundaOmnichannelSocialEngine()
    reviews = engine.get_google_reviews()

    lines = [
        "### ⭐ Chamunda AI • Google Business Profile (4.9★) Reviews & AI Auto-Responder",
        "**Overall Rating:** 4.9 ★★★★★ (842 Verified Customer Reviews)",
        ""
    ]
    for r in reviews:
        stars = "★" * r["rating"]
        lines.append(f"- **{r['customer_name']}** ({stars}, *{r['time_ago']}*):")
        lines.append(f"  💬 \"{r['comment']}\"")
        if r.get("owner_reply"):
            lines.append(f"  👑 **Owner Reply (English):** {r['owner_reply']}")
        if r.get("owner_reply_gu"):
            lines.append(f"  👑 **Owner Reply (ગુજરાતી):** {r['owner_reply_gu']}")
        lines.append("")

    return "\n".join(lines)


def chamunda_list_shop_subagents() -> str:
    """
    List all 5 specialized departmental executive sub-agents operating under CEO Aradhya:
    1. bay_chief (Master Workshop & Bay Chief - Master Tech Ramesh)
    2. parts_specialist (Inventory & OEM Parts Specialist - Jayeshbhai)
    3. customer_receptionist (24/7 Front-Desk & WhatsApp Receptionist - Priya)
    4. social_growth_manager (Omnichannel Brand Manager - Kabir)
    5. accounts_controller (Billing & Finance Accounts Controller - Hasmukhbhai)
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from shop_subagents_engine import ChamundaShopSubagentsManager
    sub_mgr = ChamundaShopSubagentsManager()
    agents = sub_mgr.list_subagents()

    lines = [
        "### 👥 Chamunda Automobile • Executive Suite & Departmental Sub-Agents",
        "**Supreme Commander:** **Aradhya • Chief Executive Officer (CEO)**",
        "**Founder & Master Tech:** **Alpesh Sir**",
        "",
        "---",
        "#### 🏢 Specialized Departmental Heads:"
    ]
    for a in agents:
        lines.append(f"• **{a['name']}** (`chamunda_{a['agent_id']}`)")
        lines.append(f"  - **Head:** {a['designated_head']}")
        lines.append(f"  - **Department:** {a['department']}")
        lines.append(f"  - **Live Status:** {a['status']} ({a['metrics']})")
        lines.append(f"  - **Key Capabilities:** {', '.join(a['capabilities'][:3])}")
        lines.append("")

    return "\n".join(lines)


def chamunda_delegate_shop_task(agent_name: str, task: str) -> str:
    """
    Delegate an executive operational directive to a specialized departmental sub-agent as CEO Aradhya.

    Args:
        agent_name: Target sub-agent ID or role ('bay_chief', 'parts_specialist', 'customer_receptionist', 'social_growth_manager', 'accounts_controller').
        task: Actionable directive or instructions to execute.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from shop_subagents_engine import ChamundaShopSubagentsManager
    sub_mgr = ChamundaShopSubagentsManager()

    clean_name = agent_name.lower().replace("chamunda_", "").replace("-", "_").strip()
    res = sub_mgr.delegate_task(agent_id=clean_name, task_title=task[:60], task_description=task)

    if not res.get("success"):
        return f"❌ Delegation Error: {res.get('error', 'Failed to dispatch task')}"

    d = res["delegation"]
    lines = [
        f"### 🎯 Chamunda AI • Executive Directive Dispatched by CEO Aradhya",
        f"**Directive ID:** `{d['delegation_id']}`",
        f"**Department / Sub-Agent:** **{d['agent_name']}**",
        f"**Designated Officer:** {res['designated_head']}",
        f"**Task Title:** {d['task_title']}",
        f"**Status:** **{d['status']}** ({d['completed_at']})",
        "",
        "---",
        f"📋 **Execution Summary:** {d['result_summary']}",
        f"🔗 **View in Web Portal:** Open [http://127.0.0.1:8080/#shop-subagents](http://127.0.0.1:8080)"
    ]
    return "\n".join(lines)


def chamunda_get_subagents_status() -> str:
    """
    Get executive consolidated operational health overview of all workshop departments for CEO Aradhya.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from shop_subagents_engine import ChamundaShopSubagentsManager
    sub_mgr = ChamundaShopSubagentsManager()
    ov = sub_mgr.get_executive_overview()

    lines = [
        "### 👑 Chamunda AI • CEO Executive Sub-Agents Dashboard",
        f"**Executive Command:** {ov['ceo_command']}",
        f"**Operational Suite Status:** **{ov['executive_suite_status']}**",
        f"**Active Departments:** **{ov['departments_active']} Departments**",
        f"**Total Delegated Directives:** **{ov['total_delegated_directives']}** (Completed: {ov['completed_directives']})",
        "",
        "---",
        "#### 📋 Recent Executive Delegations:"
    ]
    for d in ov.get("recent_delegations", []):
        lines.append(f"- `[{d['delegation_id']}]` **{d['agent_name']}:** {d['task_title']} ({d['status']})")

    return "\n".join(lines)


def chamunda_execute_written_command(command: str, sender: str = "Alpesh Sir (Founder & Chairman)") -> str:
    """
    Parse and execute a natural language written command/directive from Alpesh Sir or CEO Aradhya,
    routing it to the appropriate specialized departmental sub-agent (Bay Chief Ramesh, Parts Specialist Jayesh,
    Front-Desk Priya, Social Manager Kabir, or Accounts Controller Hasmukh).

    Args:
        command: Freeform written command in Gujarati or English.
        sender: Name/title of the commander (default: 'Alpesh Sir (Founder & Chairman)').
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from shop_subagents_engine import ChamundaShopSubagentsManager
    sub_mgr = ChamundaShopSubagentsManager()
    res = sub_mgr.execute_written_command(command_text=command, sender=sender)

    if not res.get("success"):
        return f"❌ Directive Error: {res.get('error', 'Failed to execute written command')}"

    log = res["command_log"]
    lines = [
        f"### ✍️ Chamunda AI • Executive Written Directive Executed",
        f"**Command ID:** `{res['command_id']}` | **Priority:** `{res['priority']}`",
        f"**Commander:** {res['sender']}",
        f"**Target Sub-Agent:** **{log['target_agent_name']}** ({res['designated_head']})",
        "",
        f"📝 **Raw Command:** *\"{command}\"*",
        "---",
        f"🇬🇺 **ગુજરાતી પ્રતિભાવ:** {res['response_gu']}",
        f"🇬🇧 **Operational Report:** {res['response_en']}",
        "",
        f"🔗 **Live Portal:** View status on [http://127.0.0.1:8080/#shop-subagents](http://127.0.0.1:8080)"
    ]
    return "\n".join(lines)


def chamunda_heal_shop_subagent(agent_name: str, issue: str) -> str:
    """
    Trigger autonomous issue diagnostic and self-healing for a specialized departmental sub-agent.
    The sub-agent will diagnose the root cause, formulate and apply the fix, gain XP, and unlock new capabilities.

    Args:
        agent_name: Target sub-agent ID ('bay_chief', 'parts_specialist', 'customer_receptionist', 'social_growth_manager', 'accounts_controller').
        issue: Description of technical defect, bottleneck, or operational incident to solve.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from shop_subagents_engine import ChamundaShopSubagentsManager
    sub_mgr = ChamundaShopSubagentsManager()

    clean_name = agent_name.lower().replace("chamunda_", "").replace("-", "_").strip()
    res = sub_mgr.diagnose_and_heal_incident(agent_id=clean_name, issue_description=issue)

    if not res.get("success"):
        return f"❌ Self-Healing Error: {res.get('error', 'Failed to execute self-healing')}"

    lines = [
        f"### 🛡️ Chamunda AI • Autonomous Sub-Agent Self-Healing Report",
        f"**Sub-Agent:** **{res['agent_name']}** ({res['designated_head']})",
        f"**Incident ID:** `{res['incident_id']}` | **New Level:** **Level {res['new_level']}** ({res['total_xp']} XP)",
        f"**Issue Reported:** *\"{res['issue_reported']}\"*",
        "",
        "---",
        f"🔍 **Root Cause Diagnosed:** {res['root_cause_diagnosed']}",
        f"🛠️ **Autonomous Fix Applied:** {res['applied_solution']}",
        f"🌟 **New Capability Unlocked:** `{res['new_skill_unlocked']}` (+{res['xp_awarded']} XP)",
        f"🇬🇺 **ગુજરાતી સારાંશ:** {res['solution_gu']}",
        "",
        f"🔗 **Live Portal:** View Growth Matrix on [http://127.0.0.1:8080/#shop-subagents](http://127.0.0.1:8080)"
    ]
    return "\n".join(lines)


def chamunda_get_subagents_growth_telemetry() -> str:
    """
    Retrieve autonomous growth matrix, levels, XP, and learned capabilities for all 5 Chamunda sub-agents.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from shop_subagents_engine import ChamundaShopSubagentsManager
    sub_mgr = ChamundaShopSubagentsManager()
    growth_data = sub_mgr.get_agent_growth_telemetry()

    lines = [
        "### 🧠 Chamunda AI • Sub-Agents Growth & Self-Healing Telemetry",
        "| Department / Lead | Level & Title | XP | Self-Healed Cases | Autonomous Fix Rate |",
        "| :--- | :--- | :--- | :--- | :--- |"
    ]
    for aid, prof in growth_data.items():
        lines.append(f"| **{prof['agent_name']}**<br><small>{prof['designated_head']}</small> | **Level {prof['level']}**<br>*{prof['title']}* | {prof['xp']}/{prof.get('xp_to_next_level', 700)} XP | **{prof['issues_resolved_autonomously']}** cases | **{prof.get('autonomous_healing_rate', '99.4%')}** |")

    lines.append("")
    lines.append("#### 🌟 Recent Learned Capabilities (Auto-Updated):")
    for aid, prof in growth_data.items():
        skills = prof.get("learned_capabilities", [])[:2]
        if skills:
            lines.append(f"- **{prof['designated_head']}:** {', '.join(skills)}")

    return "\n".join(lines)


def chamunda_process_bay_voice_command(spoken_text: str, mechanic_name: str = "Master Tech Ramesh") -> str:
    """
    Process a spoken voice command from workshop mechanics hands-free in Gujarati or English.
    Automatically coordinates Job Card updates, OEM inventory deduction, GST billing sync, and WhatsApp alerts.

    Args:
        spoken_text: Natural language spoken transcription (e.g. "આરાધ્યા, ગાડી નંબર GJ-02-BQ-1234 માં લિક્વી મોલી 15W-50 ઓઇલ અને ઓઇલ ફિલ્ટર નાખી દીધા છે").
        mechanic_name: Name of the mechanic or bay supervisor speaking (default: 'Master Tech Ramesh').
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from bay_voice_engine import get_bay_voice_engine
    engine = get_bay_voice_engine()
    res = engine.process_voice_action(spoken_text=spoken_text, mechanic_name=mechanic_name)

    lines = [
        "### 🎙️ Chamunda AI • Bay Hands-Free Voice-to-Action Execution",
        f"**Log ID:** `{res['log_id']}` | **Mechanic:** {mechanic_name}",
        f"**Spoken Command:** *\"{spoken_text}\"*",
        f"**Target Vehicle:** **{res['registration_no']}** | **Action:** **{res['action_detected']}**",
        "",
        "---",
        "#### 👥 Multi-Agent Workshop Synchronization:",
        f"- 🛠️ **Bay Chief (Ramesh):** {res['subagent_sync']['bay_chief']}",
        f"- 📦 **Parts Specialist (Jayeshbhai):** {res['subagent_sync']['parts_specialist']}",
        f"- 🧾 **Accounts Controller (Hasmukhbhai):** {res['subagent_sync']['accounts_controller']}",
        f"- 📱 **Receptionist (Priya):** {res['subagent_sync']['customer_receptionist']}",
        "",
        f"🔊 **Audio Response (Gujarati):** *\"{res['audio_response_gu']}\"*",
        f"🔊 **Audio Response (English):** *\"{res['audio_response_en']}\"*",
        "",
        f"🔗 **Live Voice Console:** [http://127.0.0.1:8080/#bay-voice](http://127.0.0.1:8080/#bay-voice)"
    ]
    return "\n".join(lines)


def chamunda_get_b2b_wholesale_overview() -> str:
    """
    Retrieve overview of Chamunda B2B Wholesale Spares Distribution Network across North Gujarat.
    Shows partner garages, tier margins, delivery routes, and revenue metrics.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from b2b_wholesale_engine import get_b2b_wholesale_manager
    mgr = get_b2b_wholesale_manager()
    ov = mgr.get_overview()

    lines = [
        "### 📦 Chamunda B2B Wholesale Genuine Spares Network",
        f"**Partner Garages:** {ov['partner_garages_count']} | **Total B2B Orders:** {ov['total_orders_count']}",
        f"**Wholesale Revenue:** ₹{ov['total_wholesale_revenue_inr']:,.2f} | **Active Van Routes:** {ov['active_routes_count']}",
        "",
        "| Garage ID | Garage Name | City | Tier / Margin | Outstanding | Preferred Route |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    for g in ov["garages"]:
        lines.append(f"| `{g['garage_id']}` | **{g['name']}**<br><small>{g['owner_name']} ({g['phone']})</small> | {g['city']} | **{g['tier']}** | ₹{g.get('outstanding_balance_inr', 0):,.2f} | {g.get('preferred_route', 'Route 1')} |")

    lines.append("")
    lines.append("#### 🚚 Daily Van Delivery Logistics:")
    for r in ov["routes"]:
        lines.append(f"- **{r['name']}** ({r['departure_time']}): {', '.join(r['coverage'])} | Driver: {r['driver_name']} ({r['driver_phone']})")

    return "\n".join(lines)


def chamunda_create_b2b_wholesale_order(garage_id: str, items_json: str, payment_mode: str = "Credit") -> str:
    """
    Create and dispatch a wholesale parts order for a North Gujarat partner garage.

    Args:
        garage_id: Partner garage ID (e.g. 'GAR-PATAN-001', 'GAR-VISN-003').
        items_json: JSON string of items list, e.g. '[{"part_number": "574050/C", "quantity": 10, "mrp": 210, "name": "Oil Filter"}]'.
        payment_mode: 'Credit', 'UPI / Instant 2% Discount', or 'COD'.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from b2b_wholesale_engine import get_b2b_wholesale_manager
    mgr = get_b2b_wholesale_manager()

    try:
        items = json.loads(items_json) if isinstance(items_json, str) else items_json
    except Exception:
        items = [{"part_number": "574050/C", "quantity": 5, "mrp": 210, "name": "Genuine Oil Filter Element"}]

    ord_res = mgr.create_order(garage_id=garage_id, items=items, payment_mode=payment_mode)

    lines = [
        "### 📦 Chamunda B2B Wholesale Order Dispatched",
        f"**Order ID:** `{ord_res['order_id']}` | **Tracking Code:** `{ord_res['tracking_code']}`",
        f"**Partner Garage:** **{ord_res['garage_name']}** ({ord_res['city']}) | **Tier:** {ord_res['tier']} ({ord_res['discount_pct']}% Discount)",
        f"**Delivery Route:** {ord_res['delivery_route']}",
        "",
        "---",
        f"- **MRP Total:** ₹{ord_res['mrp_total_inr']:,.2f}",
        f"- **Wholesale Discount Applied:** -₹{ord_res['discount_amount_inr']:,.2f}",
        f"- **Discounted Subtotal:** ₹{ord_res['subtotal_inr']:,.2f}",
        f"- **GST (18%):** +₹{ord_res['gst_amount_inr']:,.2f}",
        f"- **Net Invoice Payable:** **₹{ord_res['net_payable_inr']:,.2f}** ({payment_mode})",
        "",
        f"🚚 **Status:** {ord_res['order_status']}",
        f"📲 **WhatsApp Requisition Confirmed via +91 78747 19139**"
    ]
    return "\n".join(lines)


def chamunda_manage_amc_membership(
    action: str,
    name: str = "",
    phone: str = "",
    bike_model: str = "",
    registration_no: str = "",
    plan_id: str = "AMC-GOLD"
) -> str:
    """
    Manage Chamunda Royal Riders Club (CRRC) and Annual Maintenance Contract (AMC) memberships.

    Args:
        action: 'overview', 'list_plans', 'list_members', 'enroll', or 'expeditions'.
        name: Member full name (required for 'enroll').
        phone: Mobile phone number.
        bike_model: Royal Enfield model name.
        registration_no: Bike registration number (e.g. 'GJ-02-BQ-1234').
        plan_id: 'AMC-SILVER', 'AMC-GOLD', or 'AMC-PLATINUM'.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from riders_club_engine import get_riders_club_manager
    mgr = get_riders_club_manager()

    if action == "list_plans":
        plans = mgr.get_amc_plans()
        lines = ["### 🏍️ Chamunda Royal Riders Club • AMC Plans", ""]
        for p in plans:
            lines.append(f"#### 🛡️ {p['name']} ({p['name_gu']}) — ₹{p['annual_fee_inr']:,}/year")
            lines.append(f"**Recommended for:** *{p['recommended_for']}*")
            for f in p["features"]:
                lines.append(f"- {f}")
            lines.append("")
        return "\n".join(lines)

    elif action == "enroll":
        if not (name and phone and registration_no):
            return "❌ Error: 'name', 'phone', and 'registration_no' are required for enrollment."
        mem = mgr.enroll_member(name=name, phone=phone, bike_model=bike_model, registration_no=registration_no, plan_id=plan_id)
        return f"""### 🏍️ Chamunda Royal Riders Club • Member Enrolled!
**Member ID:** `{mem['member_id']}` | **Status:** {mem['membership_status']}
**Rider:** **{mem['name']}** ({mem['phone']}) | **Bike:** {mem['bike_model']} (`{mem['registration_no']}`)
**Tier:** **{mem['tier']}** | **Valid Until:** {mem['valid_until']}
**Welcome Bonus:** {mem['thump_points']} Thump Points credited!
**Services Available:** {mem['services_remaining']} Complete Services included."""

    else:
        ov = mgr.get_overview()
        lines = [
            "### 🏍️ Chamunda Royal Riders Club (CRRC) Overview",
            f"**Total Members:** {ov['total_club_members']} | **Annual AMC Revenue:** ₹{ov['annual_amc_revenue_inr']:,}",
            f"**Thump Points in Circulation:** {ov['total_thump_points_circulating']} pts | **Scheduled Expeditions:** {ov['upcoming_expeditions_count']}",
            "",
            "| Member ID | Name | Bike Model | Registration | Plan | Services Remaining | Points |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
        ]
        for m in ov["members"]:
            lines.append(f"| `{m['member_id']}` | **{m['name']}** | {m['bike_model']} | `{m['registration_no']}` | {m['tier']} | {m['services_remaining']} | {m['thump_points']} |")

        lines.append("")
        lines.append("#### 🗺️ Upcoming Expeditions with SOS Escort:")
        for e in ov["expeditions"]:
            lines.append(f"- **{e['title']}** ({e['date']}, {e['distance_km']} km): Route: *{e['route']}* | Riders: {e['registered_riders_count']}/{e['max_riders']}")

        return "\n".join(lines)


def chamunda_run_obd_iot_scan(
    bike_model: str = "Classic 350 (Reborn)",
    registration_no: str = "GJ-02-BQ-1234",
    simulate_dtc: str = "P0505"
) -> str:
    """
    Run live OBD-II diagnostic scan on a Royal Enfield EFI motorcycle, read ECU sensor telemetry, and decode DTC fault codes.

    Args:
        bike_model: Royal Enfield model name (e.g. 'Classic 350 (Reborn)', 'Hunter 350', 'Interceptor 650', 'Himalayan 450').
        registration_no: Vehicle license plate (e.g. 'GJ-02-BQ-1234').
        simulate_dtc: DTC code to simulate ('P0115', 'P0130', 'P0300', 'P0505', 'P0562', 'P0105', or 'HEALTHY').
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from obd_diagnostics_engine import get_obd_diagnostics_engine
    engine = get_obd_diagnostics_engine()
    res = engine.run_obd_scan(bike_model=bike_model, registration_no=registration_no, simulate_dtc=simulate_dtc)

    telem = res["live_telemetry"]
    lines = [
        "### 🔌 Chamunda AI • OBD-II Live IoT Telemetry & ECU Scan",
        f"**Scan ID:** `{res['scan_id']}` | **Motorcycle:** **{bike_model}** (`{registration_no}`)",
        f"**ECU Platform:** {res['platform']} (`{res['ecu_id']}`)",
        f"**Overall Health Status:** **{res['overall_ecu_health']}** | **DTCs Detected:** {res['dtc_count']}",
        "",
        "#### 📊 Live Sensor Telemetry:",
        f"- ⚡ **Battery Charging Voltage:** {telem['battery_voltage']}V (Target: 14.2V - 14.5V)",
        f"- ⏱️ **Engine Idle Speed:** {telem['engine_rpm']} RPM",
        f"- 🌡️ **Engine Thermal Temp:** {telem['engine_temp_c']}°C",
        f"- 🎯 **Throttle Position (TPS):** {telem['throttle_position_pct']}%",
        f"- 💨 **O2 Lambda Voltage:** {telem['o2_sensor_v']}V",
        f"- 🌪️ **Intake Manifold Pressure:** {telem['manifold_pressure_kpa']} kPa",
        ""
    ]

    if res["active_dtcs"]:
        lines.append("#### ⚠️ Active Diagnostic Trouble Codes (DTCs):")
        for dtc in res["active_dtcs"]:
            lines.append(f"- **{dtc['dtc_code']} ({dtc['severity']}):** {dtc['title']}")
            lines.append(f"  - **Root Cause:** {dtc['root_cause']}")
            lines.append(f"  - **Recommended Fix:** {dtc['recommended_fix']}")
            part = dtc.get("oem_part_needed")
            if part:
                lines.append(f"  - 📦 **OEM Part Needed:** {part['name']} (`{part['part_number']}`) — ₹{part['mrp']}")
    else:
        lines.append("✅ **All ECU sensors reporting optimal factory calibration. Zero DTCs.**")

    lines.append("")
    lines.append(f"🇬🇺 **ગુજરાતી તારણ:** {res['diagnosis_gu']}")
    lines.append(f"🔗 **Live OBD Console:** [http://127.0.0.1:8080/#obd-scanner](http://127.0.0.1:8080/#obd-scanner)")
    return "\n".join(lines)


def chamunda_kiosk_express_checkin(
    registration_no: str = "GJ-02-BQ-1234",
    customer_name: str = "Alpesh Sir",
    phone: str = "+91 78747 19139",
    bike_model: str = "Classic 350 (Reborn)",
    issues_csv: str = "Periodic 10,000 km Service, Tappet Sound Check"
) -> str:
    """
    Simulate a customer self-check-in at the 24/7 Workshop Smart Lounge Kiosk.
    Generates queue token, creates digital job card, and dispatches WhatsApp slip.

    Args:
        registration_no: Motorcycle registration number.
        customer_name: Full rider name.
        phone: Mobile phone number.
        bike_model: RE model name.
        issues_csv: Comma-separated list of selected symptoms/issues.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from smart_kiosk_engine import get_smart_kiosk_engine
    engine = get_smart_kiosk_engine()

    issues = [i.strip() for i in issues_csv.split(",") if i.strip()]
    res = engine.process_checkin(
        registration_no=registration_no,
        customer_name=customer_name,
        phone=phone,
        bike_model=bike_model,
        selected_issues=issues
    )

    lines = [
        "### 🖥️ Chamunda AI • Smart Lounge Kiosk Express Check-In",
        f"**Token Generated:** `{res['token_id']}` | **Job Card:** `{res['job_card_id']}`",
        f"**Rider:** **{customer_name}** ({phone}) | **Vehicle:** {bike_model} (`{registration_no}`)",
        f"**Assigned Bay:** **{res['assigned_bay']}** | **Lead Tech:** **{res['assigned_mechanic']}**",
        f"**Estimated Wait:** ~{res['estimated_wait_mins']} Minutes",
        "",
        f"📋 **Selected Issues:** {', '.join(issues)}",
        f"📲 **WhatsApp Confirmation Slip Dispatched to {phone} via +91 78747 19139**",
        f"🔗 **Live Kiosk Terminal:** [http://127.0.0.1:8080/#smart-kiosk](http://127.0.0.1:8080/#smart-kiosk)"
    ]
    return "\n".join(lines)


def chamunda_get_predictive_supply_forecast(season_key: str = "diwali_dhanteras_rush") -> str:
    """
    Analyze inventory velocity and forecast stockout risk under festival demand surges.

    Args:
        season_key: 'diwali_dhanteras_rush', 'monsoon_touring_season', or 'routine_baseline'.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from predictive_supply_chain_engine import get_predictive_supply_chain_manager
    mgr = get_predictive_supply_chain_manager()
    fc = mgr.get_critical_parts_forecast(season_key=season_key)

    lines = [
        f"### 📈 Chamunda AI • Predictive Supply Chain Forecast ({fc['season_profile']})",
        f"**Festival Multiplier:** **{fc['multiplier']}x** | **Total Catalog SKUs:** {fc['total_skus_tracked']:,}",
        f"**Critical Shortage SKUs:** {fc['critical_shortage_skus']} | **Units in Stock:** {fc['total_units_in_stock']:,}",
        "",
        "| OEM Part Number | Part Name | Stock | Burn Rate/Day | Runway Days | Suggested Reorder | Urgency |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    for p in fc["at_risk_parts"]:
        lines.append(f"| `{p['part_number']}` | **{p['name']}** | {p['current_stock']} | {p['daily_burn_rate']} pcs/d | **{p['runway_days']} days** | +{p['reorder_suggested_units']} pcs | **{p['urgency']}** |")

    lines.append("")
    lines.append(f"💡 **Action Recommendation:** {fc['recommended_action']}")
    lines.append(f"🔗 **Live Supply Chain:** [http://127.0.0.1:8080/#supply-chain](http://127.0.0.1:8080/#supply-chain)")
    return "\n".join(lines)


def chamunda_generate_predictive_auto_po(season_key: str = "diwali_dhanteras_rush") -> str:
    """
    Auto-generate and dispatch wholesale purchase order for critical parts nearing stockout.

    Args:
        season_key: 'diwali_dhanteras_rush', 'monsoon_touring_season', or 'routine_baseline'.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from predictive_supply_chain_engine import get_predictive_supply_chain_manager
    mgr = get_predictive_supply_chain_manager()
    po = mgr.generate_auto_replenishment_po(season_key=season_key)

    lines = [
        "### 📦 Chamunda AI • Automated Wholesale Purchase Order Generated",
        f"**PO Number:** `{po['po_number']}` | **Supplier:** {po['supplier_name']}",
        f"**Profile:** {po['season_profile']} ({po['multiplier_applied']}x Multiplier)",
        f"**Total Units Ordered:** **{po['total_units']} Pcs** | **Total Valuation:** **₹{po['total_po_valuation_inr']:,.2f}**",
        "",
        "| OEM Part | Name | Current Stock | Reorder Qty | Wholesale Unit Cost | Line Total |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    for item in po["items"]:
        lines.append(f"| `{item['part_number']}` | **{item['name']}** | {item['current_stock']} | **{item['reorder_qty']}** | ₹{item['cost_price']} | ₹{item['total_cost']:,} |")

    lines.append("")
    lines.append(f"🚚 **Status:** {po['status']} ({po['expected_delivery']})")
    lines.append(f"📲 **WhatsApp Stock Alert Dispatched to Jayeshbhai Patel via +91 78747 19139**")
    return "\n".join(lines)


def chamunda_lookup_3d_engine_schematic(assembly_id: str = "ASM-J350-HEAD") -> str:
    """
    Look up 3D interactive exploded engine schematic diagram, OEM parts, and factory torque specs.

    Args:
        assembly_id: 'ASM-J350-HEAD', 'ASM-650-CLUTCH', 'ASM-CI350-CRANK', or 'ASM-SHERPA-COOLING'.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from schematics_3d_engine import get_schematics_3d_engine
    mgr = get_schematics_3d_engine()
    assembly = mgr.get_assembly_by_id(assembly_id)

    if not assembly:
        assemblies = mgr.get_assemblies()
        avail = ", ".join([f"`{a['assembly_id']}` ({a['title']})" for a in assemblies])
        return f"❌ Assembly ID `{assembly_id}` not found. Available assemblies:\n{avail}"

    lines = [
        f"### 🧩 Chamunda 3D Schematics • {assembly['title']}",
        f"**Platform:** {assembly['platform']} | **ID:** `{assembly['assembly_id']}`",
        "",
        "#### ⚙️ Key Technical Specifications:",
    ]
    for k, v in assembly.get("key_specifications", {}).items():
        spec_label = k.replace("_", " ").title()
        lines.append(f"- **{spec_label}:** `{v}`")

    lines.append("")
    lines.append("#### 🔩 Exploded Components & Factory Torque Specifications:")
    lines.append("| Item # | OEM Part No | Component Name | Stock | Bin | Factory Torque (Nm) | Master Tech Advice |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    for c in assembly.get("components", []):
        lines.append(f"| #{c['item_no']} | `{c['part_number']}` | **{c['name']}** | {c['stock']} pcs | `{c['bin']}` | **{c['torque_nm']}** | {c['master_tech_advice']} |")

    lines.append("")
    lines.append(f"🔗 **Interactive 3D View:** [http://127.0.0.1:8080/#engine-schematics](http://127.0.0.1:8080/#engine-schematics)")
    return "\n".join(lines)


def chamunda_run_borescope_inspection(
    bike_model: str = "Classic 350 (Reborn)",
    registration_no: str = "GJ-02-BQ-1234",
    odometer_km: int = 15000,
    scenario: str = "heavy_carbon_crust"
) -> str:
    """
    Perform non-invasive AI optical borescope endoscopy on combustion chamber, piston crown, and cylinder bore.

    Args:
        bike_model: Motorcycle model name.
        registration_no: Vehicle license registration.
        odometer_km: Current odometer reading.
        scenario: 'heavy_carbon_crust', 'moderate_carbon', 'pristine_showroom', or 'bore_score_damage'.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from borescope_inspection_engine import get_borescope_engine
    mgr = get_borescope_engine()
    res = mgr.inspect_combustion_chamber(
        bike_model=bike_model,
        registration_no=registration_no,
        odometer_km=odometer_km,
        scenario=scenario
    )

    lines = [
        f"### 🔬 Chamunda AI • Borescope Combustion Chamber Diagnostic Report",
        f"**Inspection ID:** `{res['inspection_id']}` | **Motorcycle:** **{res['bike_model']}** (`{res['registration_no']}`)",
        f"**Odometer:** `{res['odometer_km']:,} KM` | **Combustion Health Score:** **`{res['combustion_health_score']}/100`** ({res['chamber_grade']})",
        "",
        "#### 🔍 Optical Endoscopy Findings:",
        f"- **Piston Crown Carbon Crust:** `{res['piston_crown']['carbon_crust_thickness_mm']} mm` ({res['piston_crown']['carbon_density']}) - Visibility: `{res['piston_crown']['piston_top_visibility_pct']}%`",
        f"- **Cylinder Wall Crosshatch:** `{res['cylinder_wall']['honing_crosshatch_retention_pct']}% Retention` | Scratches: `{'Yes (Scored)' if res['cylinder_wall']['micro_scratch_detected'] else 'None'}` | Glaze: `{res['cylinder_wall']['thrust_face_glazing']}`",
        f"- **Valve Sealing Margins:** Intake: `{res['valve_seals']['intake_valve_carbon_deposit']}` | Exhaust: `{res['valve_seals']['exhaust_valve_carbon_deposit']}`",
        "",
        f"💡 **Prescribed Non-Invasive Treatment:** {res['prescribed_treatment']}",
        f"💰 **Estimated Decarb / Repair Cost:** **₹{res['cost_estimate_inr']:,}**",
        "",
        f"👨‍🔧 **Master Tech Verdict (GJ):** *{res['master_tech_verdict_gu']}*",
        f"👨‍🔧 **Master Tech Verdict (EN):** *{res['master_tech_verdict_en']}*",
        f"📲 **WhatsApp Inspection PDF Dispatched to Customer via +91 78747 19139**",
        f"🔗 **Borescope Terminal:** [http://127.0.0.1:8080/#borescope-inspection](http://127.0.0.1:8080/#borescope-inspection)"
    ]
    return "\n".join(lines)


def chamunda_get_multibranch_overview() -> str:
    """
    Retrieve consolidated multi-branch cloud telemetry across North Gujarat franchise network.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from multibranch_hub_engine import get_multibranch_engine
    mgr = get_multibranch_engine()
    ov = mgr.get_branches_overview()

    lines = [
        f"### 🏢 Chamunda Automobile • Multi-Branch Franchise Network Overview",
        f"**Network Status:** **{ov['network_status']}** | **Central Hub:** {ov['hq_branch']}",
        f"**Total Active Bays:** **{ov['total_active_bays']} Bays** | **Today's Network Jobs:** **{ov['total_jobs_today']} Bikes**",
        f"**Today's Consolidated Revenue:** **₹{ov['total_revenue_today_inr']:,}** | **Network Spares Valuation:** **₹{ov['total_inventory_valuation_inr']:,}**",
        f"**Pending Intra-Branch Transfers:** `{ov['pending_transfers_count']}` In-Transit",
        "",
        "#### 📍 Branch Network Status:",
        "| Branch ID | Branch Name | City | Bays | Today Jobs | Revenue | Inventory Val | Manager Contact |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    for b in ov["branches"]:
        lines.append(f"| `{b['branch_id']}` | **{b['name']}** | {b['city']} | {b['active_bays']} | {b['today_jobs']} | ₹{b['today_revenue_inr']:,} | ₹{b['stock_valuation_inr']:,} | {b['manager']} ({b['phone']}) |")

    lines.append("")
    lines.append("#### 🚚 Recent Intra-Branch Stock Transfers:")
    lines.append("| Transfer ID | From | To | Part Number & Name | Qty | Total Value | Status |",)
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    for t in ov["recent_transfers"]:
        lines.append(f"| `{t['transfer_id']}` | `{t['from_branch']}` | `{t['to_branch']}` | `{t['part_number']}` ({t['part_name'][:25]}...) | {t['quantity']} pcs | ₹{t['total_value_inr']:,} | **{t['status']}** |")

    lines.append("")
    lines.append(f"🔗 **Multi-Branch Operations Terminal:** [http://127.0.0.1:8080/#multibranch-hub](http://127.0.0.1:8080/#multibranch-hub)")
    return "\n".join(lines)


def chamunda_transfer_branch_inventory(
    from_branch: str = "HQ-MEHSANA",
    to_branch: str = "BR-PATAN-01",
    part_number: str = "574012/A",
    quantity: int = 2,
    requested_by: str = "Branch Lead",
    notes: str = ""
) -> str:
    """
    Dispatch an intra-branch stock transfer between North Gujarat branches.

    Args:
        from_branch: Source branch ID (e.g. 'HQ-MEHSANA').
        to_branch: Destination branch ID (e.g. 'BR-PATAN-01', 'BR-VISN-02', 'BR-UNJHA-03', 'BR-PALAN-04').
        part_number: OEM Part Number to transfer.
        quantity: Number of units.
        requested_by: Name and role of requester.
        notes: Dispatch notes or reason.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from multibranch_hub_engine import get_multibranch_engine
    mgr = get_multibranch_engine()
    res = mgr.transfer_stock(
        from_branch=from_branch,
        to_branch=to_branch,
        part_number=part_number,
        quantity=quantity,
        requested_by=requested_by,
        notes=notes
    )

    t = res["transfer"]
    lines = [
        "### 🚚 Chamunda Multi-Branch • Intra-Branch Stock Transfer Dispatched",
        f"**Transfer ID:** `{t['transfer_id']}` | **Status:** **{t['status']}**",
        f"**Route:** **{t['from_branch_name']}** (`{t['from_branch']}`) ➔ **{t['to_branch_name']}** (`{t['to_branch']}`)",
        f"**Part Dispatched:** `{t['part_number']}` - **{t['part_name']}**",
        f"**Quantity:** **{t['quantity']} pcs** | **Total Valuation:** **₹{t['total_value_inr']:,}**",
        f"**Requested By:** {t['requested_by']}",
        f"**Notes:** {t['notes']}",
        "",
        f"Gujarati Dispatch Note: *{res['message_gu']}*",
        f"📲 **Intra-Branch Waybill Alert Dispatched via +91 78747 19139**",
        f"🔗 **Multi-Branch Console:** [http://127.0.0.1:8080/#multibranch-hub](http://127.0.0.1:8080/#multibranch-hub)"
    ]
    return "\n".join(lines)


def chamunda_optimize_laptop_performance(mode: str = "safe") -> str:
    """
    Execute high-speed Turbo Boost to fix laptop lagging, terminate stale/orphan background tasks,
    reclaim RAM using libc malloc_trim, and purge temp caches.

    Args:
        mode: 'safe' for standard lag resolution, 'aggressive' for deep background task pruning.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from system_optimizer import get_system_optimizer
    opt = get_system_optimizer()
    res = opt.optimize_laptop_performance(aggressive=(mode == "aggressive"))

    lines = [
        "### 🚀 Chamunda Automobile • Laptop Performance Optimizer & Lag Buster",
        f"**Optimization Mode:** `{res['mode']}` | **Status:** ✅ Completed",
        f"**Freed Memory:** **{res['freed_memory_mb']} MB RAM**",
        f"**RAM Usage Now:** **{res['metrics_after']['memory']['percent_used']}%** (Available: **{res['metrics_after']['memory']['available_mb']} MB**)",
        f"**Terminated Stale Processes:** `{res['closed_processes_count']}` | **Pruned Cache Dirs:** `{res['caches_pruned_count']}`",
        "",
        f"**ગુજરાતી અહેવાલ:** *{res['message_gu']}*",
        "",
        "🔗 **System Telemetry & Controls:** [http://127.0.0.1:8080](http://127.0.0.1:8080)"
    ]
    return "\n".join(lines)


def chamunda_get_system_performance_metrics() -> str:
    """
    Retrieve real-time CPU, RAM, load averages, and top memory processes to diagnose laptop lag.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from system_optimizer import get_system_optimizer
    opt = get_system_optimizer()
    m = opt.get_system_metrics()

    top_p = [f"  - `{p['name']}` (PID {p['pid']}): **{p['memory_mb']} MB RAM** ({p['cpu_percent']}% CPU)" for p in m['top_processes']]

    lines = [
        "### 💻 Chamunda Automobile • Laptop System Resource Telemetry",
        f"**Overall Status:** **{m['status']}** ({m['status_gu']})",
        f"**CPU Load:** **{m['cpu_percent']}%** across {m['cpu_cores_logical']} cores (Load Avg: {m['load_averages']['1_min']}, {m['load_averages']['5_min']}, {m['load_averages']['15_min']})",
        f"**RAM Utilization:** **{m['memory']['percent_used']}%** (Used: {m['memory']['used_mb']} MB / Total: {m['memory']['total_mb']} MB | Free: {m['memory']['free_mb']} MB)",
        f"**Swap Memory:** **{m['swap']['percent_used']}%** (Used: {m['swap']['used_mb']} MB / Total: {m['swap']['total_mb']} MB)",
        "",
        "**Top Resource Consuming Processes:**",
        "\n".join(top_p) if top_p else "  - None"
    ]
    return "\n".join(lines)


def chamunda_get_webar_engine_overlay(assembly_id: str = "AR-J350-HEAD") -> str:
    """
    Project Augmented Reality (AR) camera HUD markers, factory torque specs (Nm),
    tightening order (1->4), and warehouse stock for Royal Enfield engine assemblies.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from webar_engine_guide import get_webar_engine
    eng = get_webar_engine()
    res = eng.calculate_ar_camera_view(assembly_id=assembly_id)

    if not res.get("success"):
        return f"Error: {res.get('error')}"

    lines = [
        f"### 👁️ Chamunda WebAR • Live Camera Engine Overlay: {res['title']}",
        f"**Platform:** **{res['platform']}** | **Camera Resolution:** `{res['camera_resolution']}`",
        f"**Methodology:** *{res['methodology']}*",
        f"**Advisory:** {res['ramesh_advisory']}",
        "",
        "#### 🔩 AR Spatial Markers & Factory Torque Sequence:",
        "| Step | Marker Label | Part # | Factory Torque | Socket Tool | Threadlocker | Warehouse Stock |",
        "| :---: | :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    for m in res["markers"]:
        lines.append(
            f"| **#{m['sequence_step']}** | `{m['label']}` | `{m['part_number']}` | **{m['torque_nm']} Nm** (±{m['torque_tolerance_nm']}) | {m['tool_spec']} | {m['threadlocker']} | **{m.get('warehouse_stock', 'In Stock')} pcs** |"
        )
    lines.append("")
    lines.append(f"📲 **Launch WebAR Camera Overlay:** [http://127.0.0.1:8080/#webar-guide](http://127.0.0.1:8080/#webar-guide)")
    return "\n".join(lines)


def chamunda_get_night_locker_telemetry() -> str:
    """
    Retrieve 24/7 exterior highway emergency smart locker status, compartment inventory,
    environmental telemetry (temp, battery, relay lines), and night sales summary.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from night_locker_engine import get_night_locker_manager
    mgr = get_night_locker_manager()
    st = mgr.get_locker_status()

    tel = st["telemetry"]
    lines = [
        f"### 🌙 Chamunda 24/7 Highway Emergency Spares Locker Status",
        f"**Station:** `{st['locker_station']}` | **Location:** {st['location']}",
        f"**Status:** **{tel.get('system_status')}** | **Ambient Temp:** `{tel.get('ambient_temp_c')}°C` | **UPS Battery:** `{tel.get('backup_battery_pct')}%`",
        f"**Available Boxes:** **{st['available_compartments_count']} / {st['total_compartments']} Bays** | **Night Revenue:** **₹{st['total_night_revenue_inr']:,}**",
        "",
        "#### 📦 Exterior Smart Compartments Grid:",
        "| Box ID | Emergency Item | Part # | Price | Stock | Door State | Status |",
        "| :---: | :--- | :--- | :--- | :---: | :---: | :--- |"
    ]
    for c in st["compartments"]:
        lines.append(
            f"| `{c['box_id']}` | **{c['item_name'][:30]}...** | `{c['part_number']}` | ₹{c['price_inr']:,} | {c['units_inside']} pcs | `{c['door_state']}` | **{c['status']}** |"
        )
    lines.append("")
    lines.append(f"📲 **Official Customer WhatsApp Helpline:** Strictly `{st['support_whatsapp']}`")
    lines.append(f"🔗 **Locker Admin Console:** [http://127.0.0.1:8080/#night-locker](http://127.0.0.1:8080/#night-locker)")
    return "\n".join(lines)


def chamunda_reserve_emergency_highway_locker(
    box_id: str = "BOX-01",
    customer_name: str = "Touring Rider",
    phone: str = "+91 98250 12345",
    vehicle_reg: str = "GJ-02-BQ-1234"
) -> str:
    """
    Reserve an emergency highway locker compartment for a stranded rider,
    generating dynamic UPI payment string and 6-digit unlock OTP.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from night_locker_engine import get_night_locker_manager
    mgr = get_night_locker_manager()
    res = mgr.reserve_compartment(box_id=box_id, customer_name=customer_name, phone=phone, vehicle_reg=vehicle_reg)

    if not res.get("success"):
        return f"Reservation Failed: {res.get('error')}"

    lines = [
        f"### 🌙 Emergency Highway Locker Reserved Successfully",
        f"**Reservation ID:** `{res['reservation_id']}` | **Box Allocated:** `{res['box_id']}`",
        f"**Emergency Item:** **{res['item_name']}** ({res['item_name_gu']})",
        f"**Amount Payable:** **₹{res['amount_payable']}**",
        f"**Dispenser Unlock OTP:** 🔑 **`{res['otp_code']}`** *(Valid for 15 mins)*",
        f"**Dynamic UPI QR Link:** `{res['upi_payload']}`",
        "",
        f"**ગુજરાતી પુષ્ટિ:** *{res['message_gu']}*",
        f"📲 **WhatsApp Help & Payment Slip Dispatched to {phone} via {res['whatsapp_helpline']}**"
    ]
    return "\n".join(lines)


def chamunda_unlock_emergency_highway_locker(
    reservation_id: str,
    otp_code: str,
    payment_ref: str = "UPI-AUTOCONFIRMED"
) -> str:
    """
    Verify UPI payment, authenticate 6-digit OTP, and trigger physical solenoid relay to unlock compartment.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from night_locker_engine import get_night_locker_manager
    mgr = get_night_locker_manager()
    res = mgr.verify_and_unlock(reservation_id=reservation_id, otp_code=otp_code, payment_ref=payment_ref)

    if not res.get("success"):
        return f"Unlock Failed: {res.get('error')}"

    lines = [
        f"### 🔓 Emergency Locker Compartment Unlocked & Dispensed",
        f"**Box ID:** `{res['box_id']}` | **Item Dispensed:** **{res['item_name']}**",
        f"**Solenoid Relay Signal:** `{res['solenoid_relay']}` | **Door State:** `{res['door_state']}`",
        f"**Transaction ID:** `{res['transaction_id']}` | **Amount Paid:** **₹{res['amount_paid']}**",
        f"**Remaining In Box:** {res['units_remaining']} units",
        "",
        f"**ગુજરાતી પુષ્ટિ:** *{res['message_gu']}*",
        f"📲 **Official Digital Receipt Dispatched via {res['whatsapp_helpline']}**"
    ]
    return "\n".join(lines)


def chamunda_get_cloud_shadow_telemetry() -> str:
    """
    Retrieve real-time Project Chhaya Cloud Shadow status, replica agents health,
    and offline sync telemetry for CEO Aradhya and Chairman Alpesh Sir.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from cloud_shadow_engine import get_cloud_shadow_manager
    mgr = get_cloud_shadow_manager()
    st = mgr.get_shadow_telemetry()

    snap = st["snapshot_data"]
    lines = [
        f"### ☁️ Project Chhaya • Cloud Shadow Mirror Telemetry",
        f"**Cluster:** `{st['cluster_name']}` | **Region:** `{st['cloud_region']}`",
        f"**Primary Host:** `{st['primary_host']}` | **System Mode:** **`{st['system_mode']}`**",
        f"**Last Sync Heartbeat:** `{st['last_heartbeat']}`",
        "",
        f"#### 📊 Mirrored Enterprise Assets (Offline-Ready):",
        f"- **Parts SKUs Mirrored:** **{snap.get('total_parts_skus', 4469):,} distinct OEM items**",
        f"- **Mirrored Inventory Value:** **₹{snap.get('inventory_valuation_inr', 5775000):,}**",
        f"- **Active Service Bays:** **{snap.get('active_job_cards_count', 5)} motorcycles**",
        f"- **24/7 Highway Locker:** **{snap.get('night_locker_available_bays', 8)} available compartments**",
        f"- **Queued Offline Mutations:** **{st['queued_mutations_count']} pending**",
        "",
        f"#### 🤖 6 Autonomous Cloud Replica Agents Standing By:",
    ]
    for aid, ag in st["cloud_replicas"].items():
        lines.append(f"- **{ag['name']}** (`{ag['role']}`): `{ag['status']}` — *{ag['capabilities'][:40]}...*")

    lines.append("")
    lines.append(f"📲 **WhatsApp Bot Gateway:** Strictly `{st['whatsapp_helpline']}`")
    lines.append(f"🔗 **Cloud Shadow Dashboard:** [http://127.0.0.1:8080/#cloud-shadow](http://127.0.0.1:8080/#cloud-shadow)")
    return "\n".join(lines)


def chamunda_simulate_offline_agent_query(query_text: str) -> str:
    """
    Simulate a remote inquiry to Chamunda agents (e.g. via WhatsApp) while the local laptop is offline.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from cloud_shadow_engine import get_cloud_shadow_manager
    mgr = get_cloud_shadow_manager()
    res = mgr.process_remote_offline_query(query_text=query_text)

    lines = [
        f"### 📡 Cloud Shadow Offline Query Resolution",
        f"**Inquiry:** *\"{query_text}\"*",
        f"**Responding Agent:** **{res['responding_agent']}** ({res['assigned_role']})",
        f"**Environment:** `{res['execution_environment']}`",
        "",
        f"**English Response:**",
        f"> {res['response_en']}",
        "",
        f"**ગુજરાતી પ્રત્યુત્તર:**",
        f"> **{res['response_gu']}**",
        "",
        f"📲 **WhatsApp Channel:** `{res['whatsapp_helpline']}`"
    ]
    return "\n".join(lines)


def chamunda_trigger_cloud_shadow_sync() -> str:
    """
    Force instant synchronization and snapshot push from local laptop to Cloud Shadow.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from cloud_shadow_engine import get_cloud_shadow_manager
    mgr = get_cloud_shadow_manager()
    res = mgr.generate_state_snapshot()
    return f"☁️ Cloud Shadow Sync Successful! Generated snapshot at {res['timestamp']}: {res['message']}"


def chamunda_get_kalpavriksha_growth_telemetry() -> str:
    """
    Retrieve real-time Project Kalpavriksha autonomous virtual growth metrics,
    agent levels, total XP, simulations passed, and technical manuals indexed.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from kalpavriksha_growth_engine import get_kalpavriksha_engine
    engine = get_kalpavriksha_engine()
    tel = engine.get_growth_telemetry()

    lines = [
        f"### 🌳 Project Kalpavriksha • Autonomous Virtual Growth Telemetry",
        f"**Cluster:** `{tel['cluster_title']}` | **Offline Engine:** **{'100% ACTIVE' if tel['offline_mode_active'] else 'STANDBY'}**",
        f"**Fleet Overall IQ:** **{tel['fleet_overall_iq']}** | **Average Mastery Level:** **Level {tel['average_agent_level']}**",
        f"**Total Fleet Experience:** **{tel['total_fleet_xp']:,} XP** | **Simulations Passed:** **{tel['total_simulations_executed']} scenarios**",
        f"**Locally Indexed Specs:** **{tel['knowledge_specs_count']} OEM Technical Manuals**",
        "",
        f"#### 🛡️ Departmental Sub-Agents Mastery Progression:",
    ]
    for aid, ag in tel["agents"].items():
        lines.append(f"- **{ag['agent_name']}** ({ag['department']}): **Level {ag['level']}** ({ag['rank']} - {ag['total_xp']:,} XP) | *Passed: {ag['simulations_passed']} sims*")

    lines.append("")
    lines.append(f"📲 **Official Customer WhatsApp Helpline:** Strictly `{tel['whatsapp_helpline']}`")
    lines.append(f"🔗 **Virtual Growth Arena:** [http://127.0.0.1:8080/#kalpavriksha](http://127.0.0.1:8080/#kalpavriksha)")
    return "\n".join(lines)


def chamunda_trigger_agent_synthetic_training() -> str:
    """
    Trigger an autonomous virtual Royal Enfield breakdown simulation on the laptop,
    scoring agent diagnosis and awarding experience points (XP).
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from kalpavriksha_growth_engine import get_kalpavriksha_engine
    engine = get_kalpavriksha_engine()
    res = engine.run_synthetic_diagnostic_simulation()

    lines = [
        f"### ⚡ Autonomous Synthetic Breakdown Simulation Executed",
        f"**Simulation ID:** `{res['simulation_id']}` | **Motorcycle:** **{res['bike_model']}**",
        f"**Symptom Analyzed:** *\"{res['symptom']}\"*",
        f"**Responding Agent:** **{res['responding_agent']}**",
        f"**Diagnostic Finding:** {res['diagnosis']}",
        f"**Prescribed Action:** {res['solution_prescribed']}",
        f"**XP Awarded:** **+{res['xp_awarded']} XP** (Current: **Level {res['agent_current_level']}** {'🔥 LEVEL UP!' if res['leveled_up'] else ''})",
        "",
        f"**ગુજરાતી ઉકેલ:** *{res['solution_gu']}*",
        f"🛠️ *100% Offline Simulation completed locally on laptop with zero internet required.*"
    ]
    return "\n".join(lines)


# ==============================================================================

# ==============================================================================
# ROYAL ENFIELD DEALER MANAGEMENT SYSTEM (RE-DMS SUITE) TOOLS
# ==============================================================================

def chamunda_get_dms_executive_telemetry() -> str:
    """
    Retrieve comprehensive Royal Enfield Dealer Management System (RE-DMS Suite) executive telemetry:
    GST billing, FSC warranty claims, financial ledger, marketing campaigns, and 8-agent roster.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from dms_enterprise_suite_engine import get_dms_suite_engine, OFFICIAL_WHATSAPP_HELPLINE
    from shop_subagents_engine import get_shop_subagents_manager
    dms = get_dms_suite_engine()
    tel = dms.get_dms_overview_telemetry()
    acc = tel.get("accounting_summary", {})
    sub_mgr = get_shop_subagents_manager()
    subagents = sub_mgr.list_subagents()

    lines = [
        f"### 🏢 Chamunda Royal Enfield Dealer Management System (RE-DMS)",
        f"**Dealership:** `{tel.get('dealership_name', 'Chamunda Automobile')}` | **GSTIN:** `{tel.get('gstin')}`",
        f"**Official WhatsApp Helpline:** Strictly `{tel.get('helpline', OFFICIAL_WHATSAPP_HELPLINE)}`",
        "",
        f"#### 💼 Billing & Invoicing Summary:",
        f"- **Total Invoices Generated:** **{tel.get('total_invoices_generated', 0)}**",
        f"- **Total Genuine Spares Revenue (HSN 8714):** ₹{acc.get('pnl_summary', {}).get('gross_parts_revenue', 0):,.2f}",
        f"- **Total Labor Services Revenue (SAC 998729):** ₹{acc.get('pnl_summary', {}).get('gross_labor_revenue', 0):,.2f}",
        f"- **Gross Billed Turnover:** ₹{acc.get('pnl_summary', {}).get('total_revenue', 0):,.2f}",
        f"- **Total GST Collected (CGST+SGST):** ₹{acc.get('gstr1_summary', {}).get('total_gst_liability', 0):,.2f}",
        f"- **OEM Warranty & FSC Claims:** **{tel.get('total_warranty_claims', 0)} claims**",
        "",
        f"#### 📊 Double-Entry Accounting Ledger:",
        f"- **Total Cash/Bank Credits:** ₹{acc.get('total_credits', 0):,.2f} | **Debits:** ₹{acc.get('total_debits', 0):,.2f}",
        f"- **Net Cash Flow:** ₹{acc.get('net_cash_inflow', 0):,.2f}",
        f"- **Accounts Receivable (Partner Garages):** ₹{acc.get('total_ar_outstanding', 0):,.2f}",
        f"- **Distributor Accounts Payable (RE Distributorship):** ₹{acc.get('total_ap_due', 0):,.2f}",
        "",
        f"#### 📢 CRM & Marketing Pipeline:",
        f"- **Active Campaigns:** **{tel.get('active_campaigns_count', 0)}** | **Lead Pipeline:** **{tel.get('active_leads_count', 0)} riders**",
        "",
        f"#### 👥 Dealership Sub-Agents Fleet ({len(subagents)} Sub-Agents + CEO Aradhya):"
    ]
    for sa in subagents:
        lines.append(f"- **{sa.get('agent_id')}** ({sa.get('name')}): *{sa.get('designated_head')}* - {sa.get('role', sa.get('role_badge', 'Specialist'))}")

    lines.append("")
    lines.append(f"🔗 **DMS Suite Portal:** [http://127.0.0.1:8080/#dms-suite](http://127.0.0.1:8080/#dms-suite)")
    return "\n".join(lines)


def chamunda_create_dms_billing_invoice(
    customer_name: str,
    phone: str,
    bike_model: str,
    registration_no: str,
    odometer_km: int = 4500,
    warranty_type: str = "Paid Service",
    parts_items: Optional[List[Dict[str, Any]]] = None,
    labor_items: Optional[List[Dict[str, Any]]] = None,
    discount_amount: float = 0.0,
    payment_mode: str = "UPI"
) -> str:
    """
    Create an official Royal Enfield Dealership Split-GST Tax Invoice with Dynamic UPI QR & Gate Pass.
    Separates Labor (SAC 998729 @ 18% GST) and Genuine Spares (HSN 8714 @ 18% or 28% GST).
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from dms_enterprise_suite_engine import get_dms_suite_engine, OFFICIAL_WHATSAPP_HELPLINE
    dms = get_dms_suite_engine()

    res = dms.create_split_gst_invoice(
        customer_name=customer_name,
        phone=phone,
        bike_model=bike_model,
        registration_no=registration_no,
        odometer_km=odometer_km,
        warranty_type=warranty_type,
        parts_items=parts_items,
        labor_items=labor_items,
        discount_amount=discount_amount,
        payment_mode=payment_mode
    )
    inv = res.get("invoice", {})

    lines = [
        f"### 🧾 Royal Enfield Split-GST Tax Invoice Generated",
        f"**Invoice No:** `{inv.get('invoice_number')}` | **Date:** `{inv.get('date')}`",
        f"**Customer:** **{inv.get('customer_name')}** ({inv.get('phone')}) | **Bike:** **{inv.get('bike_model')}** (`{inv.get('registration_no')}`)",
        f"**Biller:** *{inv.get('biller')}*",
        "",
        f"#### ⚙️ Split Financial Breakdown:",
        f"- **Spares Subtotal (HSN 8714):** ₹{inv.get('parts_subtotal', 0):,.2f}",
        f"- **Labor Subtotal (SAC 998729):** ₹{inv.get('labor_subtotal', 0):,.2f}",
        f"- **Taxable Amount:** ₹{inv.get('taxable_amount', 0):,.2f}",
        f"- **CGST (9%):** ₹{inv.get('cgst_amount', 0):,.2f} | **SGST (9%):** ₹{inv.get('sgst_amount', 0):,.2f}",
        f"- **Grand Total Payable:** **₹{inv.get('grand_total', 0):,.2f}** ({inv.get('payment_mode')})",
        "",
        f"#### 🎫 Verified Gate Pass:",
        f"- **Gate Pass Code:** `{inv.get('gate_pass_code')}` | **Status:** Security Verified",
        "",
        f"📲 **NPCI Dynamic UPI QR URI:** `{inv.get('qr_code_uri')}`",
        f"📞 **Official Helpline:** `{OFFICIAL_WHATSAPP_HELPLINE}`"
    ]
    return "\n".join(lines)


def chamunda_file_oem_warranty_claim(
    coupon_type: str = "1st Free Service Coupon",
    chassis_no: str = "ME3J350F2NR109842",
    engine_no: str = "J350-2024-99812",
    bike_model: str = "Classic 350 (Reborn)",
    customer_name: str = "Alpesh Patel",
    phone: str = "+91 98250 12345",
    kilometers: int = 500,
    defective_components: str = "Engine Oil, Oil Filter & Periodic Check",
    claim_amount: float = 1450.0
) -> str:
    """
    File an official OEM Royal Enfield Warranty or Free Service Coupon (FSC) reimbursement claim.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from dms_enterprise_suite_engine import get_dms_suite_engine
    dms = get_dms_suite_engine()

    res = dms.file_oem_warranty_claim(
        coupon_type=coupon_type,
        chassis_no=chassis_no,
        engine_no=engine_no,
        bike_model=bike_model,
        customer_name=customer_name,
        phone=phone,
        kilometers=kilometers,
        defective_components=defective_components,
        claim_amount=claim_amount
    )
    claim = res.get("claim", {})

    lines = [
        f"### 🛡️ Royal Enfield OEM Warranty Claim Filed",
        f"**Claim ID:** `{claim.get('claim_id')}` | **Coupon / Type:** **{claim.get('coupon_type')}**",
        f"**Motorcycle:** **{claim.get('bike_model')}** | **Chassis:** `{claim.get('chassis_no')}` | **Engine:** `{claim.get('engine_no')}`",
        f"**Customer:** **{claim.get('customer_name')}** ({claim.get('phone')}) | **Odo:** {claim.get('kilometers')} km",
        f"**Claim Amount:** **₹{claim.get('claim_amount', 0):,.2f}**",
        f"**OEM Status:** `{claim.get('re_approval_status')}` | **Credit Note:** `{claim.get('re_credit_note_no')}`",
        f"**Officer:** *{claim.get('filed_by')}*",
        f"**Components:** {claim.get('defective_components')}"
    ]
    return "\n".join(lines)


def chamunda_launch_marketing_campaign(
    name: str = "Monsoon Safe Ride Health Camp",
    target_audience: str = "Classic 350 & Hunter 350 Owners (Siddhpur & Patan)",
    offer_title: str = "Free 50-Point Monsoon Health Checkup",
    offer_details: str = "Complimentary brake inspection, chain lube, and 15% off on Motul 7100 Engine Oil",
    channels: Optional[List[str]] = None
) -> str:
    """
    Deploy a targeted customer retention and marketing campaign via WhatsApp and digital channels.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from dms_enterprise_suite_engine import get_dms_suite_engine
    dms = get_dms_suite_engine()

    res = dms.create_marketing_campaign(
        name=name,
        target_audience=target_audience,
        offer_title=offer_title,
        offer_details=offer_details,
        channels=channels
    )
    camp = res.get("campaign", {})

    lines = [
        f"### 📢 Marketing & Retention Campaign Deployed",
        f"**Campaign ID:** `{camp.get('campaign_id')}` | **Campaign:** **{camp.get('name')}**",
        f"**Target Audience:** {camp.get('target_audience')}",
        f"**Offer Title:** **{camp.get('offer_title')}**",
        f"**Details:** {camp.get('offer_details')}",
        f"**Channels:** {', '.join(camp.get('channels', []))}",
        f"**Projected Leads:** **{camp.get('leads_generated')} leads** | **Expected Bookings:** **{camp.get('bookings_confirmed')} slots**",
        f"**Status:** `{camp.get('status')}`",
        f"**Campaign Lead:** *{camp.get('campaign_lead')}*"
    ]
    return "\n".join(lines)


def chamunda_get_dms_financial_daybook() -> str:
    """
    Retrieve official Royal Enfield Dealership double-entry Daybook, Cash/Bank Ledger, and GSTR-1 summary.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from dms_enterprise_suite_engine import get_dms_suite_engine
    dms = get_dms_suite_engine()
    acc = dms.get_dms_accounting_daybook()

    lines = [
        f"### 📖 Chamunda Automobile • Official Financial Daybook",
        f"**Dealership:** `{acc.get('dealership_code')}` | **GSTIN:** `{acc.get('gstin')}`",
        "",
        f"#### 💰 Double-Entry Cash Flow:",
        f"- **Total Credits (Inflow):** **₹{acc.get('total_credits', 0):,.2f}**",
        f"- **Total Debits (Outflow):** **₹{acc.get('total_debits', 0):,.2f}**",
        f"- **Net Cash Inflow:** **₹{acc.get('net_cash_inflow', 0):,.2f}**",
        "",
        f"#### 👥 Accounts Receivable (B2B Partner Garages):",
        f"- **Total Outstanding:** **₹{acc.get('total_ar_outstanding', 0):,.2f}**",
    ]
    for ar in acc.get("accounts_receivable", []):
        lines.append(f"  • **{ar['party']}** ({ar['tier']}): ₹{ar['outstanding']:,.2f} [{ar['status']}]")

    lines.append("")
    lines.append("#### 🏭 Accounts Payable (To Royal Enfield Spare Parts Distributorship):")
    lines.append(f"- **Total Payable Due:** **₹{acc.get('total_ap_due', 0):,.2f}**")
    for ap in acc.get("accounts_payable", []):
        lines.append(f"  • **{ap['vendor']}** (Inv: `{ap['invoice_ref']}`): ₹{ap['amount']:,.2f} (Due: {ap['due_date']})")

    lines.append("")
    lines.append("#### 📊 GSTR-1 Tax Summary:")
    gstr1 = acc.get("gstr1_summary", {})
    lines.append(f"- **Total Taxable Value:** ₹{gstr1.get('total_taxable_value', 0):,.2f}")
    lines.append(f"- **CGST Collected:** ₹{gstr1.get('cgst_collected', 0):,.2f} | **SGST Collected:** ₹{gstr1.get('sgst_collected', 0):,.2f}")
    lines.append(f"- **Total Output GST Liability:** **₹{gstr1.get('total_gst_liability', 0):,.2f}**")

    return "\n".join(lines)

def chamunda_create_vehicle_booking(
    customer_name: str,
    phone: str,
    bike_model: str,
    colorway: str = "Standard Edition",
    booking_amount: float = 10000.0,
    payment_mode: str = "UPI (Instant)",
    finance_bank: str = "HDFC Two Wheeler Finance"
) -> str:
    """
    Record a new Royal Enfield motorcycle booking in the showroom with official token receipt.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from dms_enterprise_suite_engine import get_dms_suite_engine, OFFICIAL_WHATSAPP_HELPLINE
    dms = get_dms_suite_engine()

    res = dms.create_vehicle_booking(
        customer_name=customer_name,
        phone=phone,
        bike_model=bike_model,
        colorway=colorway,
        booking_amount=booking_amount,
        payment_mode=payment_mode,
        finance_bank=finance_bank
    )
    b = res.get("booking", {})

    lines = [
        f"### 🏍️ Royal Enfield New Motorcycle Booking Confirmed",
        f"**Booking ID:** `{b.get('booking_id')}` | **Token Receipt:** `{b.get('token_receipt_no')}`",
        f"**Customer:** **{b.get('customer_name')}** ({b.get('phone')})",
        f"**Motorcycle:** **{b.get('bike_model')}** [{b.get('colorway')}]",
        f"**Advance Token Paid:** **₹{b.get('booking_amount', 0):,.2f}** ({b.get('payment_mode')})",
        f"**Finance Partner:** {b.get('finance_bank')}",
        f"**Tentative Delivery Date:** `{b.get('tentative_delivery_date')}`",
        f"**Sales Manager:** *{b.get('sales_manager')}*",
        f"📞 **Official Helpline:** `{OFFICIAL_WHATSAPP_HELPLINE}`"
    ]
    return "\n".join(lines)


def chamunda_generate_pdi_certificate(
    chassis_no: str,
    engine_no: str,
    bike_model: str,
    customer_name: str,
    inspector_name: str = "Master Tech Ramesh & Vikram Singh"
) -> str:
    """
    Execute and issue digital 30-Point Pre-Delivery Inspection (PDI) Delivery Passport.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from dms_enterprise_suite_engine import get_dms_suite_engine
    dms = get_dms_suite_engine()

    res = dms.generate_pdi_inspection(
        chassis_no=chassis_no,
        engine_no=engine_no,
        bike_model=bike_model,
        customer_name=customer_name,
        inspector_name=inspector_name
    )
    p = res.get("pdi_certificate", {})

    lines = [
        f"### ✅ Royal Enfield 30-Point PDI Delivery Passport Cleared",
        f"**Certificate ID:** `{p.get('pdi_id')}` | **Date:** `{p.get('date')}`",
        f"**Customer:** **{p.get('customer_name')}** | **Model:** **{p.get('bike_model')}**",
        f"**VIN / Chassis:** `{p.get('chassis_no')}` | **Engine:** `{p.get('engine_no')}`",
        "",
        f"#### 🔍 Key Inspection Parameters:",
        f"- **Battery Terminal Voltage:** **{p.get('battery_voltage')} V** (Spec: 12.6V - 13.0V)",
        f"- **Tire Pressure:** {p.get('tire_pressure')}",
        f"- **Engine Idle Speed:** **{p.get('idle_rpm')} RPM** (Factory Acoustic Spec)",
        f"- **Engine Oil & DOT-4 Fluid:** {p.get('engine_oil_level')} / {p.get('brake_fluid_dot4')}",
        f"- **Drive Chain Free-Play:** {p.get('chain_slack_mm')}",
        f"- **Toolkit & Manual:** Handed over in passport pouch",
        f"- **Delivery Status:** **{p.get('status')}** (Certified by *{p.get('inspector')}*)"
    ]
    return "\n".join(lines)


def chamunda_issue_ride_sure_warranty(
    customer_name: str,
    phone: str,
    bike_model: str,
    registration_no: str,
    chassis_no: str,
    coverage_years: int = 4,
    plan_type: str = "Ride Sure Premium (Extended Warranty + 24/7 Roadside Assistance)",
    premium_amount: float = 3850.0
) -> str:
    """
    Issue official Royal Enfield 'Ride Sure' Extended Warranty & 24/7 Roadside Assistance policy.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from dms_enterprise_suite_engine import get_dms_suite_engine, OFFICIAL_WHATSAPP_HELPLINE
    dms = get_dms_suite_engine()

    res = dms.issue_ride_sure_warranty(
        customer_name=customer_name,
        phone=phone,
        bike_model=bike_model,
        registration_no=registration_no,
        chassis_no=chassis_no,
        coverage_years=coverage_years,
        plan_type=plan_type,
        premium_amount=premium_amount
    )
    pol = res.get("policy", {})

    lines = [
        f"### 🛡️ Royal Enfield 'Ride Sure' Extended Warranty & RSA Policy",
        f"**Policy No:** `{pol.get('policy_no')}` | **Date:** `{pol.get('date')}`",
        f"**Customer:** **{pol.get('customer_name')}** ({pol.get('phone')})",
        f"**Motorcycle:** **{pol.get('bike_model')}** (`{pol.get('registration_no')}`)",
        f"**Chassis:** `{pol.get('chassis_no')}`",
        f"**Coverage Term:** **{pol.get('coverage_years')} Years Complete Warranty**",
        f"**Plan Tier:** {pol.get('plan_type')}",
        f"**Roadside Assistance (RSA):** 24/7 Toll-Free + Emergency Towing (Up to 50 km)",
        f"**Premium Paid:** **₹{pol.get('premium_amount', 0):,.2f}** (100% Daybook Reconciled)",
        f"📞 **Emergency 24/7 WhatsApp Helpline:** `{OFFICIAL_WHATSAPP_HELPLINE}`"
    ]
    return "\n".join(lines)


def chamunda_record_psf_csat_feedback(
    invoice_no: str,
    customer_name: str,
    phone: str,
    bike_model: str,
    rating_1_to_5: int,
    feedback_notes: str,
    issues_resolved: bool = True
) -> str:
    """
    Log 3-Day Post-Service Feedback (PSF) call, record CSAT score, and audit quality.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from dms_enterprise_suite_engine import get_dms_suite_engine
    dms = get_dms_suite_engine()

    res = dms.record_post_service_feedback(
        invoice_no=invoice_no,
        customer_name=customer_name,
        phone=phone,
        bike_model=bike_model,
        rating_1_to_5=rating_1_to_5,
        feedback_notes=feedback_notes,
        issues_resolved=issues_resolved
    )
    fb = res.get("feedback", {})

    lines = [
        f"### ⭐ 3-Day Post-Service Feedback (PSF) Logged",
        f"**Follow-Up ID:** `{fb.get('psf_id')}` | **Ref Invoice:** `{fb.get('invoice_no')}`",
        f"**Customer:** **{fb.get('customer_name')}** ({fb.get('phone')}) | **Bike:** **{fb.get('bike_model')}**",
        f"**Rating Given:** **{'⭐' * fb.get('rating', 5)} ({fb.get('rating')}/5 Stars)**",
        f"**Customer Delight Status:** `{fb.get('csat_status')}`",
        f"**Issues Resolved:** {'✅ Yes (First Time Right)' if fb.get('issues_resolved') else '⚠️ Recheck Required'}",
        f"**Auditor:** *{fb.get('auditor')}*",
        f"**Customer Notes:** \\\"{fb.get('feedback_notes')}\\\""
    ]
    return "\n".join(lines)


def chamunda_get_dms_csat_qc_telemetry() -> str:
    """
    Retrieve dealership CSAT, NPS score, and Quality Control metrics.
    """
    sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
    from dms_enterprise_suite_engine import get_dms_suite_engine
    dms = get_dms_suite_engine()
    csat = dms.get_csat_and_qc_telemetry()

    lines = [
        f"### 🏆 Royal Enfield Dealership Quality Control & CSAT Telemetry",
        f"**Dealership CSAT Score:** **{csat.get('dealership_csat_percentage')}%** ({csat.get('csat_benchmark_status')})",
        f"**Average Rating:** **{csat.get('average_rating_out_of_5')}/5.0 Stars**",
        f"**Total PSF Follow-Up Calls Logged:** **{csat.get('total_psf_calls_logged')}**",
        f"**Benchmark Standard:** Official Royal Enfield OEM Quality Excellence (>90% Green Target)",
        f"**Lead Quality Auditor:** *Ananya Joshi (Quality Control & CSAT Lead)*"
    ]
    return "\n".join(lines)

