"""
Tests for product data.
Validates schema, primary keys, and business logic for the products table.
"""

import pytest
import polars as pl
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from generate_data.models import PRODUCT_SCHEMA


@pytest.fixture
def products_df():
    """Load products.csv for testing."""
    data_dir = Path(__file__).parent.parent / "data"
    df = pl.read_csv(str(data_dir / "products.csv"))
    return df


class TestProductsSchema:
    """Test product data schema validation."""
    
    def test_schema_matches(self, products_df):
        """Validate that the actual schema matches the expected schema."""
        expected_dtypes = PRODUCT_SCHEMA
        for col_name, expected_dtype in expected_dtypes.items():
            assert col_name in products_df.columns, f"Missing column: {col_name}"
            actual_dtype = products_df[col_name].dtype
            assert actual_dtype == expected_dtype, (
                f"Column {col_name}: expected {expected_dtype}, got {actual_dtype}"
            )
    
    def test_correct_number_of_columns(self, products_df):
        """Validate expected number of columns."""
        assert len(products_df.columns) == len(PRODUCT_SCHEMA)


class TestProductsPrimaryKey:
    """Test primary key constraints."""
    
    def test_product_id_no_nulls(self, products_df):
        """Assert product_id has no null values."""
        null_count = products_df["product_id"].null_count()
        assert null_count == 0, f"product_id has {null_count} null values"
    
    def test_product_id_no_duplicates(self, products_df):
        """Assert product_id has no duplicate values."""
        total = len(products_df)
        unique_count = products_df["product_id"].n_unique()
        assert total == unique_count, (
            f"Found {total - unique_count} duplicate product_ids"
        )


class TestProductsBusinessLogic:
    """Test business logic and data quality."""
    
    def test_price_always_positive(self, products_df):
        """Assert price is always > 0."""
        min_price = products_df["price"].min()
        assert min_price > 0, f"Found price <= 0: {min_price}"
    
    def test_category_values_valid(self, products_df):
        """Assert all category values are in the allowed set."""
        allowed_categories = {"Electronics", "Clothing", "Books", "Home", "Sports"}
        categories = set(products_df["category"].unique().to_list())
        invalid = categories - allowed_categories
        assert len(invalid) == 0, f"Invalid categories found: {invalid}"
    
    def test_stock_quantity_non_negative(self, products_df):
        """Assert stock_quantity >= 0."""
        min_stock = products_df["stock_quantity"].min()
        assert min_stock >= 0, f"Found stock_quantity < 0: {min_stock}"
    
    def test_product_name_not_null(self, products_df):
        """Assert product_name is not null."""
        null_count = products_df["product_name"].null_count()
        assert null_count == 0, f"product_name has {null_count} null values"
