"""Tests for transform_countries transform function."""
from pathlib import Path
import pytest


def test_staged_countries_file_exists():
    """Test that staged countries CSV file exists."""
    filepath = Path(__file__).parent.parent.parent / "data" / "staged" / "countries.csv"
    assert filepath.exists(), f"File {filepath} does not exist"


def test_staged_countries_columns(staged_countries):
    """Test that countries CSV has correct columns."""
    expected_cols = ["country_name", "official_name", "region", "subregion",
                     "population", "currency_code", "currency_name", "flag_emoji"]
    assert list(staged_countries.columns) == expected_cols, \
        f"Columns mismatch. Expected {expected_cols}, got {list(staged_countries.columns)}"


def test_staged_countries_not_empty(staged_countries):
    """Test that countries has at least 100 rows."""
    assert staged_countries.height >= 100, "Countries should have at least 100 rows"


def test_staged_countries_no_null_country_name(staged_countries):
    """Test that country_name has no nulls."""
    assert staged_countries.select("country_name").null_count()[0, 0] == 0, \
        "country_name should have no nulls"


def test_staged_countries_no_null_region(staged_countries):
    """Test that region has no nulls."""
    assert staged_countries.select("region").null_count()[0, 0] == 0, \
        "region should have no nulls"


def test_staged_countries_population_non_negative(staged_countries):
    """Test that all populations are non-negative."""
    assert (staged_countries.select("population") >= 0).all()[0, 0], \
        "population should be >= 0"


def test_staged_countries_subregion_no_null(staged_countries):
    """Test that subregion has no nulls (filled with Unknown)."""
    assert staged_countries.select("subregion").null_count()[0, 0] == 0, \
        "subregion should have no nulls (should be filled with 'Unknown')"


def test_staged_countries_currency_code_no_null(staged_countries):
    """Test that currency_code has no nulls (filled with Unknown)."""
    assert staged_countries.select("currency_code").null_count()[0, 0] == 0, \
        "currency_code should have no nulls (should be filled with 'Unknown')"


def test_staged_countries_region_valid_values(staged_countries):
    """Test that region values are in valid set."""
    valid_regions = {"Africa", "Americas", "Antarctic", "Asia", "Europe", "Oceania"}
    regions = staged_countries.select("region").to_series().unique().to_list()
    for region in regions:
        assert str(region) in valid_regions, \
            f"Invalid region: {region}. Should be one of {valid_regions}"
