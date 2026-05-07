"""Tests for customer_ltv mart."""
from pathlib import Path
import pytest


def test_mart_customer_ltv_file_exists():
    """Test that customer_ltv mart CSV file exists."""
    filepath = Path(__file__).parent.parent.parent / "data" / "marts" / "customer_ltv.csv"
    assert filepath.exists(), f"File {filepath} does not exist"


def test_mart_customer_ltv_columns(mart_customer_ltv):
    """Test that customer_ltv has correct columns."""
    expected_cols = ["customer_id", "full_name", "email", "city", "total_orders",
                     "total_spent", "avg_order_value", "total_items_bought", "ltv_segment"]
    assert list(mart_customer_ltv.columns) == expected_cols, \
        f"Columns mismatch. Expected {expected_cols}, got {list(mart_customer_ltv.columns)}"


def test_mart_customer_ltv_no_null_customer_id(mart_customer_ltv):
    """Test that customer_id has no nulls."""
    assert mart_customer_ltv.select("customer_id").null_count()[0, 0] == 0, \
        "customer_id should have no nulls"


def test_mart_customer_ltv_customer_id_unique(mart_customer_ltv):
    """Test that customer_ids are unique."""
    ids = mart_customer_ltv.select("customer_id").to_series().to_list()
    assert len(ids) == len(set(ids)), "customer_id should be unique"


def test_mart_customer_ltv_total_orders_positive(mart_customer_ltv):
    """Test that all total_orders are >= 1."""
    assert (mart_customer_ltv.select("total_orders") >= 1).all()[0, 0], \
        "total_orders should be >= 1"


def test_mart_customer_ltv_total_spent_non_negative(mart_customer_ltv):
    """Test that total_spent is non-negative."""
    assert (mart_customer_ltv.select("total_spent") >= 0).all()[0, 0], \
        "total_spent should be >= 0"


def test_mart_customer_ltv_avg_order_value_positive(mart_customer_ltv):
    """Test that avg_order_value is positive."""
    assert (mart_customer_ltv.select("avg_order_value") > 0).all()[0, 0], \
        "avg_order_value should be > 0"


def test_mart_customer_ltv_ltv_segment_valid(mart_customer_ltv):
    """Test that ltv_segment values are valid."""
    segments = mart_customer_ltv.select("ltv_segment").to_series().unique().to_list()
    valid_segments = {"High", "Medium", "Low"}
    for segment in segments:
        assert str(segment) in valid_segments, \
            f"Invalid ltv_segment: {segment}. Should be one of {valid_segments}"


def test_mart_customer_ltv_segment_logic_high(mart_customer_ltv):
    """Test that all High segment customers have total_spent > 1000."""
    high_customers = mart_customer_ltv.filter(mart_customer_ltv["ltv_segment"] == "High")
    if high_customers.height > 0:
        assert (high_customers.select("total_spent") > 1000).all()[0, 0], \
            "All High segment customers should have total_spent > 1000"


def test_mart_customer_ltv_segment_logic_low(mart_customer_ltv):
    """Test that all Low segment customers have total_spent < 500."""
    low_customers = mart_customer_ltv.filter(mart_customer_ltv["ltv_segment"] == "Low")
    if low_customers.height > 0:
        assert (low_customers.select("total_spent") < 500).all()[0, 0], \
            "All Low segment customers should have total_spent < 500"


def test_mart_customer_ltv_total_items_positive(mart_customer_ltv):
    """Test that total_items_bought is positive."""
    assert (mart_customer_ltv.select("total_items_bought") >= 1).all()[0, 0], \
        "total_items_bought should be >= 1"
