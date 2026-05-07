"""Tests for transform_users transform function."""
from pathlib import Path
import pytest


def test_staged_customers_file_exists():
    """Test that staged customers CSV file exists."""
    filepath = Path(__file__).parent.parent.parent / "data" / "staged" / "customers.csv"
    assert filepath.exists(), f"File {filepath} does not exist"


def test_staged_customers_columns(staged_customers):
    """Test that customers CSV has correct columns."""
    expected_cols = ["customer_id", "first_name", "last_name", "full_name", "email",
                     "age", "gender", "city", "country", "phone", "username"]
    assert list(staged_customers.columns) == expected_cols, \
        f"Columns mismatch. Expected {expected_cols}, got {list(staged_customers.columns)}"


def test_staged_customers_row_count(staged_customers):
    """Test that customers has at least 1 row."""
    assert staged_customers.height >= 1, "Customers should have at least 1 row"


def test_staged_customers_no_null_customer_id(staged_customers):
    """Test that customer_id has no nulls."""
    assert staged_customers.select("customer_id").null_count()[0, 0] == 0, \
        "customer_id should have no nulls"


def test_staged_customers_customer_id_unique(staged_customers):
    """Test that customer_ids are unique."""
    ids = staged_customers.select("customer_id").to_series().to_list()
    assert len(ids) == len(set(ids)), "customer_id should be unique"


def test_staged_customers_email_not_null(staged_customers):
    """Test that email has no nulls."""
    assert staged_customers.select("email").null_count()[0, 0] == 0, \
        "email should have no nulls"


def test_staged_customers_full_name_not_null(staged_customers):
    """Test that full_name has no nulls."""
    assert staged_customers.select("full_name").null_count()[0, 0] == 0, \
        "full_name should have no nulls"


def test_staged_customers_full_name_contains_space(staged_customers):
    """Test that every full_name contains at least one space."""
    full_names = staged_customers.select("full_name").to_series().to_list()
    for name in full_names:
        assert " " in str(name), f"full_name '{name}' should contain a space"


def test_staged_customers_age_valid(staged_customers):
    """Test that all ages are between 18 and 100."""
    age = staged_customers.select("age")
    assert (age >= 18).all()[0, 0] and (age <= 100).all()[0, 0], \
        "age should be between 18 and 100"


def test_staged_customers_gender_valid(staged_customers):
    """Test that gender values are in valid set."""
    genders = staged_customers.select("gender").to_series().unique().to_list()
    valid_genders = {"male", "female", "other"}
    for gender in genders:
        assert str(gender).lower() in valid_genders, f"Invalid gender: {gender}"


def test_staged_customers_no_null_city(staged_customers):
    """Test that city has no nulls."""
    assert staged_customers.select("city").null_count()[0, 0] == 0, \
        "city should have no nulls"
