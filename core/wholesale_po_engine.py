"""
Automated Wholesale Purchase Order (PO) Engine for Chamunda Automobile Parts & Service.
Scans stock levels, identifies items below minimum threshold, and generates formal
Wholesale POs with supplier breakdown, quantities, and cash flow projections.
"""

import os
import sys
import json
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.settings import DEFAULT_CONFIG_DIR

sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
from inventory_engine import ChamundaInventoryManager


PO_DIR = Path("/home/alpesh/chamunda_re_enterprise/data/purchase_orders")


class WholesalePOEngine:
    """Generates automated wholesale purchase orders for low-stock spare parts."""

    def __init__(self, po_dir: Path = PO_DIR):
        self.po_dir = po_dir
        self.po_dir.mkdir(parents=True, exist_ok=True)
        self.inv_mgr = ChamundaInventoryManager()

    def generate_low_stock_purchase_order(self, supplier_name: str = "Royal Enfield OEM Genuine Spares Dist.") -> Dict[str, Any]:
        """Scan parts catalog, generate wholesale purchase order for reorders."""
        low_stock_parts = self.inv_mgr.get_low_stock_alerts()
        
        # If no items currently below threshold, include standard fast-moving stock replenishment
        if not low_stock_parts:
            all_parts = self.inv_mgr.get_all_parts()
            low_stock_parts = all_parts[:4]

        po_number = f"PO-CAPS-{datetime.datetime.now().strftime('%Y%m%d')}-{len(list(self.po_dir.glob('*.html'))) + 1:03d}"
        po_date = datetime.datetime.now().strftime("%d-%b-%Y")

        po_items = []
        total_wholesale_cost = 0

        rows_html = ""
        for idx, p in enumerate(low_stock_parts, 1):
            reorder_qty = max(10, p.get("min_threshold", 5) * 3)
            item_total = p["cost_price"] * reorder_qty
            total_wholesale_cost += item_total
            po_items.append({
                "part_id": p["part_id"],
                "name": p["name"],
                "oem_number": p["oem_number"],
                "qty": reorder_qty,
                "unit_cost": p["cost_price"],
                "total": item_total
            })

            rows_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{idx}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">
                    <strong>{p['name']}</strong><br>
                    <small style="color: #666;">OEM Part No: <code>{p['oem_number']}</code> | ID: {p['part_id']}</small>
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: center;"><strong>{reorder_qty}</strong></td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">₹{p['cost_price']}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right; font-weight: bold;">₹{item_total:,}</td>
            </tr>
            """

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Purchase Order {po_number} - Chamunda Automobile</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #fdfdfd; padding: 30px; color: #333; }}
        .po-box {{ max-width: 800px; margin: auto; background: white; border: 2px solid #1b4d3e; border-radius: 8px; padding: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.06); }}
        .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid #c5a059; padding-bottom: 15px; margin-bottom: 20px; }}
        .table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        .table th {{ background: #1b4d3e; color: white; padding: 10px; text-align: left; }}
        .total-box {{ float: right; width: 300px; margin-top: 20px; background: #0d2b22; color: #c5a059; padding: 15px; border-radius: 6px; }}
    </style>
</head>
<body>
    <div class="po-box">
        <div class="header">
            <div>
                <h1 style="color: #1b4d3e; margin: 0; font-size: 24px;">CHAMUNDA AUTOMOBILE PARTS & SERVICE</h1>
                <p style="color: #c5a059; font-weight: bold; margin: 3px 0;">★ OFFICIAL WHOLESALE REPLENISHMENT PURCHASE ORDER ★</p>
            </div>
            <div style="text-align: right;">
                <h3 style="margin: 0; color: #1b4d3e;">PURCHASE ORDER</h3>
                <p style="margin: 3px 0; font-weight: bold;">{po_number}</p>
                <p style="margin: 0; color: #777; font-size: 13px;">Date: {po_date}</p>
            </div>
        </div>

        <table style="width: 100%; margin-bottom: 20px;">
            <tr>
                <td style="width: 50%;">
                    <strong>Vendor / Supplier:</strong><br>
                    {supplier_name}<br>
                    Automotive Spares Hub, Sector 12
                </td>
                <td style="width: 50%; text-align: right;">
                    <strong>Ship To / Bill To:</strong><br>
                    Chamunda Automobile Parts & Service<br>
                    Attn: Workshop Stores Manager
                </td>
            </tr>
        </table>

        <table class="table">
            <thead>
                <tr>
                    <th style="width: 5%;">#</th>
                    <th style="width: 55%;">Part Description & OEM Spec</th>
                    <th style="width: 10%; text-align: center;">Reorder Qty</th>
                    <th style="width: 15%; text-align: right;">Wholesale Rate</th>
                    <th style="width: 15%; text-align: right;">Total Outlay</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>

        <div class="total-box">
            <table style="width: 100%; color: white;">
                <tr>
                    <td>Total Reorder SKUs:</td>
                    <td style="text-align: right;">{len(po_items)}</td>
                </tr>
                <tr style="font-size: 18px; font-weight: bold; color: #ffe29a;">
                    <td>Total Outlay:</td>
                    <td style="text-align: right;">₹{total_wholesale_cost:,}</td>
                </tr>
            </table>
        </div>

        <div style="clear: both; margin-top: 35px; border-top: 1px solid #ddd; padding-top: 15px; font-size: 12px; color: #666;">
            <strong>Authorized Signatory:</strong> Chief Executive Officer (CEO), Chamunda Automobile Parts & Service.
        </div>
    </div>
</body>
</html>
"""
        po_file = self.po_dir / f"{po_number}.html"
        po_file.write_text(html_content, encoding="utf-8")

        summary = f"Wholesale Purchase Order `{po_number}` generated for **{len(po_items)} SKUs** (Total Wholesale Outlay: **₹{total_wholesale_cost:,}**)."

        return {
            "po_number": po_number,
            "total_outlay_inr": total_wholesale_cost,
            "po_file": str(po_file),
            "items": po_items,
            "summary": summary
        }
