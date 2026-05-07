"""Tests for marts.circuit_difficulty_index."""
from __future__ import annotations

import polars as pl

from tests._helpers import assert_in_range, assert_no_duplicate_keys, load


def test_cdi_primary_key_unique():
    df = load("marts", "circuit_difficulty_index")
    assert_no_duplicate_keys(df, ["circuit_id"])


def test_cdi_dnf_rate_in_unit_interval():
    df = load("marts", "circuit_difficulty_index")
    assert_in_range(df, "avg_dnf_rate", 0.0, 1.0)


def test_cdi_index_finite():
    df = load("marts", "circuit_difficulty_index")
    bad = df.filter(pl.col("difficulty_index").is_nan() | pl.col("difficulty_index").is_infinite())
    assert bad.height == 0
