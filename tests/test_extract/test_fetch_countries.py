"""Tests for fetch_carts extract function."""
from pathlib import Path
import pytest


def test_raw_carts_file_exists():
    """Test that carts raw JSON file exists."""
    filepath = Path(__file__).parent.parent.parent / "data" / "raw" / "carts_raw.json"
    assert filepath.exists(), f"File {filepath} does not exist"


def test_raw_carts_is_list(raw_carts):
    """Test that raw carts data is a list."""
    assert isinstance(raw_carts, list), "Carts data should be a list"


def test_raw_carts_not_empty(raw_carts):
    """Test that carts list is not empty."""
    assert len(raw_carts) > 0, "Carts list should not be empty"


def test_raw_carts_has_required_keys(raw_carts):
    """Test that each cart has required keys."""
    required_keys = {"id", "userId", "total", "discountedTotal", "totalProducts", "totalQuantity", "products"}
    for cart in raw_carts:
        assert required_keys.issubset(set(cart.keys())), \
            f"Cart missing required keys. Got: {set(cart.keys())}"


def test_raw_carts_id_unique(raw_carts):
    """Test that cart IDs are unique."""
    ids = [c["id"] for c in raw_carts]
    assert len(ids) == len(set(ids)), "Cart IDs should be unique"


def test_raw_carts_products_is_list(raw_carts):
    """Test that products field is always a list."""
    for cart in raw_carts:
        assert isinstance(cart.get("products"), list), \
            f"Cart {cart['id']} products field is not a list"


def test_raw_carts_products_not_empty(raw_carts):
    """Test that every cart has at least one product."""
    for cart in raw_carts:
        assert len(cart["products"]) > 0, \
            f"Cart {cart['id']} has no products"


def test_raw_carts_total_positive(raw_carts):
    """Test that all cart totals are positive."""
    for cart in raw_carts:
        assert cart["total"] > 0, f"Cart {cart['id']} has non-positive total"


def test_raw_carts_discounted_lte_total(raw_carts):
    """Test that discountedTotal <= total for every cart."""
    for cart in raw_carts:
        assert cart["discountedTotal"] <= cart["total"], \
            f"Cart {cart['id']} discountedTotal > total"


def test_raw_carts_userid_positive(raw_carts):
    """Test that all userIds are positive."""
    for cart in raw_carts:
        assert cart["userId"] > 0, f"Cart {cart['id']} has non-positive userId"
