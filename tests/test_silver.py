"""Smoke tests on silver: every table exists, has rows, has the expected key."""
from __future__ import annotations

import pytest

from common.io import path_for, read

EXPECTED = {
    "seasons":               (["season"],                              1),
    "circuits":              (["circuit_id"],                          5),
    "drivers":               (["driver_id"],                           10),
    "constructors":          (["constructor_id"],                      5),
    "status":                (["status_id"],                           20),
    "races":                 (["race_id"],                             10),
    "results":               (["race_id", "driver_id"],                100),
    "qualifying":            (["race_id", "driver_id"],                100),
    "driver_standings":      (["season", "driver_id"],                 5),
    "constructor_standings": (["season", "constructor_id"],            5),
    "pit_stops":             (["race_id", "driver_id", "stop_number"], 50),
    "lap_times":             (["race_id", "driver_id", "lap"],         500),
}


@pytest.mark.parametrize("name,expected", list(EXPECTED.items()))
def test_silver_table(name: str, expected: tuple[list[str], int]):
    keys, min_rows = expected
    p = path_for("silver", name)
    assert p.exists(), f"missing silver {name}"
    df = read("silver", name)
    assert df.height >= min_rows, f"{name} too few rows: {df.height}"
    for k in keys:
        assert k in df.columns, f"{name} missing key {k}"
    # Composite-key uniqueness.
    assert df.select(keys).n_unique() == df.height, f"{name} duplicate keys on {keys}"
