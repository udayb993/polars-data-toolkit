"""Tests for transform_products transform function."""
from pathlib import Path
import re
import pytest


def test_staged_products_file_exists():
    """Test that staged products CSV file exists."""
    filepath = Path(__file__).parent.parent.parent / "data" / "staged" / "products.csv"
    assert filepath.exists(), f"File {filepath} does not exist"


def test_staged_products_columns(staged_products):
    """Test that products CSV has correct columns."""
    expected_cols = ["product_id", "product_name", "category", "brand", "price",
                     "original_price", "discount_pct", "rating", "stock_quantity", "description"]
    assert list(staged_products.columns) == expected_cols, \
        f"Columns mismatch. Expected {expected_cols}, got {list(staged_products.columns)}"


def test_staged_products_row_count(staged_products):
    """Test that products has at least 1 row."""
    assert staged_products.height >= 1, "Products should have at least 1 row"


def test_staged_products_no_null_product_id(staged_products):
    """Test that product_id has no nulls."""
    assert staged_products.select("product_id").null_count()[0, 0] == 0, \
        "product_id should have no nulls"


def test_staged_products_product_id_unique(staged_products):
    """Test that product_ids are unique."""
    ids = staged_products.select("product_id").to_series().to_list()
    assert len(ids) == len(set(ids)), "product_id should be unique"


def test_staged_products_price_positive(staged_products):
    """Test that all prices are positive."""
    assert (staged_products.select("price") > 0).all()[0, 0], \
        "All prices should be > 0"


def test_staged_products_discount_pct_range(staged_products):
    """Test that discount_pct is between 0 and 100."""
    discount = staged_products.select("discount_pct")
    assert (discount >= 0).all()[0, 0] and (discount <= 100).all()[0, 0], \
        "discount_pct should be between 0 and 100"


def test_staged_products_rating_range(staged_products):
    """Test that rating is between 0 and 5."""
    rating = staged_products.select("rating")
    assert (rating >= 0).all()[0, 0] and (rating <= 5).all()[0, 0], \
        "rating should be between 0 and 5"


def test_staged_products_stock_non_negative(staged_products):
    """Test that stock_quantity is non-negative."""
    assert (staged_products.select("stock_quantity") >= 0).all()[0, 0], \
        "stock_quantity should be >= 0"


def test_staged_products_original_price_gte_price(staged_products):
    """Test that original_price >= price."""
    assert (staged_products.select("original_price") >= staged_products.select("price")).all()[0, 0], \
        "original_price should be >= price"


def test_staged_products_no_null_category(staged_products):
    """Test that category has no nulls."""
    assert staged_products.select("category").null_count()[0, 0] == 0, \
        "category should have no nulls"


def test_staged_products_brand_no_null(staged_products):
    """Test that brand has no nulls (should be filled)."""
    assert staged_products.select("brand").null_count()[0, 0] == 0, \
        "brand should have no nulls (should have been filled with 'Unknown')"
