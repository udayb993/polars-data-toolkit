"""Tests for silver.sprint_results (skipped if no sprint data)."""
from __future__ import annotations

import polars as pl
import pytest

from common.io import path_for, read
from tests._helpers import (
    assert_columns_dtype,
    assert_in_range,
    assert_no_duplicate_keys,
    assert_no_nulls,
)

pytestmark = pytest.mark.skipif(
    not path_for("silver", "sprint_results").exists()
    or read("silver", "sprint_results").width == 0,
    reason="no sprint data for the configured seasons",
)


def _df() -> pl.DataFrame:
    return read("silver", "sprint_results")


def test_sprint_min_rows():
    assert _df().height >= 20


def test_sprint_primary_key_unique():
    assert_no_duplicate_keys(_df(), ["race_id", "driver_id"])


def test_sprint_dtypes():
    assert_columns_dtype(_df(), {
        "race_id":         pl.Utf8,
        "driver_id":       pl.Utf8,
        "constructor_id":  pl.Utf8,
        "grid_position":   pl.Int32,
        "finish_position": pl.Int32,
        "sprint_points":   pl.Float64,
        "finished_flag":   pl.Boolean,
        "sprint_time":     pl.Duration("us"),
    })


def test_sprint_points_in_range():
    # Sprint awards 0..8 points (P1=8); FL bonus not awarded for sprints.
    assert_in_range(_df(), "sprint_points", 0.0, 8.0)


def test_sprint_position_in_range():
    assert_in_range(_df(), "finish_position", 1, 30)


def test_sprint_no_nulls_on_keys():
    assert_no_nulls(_df(), ["race_id", "driver_id", "constructor_id"])
