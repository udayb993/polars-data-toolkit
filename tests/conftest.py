"""Shared pytest fixtures for all tests."""
import json
from pathlib import Path
import pytest
import polars as pl


# ============================================================================
# RAW DATA FIXTURES (from extract layer)
# ============================================================================

@pytest.fixture
def raw_products():
    """Load raw products JSON from data/raw/products_raw.json."""
    filepath = Path(__file__).parent.parent / "data" / "raw" / "products_raw.json"
    if not filepath.exists():
        pytest.skip(f"Raw file not found: {filepath} - run extract step first")
    with open(filepath, "r") as f:
        return json.load(f)


@pytest.fixture
def raw_users():
    """Load raw users JSON from data/raw/users_raw.json."""
    filepath = Path(__file__).parent.parent / "data" / "raw" / "users_raw.json"
    if not filepath.exists():
        pytest.skip(f"Raw file not found: {filepath} - run extract step first")
    with open(filepath, "r") as f:
        return json.load(f)


@pytest.fixture
def raw_carts():
    """Load raw carts JSON from data/raw/carts_raw.json."""
    filepath = Path(__file__).parent.parent / "data" / "raw" / "carts_raw.json"
    if not filepath.exists():
        pytest.skip(f"Raw file not found: {filepath} - run extract step first")
    with open(filepath, "r") as f:
        return json.load(f)


@pytest.fixture
def raw_countries():
    """Load raw countries JSON from data/raw/countries_raw.json."""
    filepath = Path(__file__).parent.parent / "data" / "raw" / "countries_raw.json"
    if not filepath.exists():
        pytest.skip(f"Raw file not found: {filepath} - run extract step first")
    with open(filepath, "r") as f:
        return json.load(f)


# ============================================================================
# STAGED DATA FIXTURES (from transform layer)
# ============================================================================

@pytest.fixture
def staged_products():
    """Load staged products CSV from data/staged/products.csv."""
    filepath = Path(__file__).parent.parent / "data" / "staged" / "products.csv"
    if not filepath.exists():
        pytest.skip(f"Staged file not found: {filepath} - run transform step first")
    return pl.read_csv(filepath)


@pytest.fixture
def staged_customers():
    """Load staged customers CSV from data/staged/customers.csv."""
    filepath = Path(__file__).parent.parent / "data" / "staged" / "customers.csv"
    if not filepath.exists():
        pytest.skip(f"Staged file not found: {filepath} - run transform step first")
    return pl.read_csv(filepath)


@pytest.fixture
def staged_orders():
    """Load staged orders CSV from data/staged/orders.csv."""
    filepath = Path(__file__).parent.parent / "data" / "staged" / "orders.csv"
    if not filepath.exists():
        pytest.skip(f"Staged file not found: {filepath} - run transform step first")
    return pl.read_csv(filepath)


@pytest.fixture
def staged_order_items():
    """Load staged order_items CSV from data/staged/order_items.csv."""
    filepath = Path(__file__).parent.parent / "data" / "staged" / "order_items.csv"
    if not filepath.exists():
        pytest.skip(f"Staged file not found: {filepath} - run transform step first")
    return pl.read_csv(filepath)


@pytest.fixture
def staged_countries():
    """Load staged countries CSV from data/staged/countries.csv."""
    filepath = Path(__file__).parent.parent / "data" / "staged" / "countries.csv"
    if not filepath.exists():
        pytest.skip(f"Staged file not found: {filepath} - run transform step first")
    return pl.read_csv(filepath)


# ============================================================================
# MART DATA FIXTURES (from load layer)
# ============================================================================

@pytest.fixture
def mart_order_summary():
    """Load mart order_summary CSV from data/marts/order_summary.csv."""
    filepath = Path(__file__).parent.parent / "data" / "marts" / "order_summary.csv"
    if not filepath.exists():
        pytest.skip(f"Mart file not found: {filepath} - run load step first")
    return pl.read_csv(filepath)


@pytest.fixture
def mart_customer_ltv():
    """Load mart customer_ltv CSV from data/marts/customer_ltv.csv."""
    filepath = Path(__file__).parent.parent / "data" / "marts" / "customer_ltv.csv"
    if not filepath.exists():
        pytest.skip(f"Mart file not found: {filepath} - run load step first")
    return pl.read_csv(filepath)


@pytest.fixture
def mart_category_revenue():
    """Load mart category_revenue CSV from data/marts/category_revenue.csv."""
    filepath = Path(__file__).parent.parent / "data" / "marts" / "category_revenue.csv"
    if not filepath.exists():
        pytest.skip(f"Mart file not found: {filepath} - run load step first")
    return pl.read_csv(filepath)


@pytest.fixture
def mart_monthly_trend():
    """Load mart monthly_trend CSV from data/marts/monthly_trend.csv."""
    filepath = Path(__file__).parent.parent / "data" / "marts" / "monthly_trend.csv"
    if not filepath.exists():
        pytest.skip(f"Mart file not found: {filepath} - run load step first")
    return pl.read_csv(filepath)
