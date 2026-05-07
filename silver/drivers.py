"""silver.drivers — dimension table, deduped across seasons.

Practices: deterministic dedup with ``unique(keep="first")``, date parsing,
nullable int coercion.
"""
from __future__ import annotations

import polars as pl

from common.io import scan, write


def build() -> pl.DataFrame:
    df = (
        scan("bronze", "drivers")
        .select(
            pl.col("driverId").alias("driver_id"),
            pl.col("code").alias("driver_code"),
            pl.col("permanentNumber").cast(pl.Int32, strict=False).alias("permanent_number"),
            pl.col("givenName").alias("given_name"),
            pl.col("familyName").alias("family_name"),
            (pl.col("givenName") + pl.lit(" ") + pl.col("familyName")).alias("full_name"),
            pl.col("dateOfBirth").str.to_date(strict=False).alias("date_of_birth"),
            pl.col("nationality"),
            pl.col("url"),
        )
        .unique(subset=["driver_id"], keep="first")
        .sort("driver_id")
        .collect()
    )
    write(df, "silver", "drivers")
    return df


if __name__ == "__main__":
    build()
