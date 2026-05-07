"""Tests for fetch_products extract function."""
from pathlib import Path
import pytest


def test_raw_products_file_exists():
    """Test that products raw JSON file exists."""
    filepath = Path(__file__).parent.parent.parent / "data" / "raw" / "products_raw.json"
    assert filepath.exists(), f"File {filepath} does not exist"


def test_raw_products_is_list(raw_products):
    """Test that raw products data is a list."""
    assert isinstance(raw_products, list), "Products data should be a list"


def test_raw_products_not_empty(raw_products):
    """Test that products list is not empty."""
    assert len(raw_products) > 0, "Products list should not be empty"


def test_raw_products_has_required_keys(raw_products):
    """Test that each product has required keys."""
    required_keys = {"id", "title", "category", "price", "stock", "rating", "discountPercentage"}
    for product in raw_products:
        assert required_keys.issubset(set(product.keys())), \
            f"Product missing required keys. Got: {set(product.keys())}"


def test_raw_products_id_unique(raw_products):
    """Test that product IDs are unique."""
    ids = [p["id"] for p in raw_products]
    assert len(ids) == len(set(ids)), "Product IDs should be unique"


def test_raw_products_price_positive(raw_products):
    """Test that all product prices are positive."""
    for product in raw_products:
        assert product["price"] > 0, f"Product {product['id']} has non-positive price"


def test_raw_products_stock_non_negative(raw_products):
    """Test that all product stock is non-negative."""
    for product in raw_products:
        assert product["stock"] >= 0, f"Product {product['id']} has negative stock"


def test_raw_products_rating_range(raw_products):
    """Test that all ratings are between 0 and 5."""
    for product in raw_products:
        assert 0 <= product["rating"] <= 5, \
            f"Product {product['id']} has rating {product['rating']} outside [0, 5]"
