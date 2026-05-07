"""Shared expression helpers used across silver transforms.

These exist so multiple silver scripts express the same parsing logic the
same way (e.g. lap-time strings → Duration).  They are intentionally
``pl.Expr``-returning so they compose inside ``select`` / ``with_columns``.
"""
from __future__ import annotations

import polars as pl


def parse_lap_time(col: str = "time") -> pl.Expr:
    """Parse Ergast lap-time strings → Duration.

    Accepted forms: ``"1:31.295"``, ``"31.295"``, ``"1:23:45.678"`` (rare).
    Anything else → null.  Stored as Duration so we can do real arithmetic
    (subtract, mean, quantile).

    Note: ``when/then/otherwise`` evaluates all branches; pass
    ``null_on_oob=True`` to ``list.get`` so out-of-bounds index in the unused
    branch yields null rather than raising.
    """
    s = pl.col(col).cast(pl.Utf8).str.strip_chars()
    parts = s.str.split(":")
    g0 = parts.list.get(0, null_on_oob=True).cast(pl.Float64, strict=False)
    g1 = parts.list.get(1, null_on_oob=True).cast(pl.Float64, strict=False)
    g2 = parts.list.get(2, null_on_oob=True).cast(pl.Float64, strict=False)
    n = parts.list.len()
    h = pl.when(n == 3).then(g0).otherwise(0.0)
    m = (
        pl.when(n == 3).then(g1)
        .when(n == 2).then(g0)
        .otherwise(0.0)
    )
    sec = (
        pl.when(n == 3).then(g2)
        .when(n == 2).then(g1)
        .otherwise(g0)
    )
    total_us = ((h * 3600.0 + m * 60.0 + sec) * 1_000_000).cast(pl.Int64, strict=False)
    return pl.duration(microseconds=total_us)


def parse_int(col: str) -> pl.Expr:
    return pl.col(col).cast(pl.Int64, strict=False)


def parse_float(col: str) -> pl.Expr:
    return pl.col(col).cast(pl.Float64, strict=False)


def parse_date(col: str = "date") -> pl.Expr:
    return pl.col(col).str.to_date(strict=False)
