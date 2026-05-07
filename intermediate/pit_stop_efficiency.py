"""intermediate.pit_stop_efficiency — rank stops within race / constructor / circuit.

Practices: chained ``rank`` window functions over different partitions,
percentile via ``rank().over() / count().over()``.
"""
from __future__ import annotations

import polars as pl

from common.io import scan, write


def build() -> pl.DataFrame:
    pits = scan("silver", "pit_stops")
    races = scan("silver", "races").select("race_id", "circuit_id")
    results = scan("silver", "results").select("race_id", "driver_id", "constructor_id")

    df = (
        pits.join(races, on="race_id", how="left")
        .join(results, on=["race_id", "driver_id"], how="left")
        .with_columns(
            (pl.col("stop_duration").dt.total_milliseconds() / 1000.0).alias("stop_seconds"),
        )
        .with_columns(
            pl.col("stop_seconds").rank("min").over("race_id").alias("rank_in_race"),
            pl.col("stop_seconds").rank("min").over(["season", "constructor_id"]).alias("rank_in_constructor_season"),
            pl.col("stop_seconds").rank("min").over("circuit_id").alias("rank_at_circuit_alltime"),
            (pl.col("stop_seconds").rank("average").over("circuit_id")
             / pl.len().over("circuit_id").cast(pl.Float64)).alias("circuit_percentile"),
        )
        .sort(["season", "round", "stop_seconds"])
        .collect()
    )
    write(df, "intermediate", "pit_stop_efficiency")
    return df


if __name__ == "__main__":
    build()
