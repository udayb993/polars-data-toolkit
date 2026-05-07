"""silver.qualifying — pick best of Q1/Q2/Q3 + gap-to-pole.

Practices: ``min_horizontal`` over Duration columns, ``over("race_id")``
window for pole reference, conditional null arithmetic.
"""
from __future__ import annotations

import polars as pl

from common.io import read, scan, write
from silver._expressions import parse_lap_time

DRIVER_DTYPE = pl.Struct({"driverId": pl.Utf8})
CONSTRUCTOR_DTYPE = pl.Struct({"constructorId": pl.Utf8})


def build() -> pl.DataFrame:
    races = read("silver", "races").select(["season", "round", "race_id", "race_date"]).lazy()
    df = (
        scan("bronze", "qualifying")
        .with_columns(
            pl.col("Driver").str.json_decode(DRIVER_DTYPE).struct.field("driverId").alias("driver_id"),
            pl.col("Constructor").str.json_decode(CONSTRUCTOR_DTYPE).struct.field("constructorId").alias("constructor_id"),
            parse_lap_time("Q1").alias("q1_time"),
            parse_lap_time("Q2").alias("q2_time"),
            parse_lap_time("Q3").alias("q3_time"),
            pl.col("season").cast(pl.Int32),
            pl.col("round").cast(pl.Int32),
            pl.col("position").cast(pl.Int32, strict=False).alias("quali_position"),
            pl.col("number").cast(pl.Int32, strict=False).alias("car_number"),
        )
        .with_columns(
            pl.min_horizontal("q1_time", "q2_time", "q3_time").alias("best_quali_time"),
        )
        .join(races, on=["season", "round"], how="left")
        # Gap-to-pole = best_quali_time – min(best_quali_time) over race
        .with_columns(
            (pl.col("best_quali_time") - pl.col("best_quali_time").min().over("race_id"))
              .alias("gap_to_pole"),
        )
        .select(
            "race_id", "season", "round", "race_date",
            "driver_id", "constructor_id", "car_number", "quali_position",
            "q1_time", "q2_time", "q3_time", "best_quali_time", "gap_to_pole",
        )
        .sort(["season", "round", "quali_position"], nulls_last=True)
        .collect()
    )
    write(df, "silver", "qualifying")
    return df


if __name__ == "__main__":
    build()
