"""Tests for transform_carts transform function."""
from pathlib import Path
import re
import pytest


# ============================================================================
# TESTS FOR ORDERS CSV
# ============================================================================

def test_staged_orders_file_exists():
    """Test that staged orders CSV file exists."""
    filepath = Path(__file__).parent.parent.parent / "data" / "staged" / "orders.csv"
    assert filepath.exists(), f"File {filepath} does not exist"


def test_staged_orders_columns(staged_orders):
    """Test that orders CSV has correct columns."""
    expected_cols = ["order_id", "customer_id", "total_products", "total_quantity",
                     "total_amount", "discounted_total", "discount_amount", "order_month"]
    assert list(staged_orders.columns) == expected_cols, \
        f"Columns mismatch. Expected {expected_cols}, got {list(staged_orders.columns)}"


def test_staged_orders_no_null_order_id(staged_orders):
    """Test that order_id has no nulls."""
    assert staged_orders.select("order_id").null_count()[0, 0] == 0, \
        "order_id should have no nulls"


def test_staged_orders_order_id_unique(staged_orders):
    """Test that order_ids are unique."""
    ids = staged_orders.select("order_id").to_series().to_list()
    assert len(ids) == len(set(ids)), "order_id should be unique"


def test_staged_orders_total_amount_positive(staged_orders):
    """Test that all total_amounts are positive."""
    assert (staged_orders.select("total_amount") > 0).all()[0, 0], \
        "total_amount should be > 0"


def test_staged_orders_discounted_lte_total(staged_orders):
    """Test that discounted_total <= total_amount."""
    assert (staged_orders.select("discounted_total") <= staged_orders.select("total_amount")).all()[0, 0], \
        "discounted_total should be <= total_amount"


def test_staged_orders_discount_amount_non_negative(staged_orders):
    """Test that discount_amount is non-negative."""
    assert (staged_orders.select("discount_amount") >= 0).all()[0, 0], \
        "discount_amount should be >= 0"


def test_staged_orders_customer_id_positive(staged_orders):
    """Test that all customer_ids are positive."""
    assert (staged_orders.select("customer_id") > 0).all()[0, 0], \
        "customer_id should be > 0"


def test_staged_orders_order_month_format(staged_orders):
    """Test that order_month matches YYYY-MM pattern."""
    pattern = r"^\d{4}-\d{2}$"
    months = staged_orders.select("order_month").to_series().to_list()
    for month in months:
        assert re.match(pattern, str(month)), \
            f"order_month '{month}' does not match YYYY-MM pattern"


# ============================================================================
# TESTS FOR ORDER_ITEMS CSV
# ============================================================================

def test_staged_order_items_file_exists():
    """Test that staged order_items CSV file exists."""
    filepath = Path(__file__).parent.parent.parent / "data" / "staged" / "order_items.csv"
    assert filepath.exists(), f"File {filepath} does not exist"


def test_staged_order_items_columns(staged_order_items):
    """Test that order_items CSV has correct columns."""
    expected_cols = ["order_item_id", "order_id", "product_id", "product_name",
                     "quantity", "unit_price", "discount_pct", "subtotal", "discounted_subtotal"]
    assert list(staged_order_items.columns) == expected_cols, \
        f"Columns mismatch. Expected {expected_cols}, got {list(staged_order_items.columns)}"


def test_staged_order_items_no_null_order_item_id(staged_order_items):
    """Test that order_item_id has no nulls."""
    assert staged_order_items.select("order_item_id").null_count()[0, 0] == 0, \
        "order_item_id should have no nulls"


def test_staged_order_items_order_item_id_unique(staged_order_items):
    """Test that order_item_ids are unique."""
    ids = staged_order_items.select("order_item_id").to_series().to_list()
    assert len(ids) == len(set(ids)), "order_item_id should be unique"


def test_staged_order_items_quantity_positive(staged_order_items):
    """Test that all quantities are >= 1."""
    assert (staged_order_items.select("quantity") >= 1).all()[0, 0], \
        "quantity should be >= 1"


def test_staged_order_items_unit_price_positive(staged_order_items):
    """Test that all unit_prices are positive."""
    assert (staged_order_items.select("unit_price") > 0).all()[0, 0], \
        "unit_price should be > 0"


def test_staged_order_items_subtotal_correct(staged_order_items):
    """Test that subtotal == quantity * unit_price."""
    calculated = staged_order_items.select("quantity") * staged_order_items.select("unit_price")
    actual = staged_order_items.select("subtotal")
    # Allow small tolerance for floating point
    diff = (calculated - actual).abs()
    assert (diff <= 0.01).all()[0, 0], "subtotal calculation is incorrect"


def test_staged_order_items_discounted_subtotal_lte_subtotal(staged_order_items):
    """Test that discounted_subtotal <= subtotal."""
    assert (staged_order_items.select("discounted_subtotal") <= staged_order_items.select("subtotal")).all()[0, 0], \
        "discounted_subtotal should be <= subtotal"


def test_staged_order_items_referential_integrity_order_id(staged_orders, staged_order_items):
    """Test that all order_ids in order_items exist in orders."""
    order_ids_orders = set(staged_orders.select("order_id").to_series().to_list())
    order_ids_items = set(staged_order_items.select("order_id").to_series().to_list())
    orphans = order_ids_items - order_ids_orders
    assert len(orphans) == 0, f"order_items has orphan order_ids: {orphans}"


def test_staged_order_items_referential_integrity_product_id(staged_products, staged_order_items):
    """Test that all product_ids in order_items exist in products."""
    product_ids_products = set(staged_products.select("product_id").to_series().to_list())
    product_ids_items = set(staged_order_items.select("product_id").to_series().to_list())
    orphans = product_ids_items - product_ids_products
    assert len(orphans) == 0, f"order_items has orphan product_ids: {orphans}"
