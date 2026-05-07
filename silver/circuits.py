"""silver.circuits — JSON-string ``Location`` → struct → flat columns.

Practices: ``str.json_decode`` with explicit dtype, ``struct.field``,
deduplication across seasons (a circuit may appear in multiple seasons).
"""
from __future__ import annotations

import polars as pl

from common.io import scan, write

LOCATION_DTYPE = pl.Struct({
    "lat": pl.Utf8,
    "long": pl.Utf8,
    "locality": pl.Utf8,
    "country": pl.Utf8,
})


def build() -> pl.DataFrame:
    df = (
        scan("bronze", "circuits")
        .with_columns(pl.col("Location").str.json_decode(LOCATION_DTYPE).alias("loc"))
        .select(
            pl.col("circuitId").alias("circuit_id"),
            pl.col("circuitName").alias("circuit_name"),
            pl.col("url"),
            pl.col("loc").struct.field("country"),
            pl.col("loc").struct.field("locality").alias("city"),
            pl.col("loc").struct.field("lat").cast(pl.Float64, strict=False),
            pl.col("loc").struct.field("long").cast(pl.Float64, strict=False).alias("lon"),
        )
        .unique(subset=["circuit_id"], keep="first")
        .sort("circuit_id")
        .collect()
    )
    write(df, "silver", "circuits")
    return df


if __name__ == "__main__":
    build()
