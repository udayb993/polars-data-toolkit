"""silver.constructors — dimension table, deduped across seasons."""
from __future__ import annotations

import polars as pl

from common.io import scan, write


def build() -> pl.DataFrame:
    df = (
        scan("bronze", "constructors")
        .select(
            pl.col("constructorId").alias("constructor_id"),
            pl.col("name").alias("constructor_name"),
            pl.col("nationality"),
            pl.col("url"),
        )
        .unique(subset=["constructor_id"], keep="first")
        .sort("constructor_id")
        .collect()
    )
    write(df, "silver", "constructors")
    return df


if __name__ == "__main__":
    build()
