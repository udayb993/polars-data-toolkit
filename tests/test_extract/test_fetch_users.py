"""Tests for fetch_users extract function."""
from pathlib import Path
import pytest


def test_raw_users_file_exists():
    """Test that users raw JSON file exists."""
    filepath = Path(__file__).parent.parent.parent / "data" / "raw" / "users_raw.json"
    assert filepath.exists(), f"File {filepath} does not exist"


def test_raw_users_is_list(raw_users):
    """Test that raw users data is a list."""
    assert isinstance(raw_users, list), "Users data should be a list"


def test_raw_users_not_empty(raw_users):
    """Test that users list is not empty."""
    assert len(raw_users) > 0, "Users list should not be empty"


def test_raw_users_has_required_keys(raw_users):
    """Test that each user has required keys."""
    required_keys = {"id", "firstName", "lastName", "email", "age", "gender", "address", "phone", "username"}
    for user in raw_users:
        assert required_keys.issubset(set(user.keys())), \
            f"User missing required keys. Got: {set(user.keys())}"


def test_raw_users_id_unique(raw_users):
    """Test that user IDs are unique."""
    ids = [u["id"] for u in raw_users]
    assert len(ids) == len(set(ids)), "User IDs should be unique"


def test_raw_users_email_not_null(raw_users):
    """Test that no user has null or empty email."""
    for user in raw_users:
        assert user.get("email") and len(str(user["email"])) > 0, \
            f"User {user['id']} has null or empty email"


def test_raw_users_age_valid(raw_users):
    """Test that all ages are between 18 and 100."""
    for user in raw_users:
        age = user["age"]
        assert 18 <= age <= 100, \
            f"User {user['id']} has invalid age {age}"


def test_raw_users_address_has_city(raw_users):
    """Test that every address dict has a city key."""
    for user in raw_users:
        address = user.get("address")
        assert address is not None, f"User {user['id']} has no address"
        assert "city" in address, f"User {user['id']} address has no city key"
