"""
Tests for order data.
Validates schema, primary/foreign keys, and business logic for the orders table.
"""

import pytest
import polars as pl
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from generate_data.models import ORDER_SCHEMA


@pytest.fixture
def orders_df():
    """Load orders.csv for testing."""
    data_dir = Path(__file__).parent.parent / "data"
    df = pl.read_csv(str(data_dir / "orders.csv"))
    return df


@pytest.fixture
def customers_df():
    """Load customers.csv for testing."""
    data_dir = Path(__file__).parent.parent / "data"
    df = pl.read_csv(str(data_dir / "customers.csv"))
    return df


class TestOrdersSchema:
    """Test order data schema validation."""
    
    def test_schema_matches(self, orders_df):
        """Validate that the actual schema matches the expected schema."""
        expected_dtypes = ORDER_SCHEMA
        for col_name, expected_dtype in expected_dtypes.items():
            assert col_name in orders_df.columns, f"Missing column: {col_name}"
            actual_dtype = orders_df[col_name].dtype
            assert actual_dtype == expected_dtype, (
                f"Column {col_name}: expected {expected_dtype}, got {actual_dtype}"
            )
    
    def test_correct_number_of_columns(self, orders_df):
        """Validate expected number of columns."""
        assert len(orders_df.columns) == len(ORDER_SCHEMA)


class TestOrdersPrimaryKey:
    """Test primary key constraints."""
    
    def test_order_id_no_nulls(self, orders_df):
        """Assert order_id has no null values."""
        null_count = orders_df["order_id"].null_count()
        assert null_count == 0, f"order_id has {null_count} null values"
    
    def test_order_id_no_duplicates(self, orders_df):
        """Assert order_id has no duplicate values."""
        total = len(orders_df)
        unique_count = orders_df["order_id"].n_unique()
        assert total == unique_count, (
            f"Found {total - unique_count} duplicate order_ids"
        )


class TestOrdersForeignKey:
    """Test foreign key constraints."""
    
    def test_customer_id_exists_in_customers(self, orders_df, customers_df):
        """Assert all customer_id values in orders exist in customers."""
        valid_customer_ids = set(customers_df["customer_id"].unique().to_list())
        order_customer_ids = set(orders_df["customer_id"].unique().to_list())
        invalid_ids = order_customer_ids - valid_customer_ids
        assert len(invalid_ids) == 0, (
            f"Found {len(invalid_ids)} customer_ids in orders that don't exist in customers: {invalid_ids}"
        )


class TestOrdersBusinessLogic:
    """Test business logic and data quality."""
    
    def test_status_values_valid(self, orders_df):
        """Assert all status values are in the allowed set."""
        allowed_statuses = {"pending", "shipped", "delivered", "cancelled"}
        statuses = set(orders_df["status"].unique().to_list())
        invalid = statuses - allowed_statuses
        assert len(invalid) == 0, f"Invalid statuses found: {invalid}"
    
    def test_total_amount_non_negative(self, orders_df):
        """Assert total_amount >= 0."""
        min_amount = orders_df["total_amount"].min()
        assert min_amount >= 0, f"Found total_amount < 0: {min_amount}"
    
    def test_order_date_not_null(self, orders_df):
        """Assert order_date is not null."""
        null_count = orders_df["order_date"].null_count()
        assert null_count == 0, f"order_date has {null_count} null values"
    
    def test_customer_id_not_null(self, orders_df):
        """Assert customer_id is not null."""
        null_count = orders_df["customer_id"].null_count()
        assert null_count == 0, f"customer_id has {null_count} null values"
