"""Tests for monthly_trend mart."""
from pathlib import Path
import re
import pytest


def test_mart_monthly_trend_file_exists():
    """Test that monthly_trend mart CSV file exists."""
    filepath = Path(__file__).parent.parent.parent / "data" / "marts" / "monthly_trend.csv"
    assert filepath.exists(), f"File {filepath} does not exist"


def test_mart_monthly_trend_columns(mart_monthly_trend):
    """Test that monthly_trend has correct columns."""
    expected_cols = ["order_month", "total_orders", "total_revenue",
                     "total_discounted_revenue", "total_discount_given",
                     "avg_order_value", "avg_discount_pct"]
    assert list(mart_monthly_trend.columns) == expected_cols, \
        f"Columns mismatch. Expected {expected_cols}, got {list(mart_monthly_trend.columns)}"


def test_mart_monthly_trend_no_null_month(mart_monthly_trend):
    """Test that order_month has no nulls."""
    assert mart_monthly_trend.select("order_month").null_count()[0, 0] == 0, \
        "order_month should have no nulls"


def test_mart_monthly_trend_month_unique(mart_monthly_trend):
    """Test that months are unique."""
    months = mart_monthly_trend.select("order_month").to_series().to_list()
    assert len(months) == len(set(months)), "months should be unique"


def test_mart_monthly_trend_month_format(mart_monthly_trend):
    """Test that order_month matches YYYY-MM pattern."""
    pattern = r"^\d{4}-\d{2}$"
    months = mart_monthly_trend.select("order_month").to_series().to_list()
    for month in months:
        assert re.match(pattern, str(month)), \
            f"order_month '{month}' does not match YYYY-MM pattern"


def test_mart_monthly_trend_total_orders_positive(mart_monthly_trend):
    """Test that total_orders is positive."""
    assert (mart_monthly_trend.select("total_orders") > 0).all()[0, 0], \
        "total_orders should be > 0"


def test_mart_monthly_trend_total_revenue_positive(mart_monthly_trend):
    """Test that total_revenue is positive."""
    assert (mart_monthly_trend.select("total_revenue") > 0).all()[0, 0], \
        "total_revenue should be > 0"


def test_mart_monthly_trend_discounted_lte_total(mart_monthly_trend):
    """Test that total_discounted_revenue <= total_revenue."""
    assert (mart_monthly_trend.select("total_discounted_revenue") <= mart_monthly_trend.select("total_revenue")).all()[0, 0], \
        "total_discounted_revenue should be <= total_revenue"


def test_mart_monthly_trend_discount_pct_range(mart_monthly_trend):
    """Test that avg_discount_pct is between 0 and 100."""
    pct = mart_monthly_trend.select("avg_discount_pct")
    assert (pct >= 0).all()[0, 0] and (pct <= 100).all()[0, 0], \
        "avg_discount_pct should be between 0 and 100"


def test_mart_monthly_trend_sorted_ascending(mart_monthly_trend):
    """Test that order_month is sorted ascending."""
    months = mart_monthly_trend.select("order_month").to_series().to_list()
    assert months == sorted(months), "order_month should be sorted in ascending order"
