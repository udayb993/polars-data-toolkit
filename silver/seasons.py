"""silver.seasons — trivial cast.

Practices: ``scan_parquet`` lazy → ``cast`` → ``collect`` → ``write``.
"""
from __future__ import annotations

import polars as pl

from common.io import scan, write


def build() -> pl.DataFrame:
    df = (
        scan("bronze", "seasons")
        .select(
            pl.col("season").cast(pl.Int32),
            pl.col("url"),
        )
        .sort("season")
        .collect()
    )
    write(df, "silver", "seasons")
    return df


if __name__ == "__main__":
    build()
