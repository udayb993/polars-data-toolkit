"""Shared test helpers used across per-table test modules."""
from __future__ import annotations

import polars as pl

from common.io import path_for, read


def load(layer: str, name: str) -> pl.DataFrame:
    """Load a parquet table or fail with a clear message."""
    p = path_for(layer, name)
    assert p.exists(), f"missing {layer}/{name}.parquet — run the pipeline first"
    return read(layer, name)


def assert_no_duplicate_keys(df: pl.DataFrame, keys: list[str]) -> None:
    dup = df.group_by(keys).len().filter(pl.col("len") > 1)
    assert dup.height == 0, (
        f"duplicate keys on {keys}:\n{dup.head(5)}"
    )


def assert_columns_dtype(df: pl.DataFrame, expected: dict[str, pl.DataType]) -> None:
    for col, dtype in expected.items():
        assert col in df.columns, f"missing column {col}"
        actual = df.schema[col]
        assert actual == dtype, f"column {col}: expected {dtype}, got {actual}"


def assert_no_nulls(df: pl.DataFrame, cols: list[str]) -> None:
    for c in cols:
        n = df.select(pl.col(c).is_null().sum()).item()
        assert n == 0, f"column {c} has {n} unexpected nulls"


def assert_in_range(df: pl.DataFrame, col: str, lo, hi, *, allow_null: bool = True) -> None:
    expr = pl.col(col)
    if allow_null:
        bad = df.filter(expr.is_not_null() & ((expr < lo) | (expr > hi)))
    else:
        bad = df.filter(expr.is_null() | (expr < lo) | (expr > hi))
    assert bad.height == 0, (
        f"column {col} out of [{lo}, {hi}]; {bad.height} bad rows, sample:\n"
        f"{bad.select(col).head(5)}"
    )


def assert_values_subset(df: pl.DataFrame, col: str, allowed: set) -> None:
    seen = set(df[col].drop_nulls().unique().to_list())
    extra = seen - allowed
    assert not extra, f"column {col} has unexpected values: {sorted(extra)}"
