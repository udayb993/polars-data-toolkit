"""Tests for order_summary mart."""
from pathlib import Path
import pytest


def test_mart_order_summary_file_exists():
    """Test that order_summary mart CSV file exists."""
    filepath = Path(__file__).parent.parent.parent / "data" / "marts" / "order_summary.csv"
    assert filepath.exists(), f"File {filepath} does not exist"


def test_mart_order_summary_columns(mart_order_summary):
    """Test that order_summary has correct columns."""
    expected_cols = ["order_id", "customer_id", "full_name", "email", "city",
                     "total_amount", "discounted_total", "discount_amount",
                     "total_products", "total_quantity", "order_month"]
    assert list(mart_order_summary.columns) == expected_cols, \
        f"Columns mismatch. Expected {expected_cols}, got {list(mart_order_summary.columns)}"


def test_mart_order_summary_no_null_order_id(mart_order_summary):
    """Test that order_id has no nulls."""
    assert mart_order_summary.select("order_id").null_count()[0, 0] == 0, \
        "order_id should have no nulls"


def test_mart_order_summary_order_id_unique(mart_order_summary):
    """Test that order_ids are unique."""
    ids = mart_order_summary.select("order_id").to_series().to_list()
    assert len(ids) == len(set(ids)), "order_id should be unique"


def test_mart_order_summary_no_null_customer_id(mart_order_summary):
    """Test that customer_id has no nulls."""
    assert mart_order_summary.select("customer_id").null_count()[0, 0] == 0, \
        "customer_id should have no nulls"


def test_mart_order_summary_no_null_full_name(mart_order_summary):
    """Test that full_name has no nulls."""
    assert mart_order_summary.select("full_name").null_count()[0, 0] == 0, \
        "full_name should have no nulls"


def test_mart_order_summary_total_amount_positive(mart_order_summary):
    """Test that all total_amounts are positive."""
    assert (mart_order_summary.select("total_amount") > 0).all()[0, 0], \
        "total_amount should be > 0"


def test_mart_order_summary_discounted_lte_total(mart_order_summary):
    """Test that discounted_total <= total_amount."""
    assert (mart_order_summary.select("discounted_total") <= mart_order_summary.select("total_amount")).all()[0, 0], \
        "discounted_total should be <= total_amount"


def test_mart_order_summary_row_count_matches_orders(staged_orders, mart_order_summary):
    """Test that row count matches staged orders."""
    assert mart_order_summary.height == staged_orders.height, \
        f"Row count should match staged orders ({staged_orders.height}), got {mart_order_summary.height}"
