"""Tests for category_revenue mart."""
from pathlib import Path
import pytest


def test_mart_category_revenue_file_exists():
    """Test that category_revenue mart CSV file exists."""
    filepath = Path(__file__).parent.parent.parent / "data" / "marts" / "category_revenue.csv"
    assert filepath.exists(), f"File {filepath} does not exist"


def test_mart_category_revenue_columns(mart_category_revenue):
    """Test that category_revenue has correct columns."""
    expected_cols = ["category", "total_orders", "total_units_sold", "gross_revenue",
                     "discounted_revenue", "total_discount_given", "avg_unit_price",
                     "avg_discount_pct", "top_product"]
    assert list(mart_category_revenue.columns) == expected_cols, \
        f"Columns mismatch. Expected {expected_cols}, got {list(mart_category_revenue.columns)}"


def test_mart_category_revenue_no_null_category(mart_category_revenue):
    """Test that category has no nulls."""
    assert mart_category_revenue.select("category").null_count()[0, 0] == 0, \
        "category should have no nulls"


def test_mart_category_revenue_category_unique(mart_category_revenue):
    """Test that categories are unique."""
    categories = mart_category_revenue.select("category").to_series().to_list()
    assert len(categories) == len(set(categories)), "categories should be unique"


def test_mart_category_revenue_gross_revenue_positive(mart_category_revenue):
    """Test that gross_revenue is positive."""
    assert (mart_category_revenue.select("gross_revenue") > 0).all()[0, 0], \
        "gross_revenue should be > 0"


def test_mart_category_revenue_discounted_lte_gross(mart_category_revenue):
    """Test that discounted_revenue <= gross_revenue."""
    assert (mart_category_revenue.select("discounted_revenue") <= mart_category_revenue.select("gross_revenue")).all()[0, 0], \
        "discounted_revenue should be <= gross_revenue"


def test_mart_category_revenue_discount_given_non_negative(mart_category_revenue):
    """Test that total_discount_given is non-negative."""
    assert (mart_category_revenue.select("total_discount_given") >= 0).all()[0, 0], \
        "total_discount_given should be >= 0"


def test_mart_category_revenue_units_sold_positive(mart_category_revenue):
    """Test that total_units_sold is >= 1."""
    assert (mart_category_revenue.select("total_units_sold") >= 1).all()[0, 0], \
        "total_units_sold should be >= 1"


def test_mart_category_revenue_avg_price_positive(mart_category_revenue):
    """Test that avg_unit_price is positive."""
    assert (mart_category_revenue.select("avg_unit_price") > 0).all()[0, 0], \
        "avg_unit_price should be > 0"


def test_mart_category_revenue_top_product_not_null(mart_category_revenue):
    """Test that top_product has no nulls."""
    assert mart_category_revenue.select("top_product").null_count()[0, 0] == 0, \
        "top_product should have no nulls"
