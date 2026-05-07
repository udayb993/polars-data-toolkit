"""silver.constructor_standings — final season standing per constructor."""
from __future__ import annotations

import polars as pl

from common.io import scan, write

CONSTRUCTOR_DTYPE = pl.Struct({"constructorId": pl.Utf8})


def build() -> pl.DataFrame:
    df = (
        scan("bronze", "constructor_standings")
        .with_columns(
            pl.col("Constructor").str.json_decode(CONSTRUCTOR_DTYPE).struct.field("constructorId").alias("constructor_id"),
        )
        .select(
            pl.col("season").cast(pl.Int32),
            pl.col("round").cast(pl.Int32).alias("final_round"),
            "constructor_id",
            pl.col("position").cast(pl.Int32, strict=False).alias("final_position"),
            pl.col("points").cast(pl.Float64).alias("final_points"),
            pl.col("wins").cast(pl.Int32, strict=False).alias("season_wins"),
        )
        .sort(["season", "final_position"], nulls_last=True)
        .collect()
    )
    write(df, "silver", "constructor_standings")
    return df


if __name__ == "__main__":
    build()
