"""Tests for marts.dnf_analysis."""
from __future__ import annotations

import polars as pl

from tests._helpers import assert_in_range, assert_no_duplicate_keys, load


def test_dnf_primary_key_unique():
    df = load("marts", "dnf_analysis")
    assert_no_duplicate_keys(df, ["season", "constructor_id"])


def test_dnf_reliability_in_unit_interval():
    df = load("marts", "dnf_analysis")
    assert_in_range(df, "reliability", 0.0, 1.0)


def test_dnf_finished_le_starts():
    df = load("marts", "dnf_analysis")
    bad = df.filter(pl.col("n_finished") > pl.col("n_starts"))
    assert bad.height == 0
