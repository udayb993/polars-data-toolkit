"""
Tests for customer data.
Validates schema, primary keys, and business logic for the customers table.
"""

import pytest
import polars as pl
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from generate_data.models import CUSTOMER_SCHEMA


@pytest.fixture
def customers_df():
    """Load customers.csv for testing."""
    data_dir = Path(__file__).parent.parent / "data"
    df = pl.read_csv(str(data_dir / "customers.csv"))
    return df


class TestCustomersSchema:
    """Test customer data schema validation."""
    
    def test_schema_matches(self, customers_df):
        """Validate that the actual schema matches the expected schema."""
        expected_dtypes = CUSTOMER_SCHEMA
        for col_name, expected_dtype in expected_dtypes.items():
            assert col_name in customers_df.columns, f"Missing column: {col_name}"
            actual_dtype = customers_df[col_name].dtype
            assert actual_dtype == expected_dtype, (
                f"Column {col_name}: expected {expected_dtype}, got {actual_dtype}"
            )
    
    def test_correct_number_of_columns(self, customers_df):
        """Validate expected number of columns."""
        assert len(customers_df.columns) == len(CUSTOMER_SCHEMA)


class TestCustomersPrimaryKey:
    """Test primary key constraints."""
    
    def test_customer_id_no_nulls(self, customers_df):
        """Assert customer_id has no null values."""
        null_count = customers_df["customer_id"].null_count()
        assert null_count == 0, f"customer_id has {null_count} null values"
    
    def test_customer_id_no_duplicates(self, customers_df):
        """Assert customer_id has no duplicate values."""
        total = len(customers_df)
        unique_count = customers_df["customer_id"].n_unique()
        assert total == unique_count, (
            f"Found {total - unique_count} duplicate customer_ids"
        )


class TestCustomersBusinessLogic:
    """Test business logic and data quality."""
    
    def test_country_values_valid(self, customers_df):
        """Assert all country values are in the allowed set."""
        allowed_countries = {"UK", "US", "Germany", "France", "India"}
        countries = set(customers_df["country"].unique().to_list())
        invalid = countries - allowed_countries
        assert len(invalid) == 0, f"Invalid countries found: {invalid}"
    
    def test_signup_date_not_null(self, customers_df):
        """Assert signup_date is not null for any row."""
        null_count = customers_df["signup_date"].null_count()
        assert null_count == 0, f"signup_date has {null_count} null values"
    
    def test_is_active_is_boolean(self, customers_df):
        """Assert is_active column is boolean type."""
        assert customers_df["is_active"].dtype == pl.Boolean, (
            f"is_active dtype is {customers_df['is_active'].dtype}, expected Boolean"
        )
    
    def test_email_not_null(self, customers_df):
        """Assert email is not null for any row."""
        null_count = customers_df["email"].null_count()
        assert null_count == 0, f"email has {null_count} null values"
