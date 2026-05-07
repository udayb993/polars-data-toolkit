"""silver.driver_standings — final season standing per driver."""
from __future__ import annotations

import polars as pl

from common.io import scan, write

DRIVER_DTYPE = pl.Struct({"driverId": pl.Utf8})


def build() -> pl.DataFrame:
    df = (
        scan("bronze", "driver_standings")
        .with_columns(
            pl.col("Driver").str.json_decode(DRIVER_DTYPE).struct.field("driverId").alias("driver_id"),
        )
        .select(
            pl.col("season").cast(pl.Int32),
            pl.col("round").cast(pl.Int32).alias("final_round"),
            "driver_id",
            pl.col("position").cast(pl.Int32, strict=False).alias("final_position"),
            pl.col("points").cast(pl.Float64).alias("final_points"),
            pl.col("wins").cast(pl.Int32, strict=False).alias("season_wins"),
        )
        .sort(["season", "final_position"], nulls_last=True)
        .collect()
    )
    write(df, "silver", "driver_standings")
    return df


if __name__ == "__main__":
    build()
