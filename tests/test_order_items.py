"""
Tests for order items data.
Validates schema, primary/foreign keys, and business logic for the order_items table.
"""

import pytest
import polars as pl
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from generate_data.models import ORDER_ITEM_SCHEMA


@pytest.fixture
def order_items_df():
    """Load order_items.csv for testing."""
    data_dir = Path(__file__).parent.parent / "data"
    df = pl.read_csv(str(data_dir / "order_items.csv"))
    return df


@pytest.fixture
def orders_df():
    """Load orders.csv for testing."""
    data_dir = Path(__file__).parent.parent / "data"
    df = pl.read_csv(str(data_dir / "orders.csv"))
    return df


@pytest.fixture
def products_df():
    """Load products.csv for testing."""
    data_dir = Path(__file__).parent.parent / "data"
    df = pl.read_csv(str(data_dir / "products.csv"))
    return df


class TestOrderItemsSchema:
    """Test order items data schema validation."""
    
    def test_schema_matches(self, order_items_df):
        """Validate that the actual schema matches the expected schema."""
        expected_dtypes = ORDER_ITEM_SCHEMA
        for col_name, expected_dtype in expected_dtypes.items():
            assert col_name in order_items_df.columns, f"Missing column: {col_name}"
            actual_dtype = order_items_df[col_name].dtype
            assert actual_dtype == expected_dtype, (
                f"Column {col_name}: expected {expected_dtype}, got {actual_dtype}"
            )
    
    def test_correct_number_of_columns(self, order_items_df):
        """Validate expected number of columns."""
        assert len(order_items_df.columns) == len(ORDER_ITEM_SCHEMA)


class TestOrderItemsPrimaryKey:
    """Test primary key constraints."""
    
    def test_order_item_id_no_nulls(self, order_items_df):
        """Assert order_item_id has no null values."""
        null_count = order_items_df["order_item_id"].null_count()
        assert null_count == 0, f"order_item_id has {null_count} null values"
    
    def test_order_item_id_no_duplicates(self, order_items_df):
        """Assert order_item_id has no duplicate values."""
        total = len(order_items_df)
        unique_count = order_items_df["order_item_id"].n_unique()
        assert total == unique_count, (
            f"Found {total - unique_count} duplicate order_item_ids"
        )


class TestOrderItemsForeignKeys:
    """Test foreign key constraints."""
    
    def test_order_id_exists_in_orders(self, order_items_df, orders_df):
        """Assert all order_id values exist in orders."""
        valid_order_ids = set(orders_df["order_id"].unique().to_list())
        item_order_ids = set(order_items_df["order_id"].unique().to_list())
        invalid_ids = item_order_ids - valid_order_ids
        assert len(invalid_ids) == 0, (
            f"Found {len(invalid_ids)} order_ids that don't exist in orders: {invalid_ids}"
        )
    
    def test_product_id_exists_in_products(self, order_items_df, products_df):
        """Assert all product_id values exist in products."""
        valid_product_ids = set(products_df["product_id"].unique().to_list())
        item_product_ids = set(order_items_df["product_id"].unique().to_list())
        invalid_ids = item_product_ids - valid_product_ids
        assert len(invalid_ids) == 0, (
            f"Found {len(invalid_ids)} product_ids that don't exist in products: {invalid_ids}"
        )


class TestOrderItemsBusinessLogic:
    """Test business logic and data quality."""
    
    def test_subtotal_calculation(self, order_items_df):
        """Assert subtotal == quantity * unit_price for every row."""
        # Allow small floating point tolerance
        tolerance = 0.01
        
        calculated_subtotal = order_items_df["quantity"] * order_items_df["unit_price"]
        differences = (calculated_subtotal - order_items_df["subtotal"]).abs()
        
        max_diff = differences.max()
        assert max_diff <= tolerance, (
            f"Found subtotal calculation errors > {tolerance}: max difference = {max_diff}"
        )
    
    def test_quantity_at_least_one(self, order_items_df):
        """Assert quantity >= 1."""
        min_quantity = order_items_df["quantity"].min()
        assert min_quantity >= 1, f"Found quantity < 1: {min_quantity}"
    
    def test_unit_price_positive(self, order_items_df):
        """Assert unit_price > 0."""
        min_price = order_items_df["unit_price"].min()
        assert min_price > 0, f"Found unit_price <= 0: {min_price}"
    
    def test_subtotal_positive(self, order_items_df):
        """Assert subtotal > 0."""
        min_subtotal = order_items_df["subtotal"].min()
        assert min_subtotal > 0, f"Found subtotal <= 0: {min_subtotal}"
    
    def test_no_nulls_in_key_columns(self, order_items_df):
        """Assert no null values in key columns."""
        key_columns = ["order_item_id", "order_id", "product_id", "quantity", "unit_price", "subtotal"]
        for col in key_columns:
            null_count = order_items_df[col].null_count()
            assert null_count == 0, f"{col} has {null_count} null values"
