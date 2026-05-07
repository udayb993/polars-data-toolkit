"""silver.races — assign surrogate ``race_id`` and a UTC race datetime.

Practices: composite key construction, conditional time concatenation,
``str.to_datetime``, sort key for downstream window functions ordered by date.
"""
from __future__ import annotations

import polars as pl

from common.io import scan, write

CIRCUIT_DTYPE = pl.Struct({"circuitId": pl.Utf8, "circuitName": pl.Utf8, "url": pl.Utf8})


def build() -> pl.DataFrame:
    df = (
        scan("bronze", "races")
        .with_columns(pl.col("Circuit").str.json_decode(CIRCUIT_DTYPE).alias("c"))
        .select(
            pl.col("season").cast(pl.Int32),
            pl.col("round").cast(pl.Int32).alias("round"),
            pl.col("raceName").alias("race_name"),
            pl.col("c").struct.field("circuitId").alias("circuit_id"),
            pl.col("date").str.to_date(strict=False).alias("race_date"),
            pl.col("time"),
            pl.col("url"),
        )
        # Surrogate key – stable, sortable.
        .with_columns(
            (pl.col("season").cast(pl.Utf8) + pl.lit("_") + pl.col("round").cast(pl.Utf8).str.zfill(2))
            .alias("race_id")
        )
        # Combine date + time into a UTC timestamp where possible.
        .with_columns(
            pl.when(pl.col("time").is_not_null())
            .then(
                (pl.col("race_date").cast(pl.Utf8) + pl.lit("T") + pl.col("time"))
                .str.to_datetime("%Y-%m-%dT%H:%M:%SZ", strict=False, time_zone="UTC")
            )
            .otherwise(None)
            .alias("race_start_utc")
        )
        .drop("time")
        .sort(["season", "round"])
        .collect()
    )
    write(df, "silver", "races")
    return df


if __name__ == "__main__":
    build()
