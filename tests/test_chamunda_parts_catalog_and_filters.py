"""
Test Suite for Chamunda AI Royal Enfield Parts Catalog & Multi-Parameter Filter Engine.
Verifies authentic parts sourced from spares.royalenfield.com, multi-criteria filtering,
CEO tools integration, and Gujarati/English offline commander support.
"""

import json
import pytest
from pathlib import Path

import sys
sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
from inventory_engine import ChamundaInventoryManager, DATA_DIR

from tools.chamunda_ceo_tools import (
    chamunda_lookup_part,
    chamunda_search_parts_filtered,
)
from core.offline_commander import OfflineCommander


@pytest.fixture
def inventory_manager():
    return ChamundaInventoryManager()


def test_catalog_loaded_and_count(inventory_manager):
    """Verify catalog loads authentic parts from spares.royalenfield.com."""
    parts = inventory_manager.get_all_parts()
    assert len(parts) >= 71, f"Expected at least 71 parts, found {len(parts)}"
    
    # Verify required schema on every part
    for p in parts[:50]:
        assert "name" in p and len(p["name"]) > 0
        assert "part_number" in p or "oem_number" in p
        assert "category" in p and len(p["category"]) > 0
        assert "models" in p and isinstance(p["models"], list) and len(p["models"]) > 0
        assert "mrp" in p and p["mrp"] > 0
        assert "cost_price" in p and p["cost_price"] > 0
        assert "stock" in p and p["stock"] >= 0
        assert "bin_location" in p


def test_filter_by_part_number(inventory_manager):
    """Verify exact and substring search by OEM part number / SKU."""
    results = inventory_manager.filter_parts(part_number="574050")
    assert len(results) >= 1
    assert any("574050" in p.get("part_number", "") or "574050" in p.get("oem_number", "") for p in results)


def test_filter_by_bike_model(inventory_manager):
    """Verify filtering by Royal Enfield motorcycle models."""
    for model in ["Hunter 350", "Classic 350", "Interceptor 650", "Himalayan 450"]:
        matches = inventory_manager.filter_parts(model=model)
        assert len(matches) > 0, f"Expected parts for {model}"
        for p in matches:
            assert any(model.lower() in m.lower() for m in p.get("models", []))


def test_filter_by_category(inventory_manager):
    """Verify filtering by catalog category."""
    braking_parts = inventory_manager.filter_parts(category="Braking")
    assert len(braking_parts) > 0
    for p in braking_parts:
        assert "braking" in p["category"].lower()


def test_filter_by_price_range(inventory_manager):
    """Verify filtering with min_price and max_price."""
    min_p, max_p = 200, 1000
    priced_parts = inventory_manager.filter_parts(min_price=min_p, max_price=max_p)
    assert len(priced_parts) > 0
    for p in priced_parts:
        assert min_p <= p["mrp"] <= max_p


def test_filter_by_stock_status(inventory_manager):
    """Verify filtering by in_stock, low_stock, and out_of_stock."""
    in_stock = inventory_manager.filter_parts(stock_status="in_stock")
    assert len(in_stock) > 0
    assert all(p["stock"] > 0 for p in in_stock)

    low_stock = inventory_manager.filter_parts(stock_status="low_stock")
    assert all(p["stock"] <= p.get("min_threshold", 5) for p in low_stock)


def test_sorting_capabilities(inventory_manager):
    """Verify sorting by price_asc, price_desc, stock, and name."""
    parts_asc = inventory_manager.filter_parts(sort_by="price_asc", limit=20)
    for i in range(len(parts_asc) - 1):
        assert parts_asc[i]["mrp"] <= parts_asc[i + 1]["mrp"]

    parts_desc = inventory_manager.filter_parts(sort_by="price_desc", limit=20)
    for i in range(len(parts_desc) - 1):
        assert parts_desc[i]["mrp"] >= parts_desc[i + 1]["mrp"]

    parts_stock = inventory_manager.filter_parts(sort_by="stock", limit=20)
    for i in range(len(parts_stock) - 1):
        assert parts_stock[i]["stock"] >= parts_stock[i + 1]["stock"]


def test_chamunda_search_parts_filtered_tool():
    """Verify the CEO tool chamunda_search_parts_filtered produces valid executive Markdown table."""
    output = chamunda_search_parts_filtered(
        query="oil filter",
        min_price=100,
        max_price=1000,
        sort_by="price_asc"
    )
    assert "Chamunda Automobile" in output
    assert "| OEM Part No | Part Name | Category | MRP | Cost | Stock | Bin | Compatible Models |" in output
    assert "₹" in output


def test_chamunda_lookup_part_natural_language():
    """Verify chamunda_lookup_part handles natural language and price constraints."""
    res = chamunda_lookup_part("Hunter 350 brake pads")
    assert "Chamunda Automobile" in res
    assert len(res) > 50

    res_price = chamunda_lookup_part("oil filter under 500")
    assert "Chamunda Automobile" in res_price
    assert "₹" in res_price


def test_offline_commander_parts_gujarati_and_english():
    """Verify OfflineCommander routes parts queries in Gujarati and English with closure protocol."""
    commander = OfflineCommander()

    # Gujarati query for Hunter 350 brake parts
    resp_gu = commander.execute_offline_turn("ચામુંડા હંટર 350 બ્રેક પાર્ટ શોધો")
    assert "ચામુંડા ઓટોમોબાઇલ રોયલ એનફિલ્ડ સ્પેર પાર્ટ્સ" in resp_gu
    assert "કામ સફળતાપૂર્વક પૂર્ણ થઈ ગયું છે" in resp_gu
    assert "બીજું કોઈ કામ છે" in resp_gu
    assert "નવો આઈડિયા/સજેશન" in resp_gu

    # English query for oil filter with English config
    commander.config.language = "english"
    resp_en = commander.execute_offline_turn("show royal enfield oil filter under 500")
    assert "Chamunda Automobile" in resp_en
    assert "Work completed successfully" in resp_en
    assert "Is there any other work for me" in resp_en

    # Part number lookup query
    resp_pn = commander.execute_offline_turn("ચામુંડા પાર્ટ નંબર 574050 બતાવો")
    assert "574050" in resp_pn


def test_search_parts_cli_execution():
    """Verify the CLI search tool search_parts_cli.py executes and returns valid filtered data."""
    import subprocess
    cmd = ["python3", "/home/alpesh/chamunda_re_enterprise/search_parts_cli.py", "--query", "oil filter", "--max-price", "500", "--json"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(proc.stdout)
    assert data["count"] > 0
    assert all(p["mrp"] <= 500 for p in data["items"])


def test_data_wise_filters_all_dimensions(inventory_manager):
    """Verify data-wise filters across all dimensions: part_no, model, category, price, cost, status, stock, bin, hsn, unit."""
    # 1. HSN code filter
    hsn_parts = inventory_manager.filter_parts(hsn_code="84212300")
    assert len(hsn_parts) > 0
    assert all("84212300" in p.get("hsn_code", "") for p in hsn_parts)

    # 2. Wholesale cost filter
    cost_parts = inventory_manager.filter_parts(min_cost=100, max_cost=500)
    assert len(cost_parts) > 0
    assert all(100 <= p.get("cost_price", 0) <= 500 for p in cost_parts)

    # 3. Bin location filter
    bin_parts = inventory_manager.filter_parts(bin_location="Rack A")
    assert len(bin_parts) > 0
    assert all("rack a" in p.get("bin_location", "").lower() for p in bin_parts)

    # 4. Out of stock filter
    oos_parts = inventory_manager.filter_parts(stock_status="out_of_stock")
    assert len(oos_parts) > 0
    assert all(p.get("stock", 0) == 0 for p in oos_parts)

    # 5. Low stock filter
    low_parts = inventory_manager.filter_parts(stock_status="low_stock")
    assert len(low_parts) > 0
    assert all(p.get("stock", 0) <= p.get("min_threshold", 5) for p in low_parts)

