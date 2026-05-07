"""intermediate.race_facts — wide one-row-per-race fact built from silver.

Each race answers: who took pole, who won, who set the fastest lap, how
many DNFs, how many pit stops, did anyone earn a sprint win.

Practices: many ``filter().group_by().agg()`` reductions joined back into a
spine, ``join`` chaining, ``coalesce`` for optional sources.
"""
from __future__ import annotations

import polars as pl

from common.io import path_for, scan, write


def build() -> pl.DataFrame:
    races = scan("silver", "races")
    results = scan("silver", "results")
    quali = scan("silver", "qualifying")
    pits = scan("silver", "pit_stops")
    laps = scan("silver", "lap_times")

    winners = (
        results.filter(pl.col("finish_position") == 1)
        .select("race_id",
                pl.col("driver_id").alias("winner_driver_id"),
                pl.col("constructor_id").alias("winner_constructor_id"),
                pl.col("race_time").alias("winner_race_time"))
    )
    pole = (
        quali.filter(pl.col("quali_position") == 1)
        .select("race_id", pl.col("driver_id").alias("pole_driver_id"))
    )
    fastest = (
        results.filter(pl.col("fastest_lap_time").is_not_null())
        .sort(["race_id", "fastest_lap_time"])
        .group_by("race_id")
        .agg(
            pl.col("driver_id").first().alias("fastest_lap_driver_id"),
            pl.col("fastest_lap_time").first().alias("fastest_lap_time"),
        )
    )
    dnfs = (
        results.group_by("race_id").agg(
            (~pl.col("finished_flag")).sum().alias("n_dnfs"),
            pl.col("driver_id").count().alias("n_starters"),
        )
    )
    pit_agg = pits.group_by("race_id").agg(
        pl.col("stop_duration").count().alias("n_pit_stops"),
        pl.col("stop_duration").mean().alias("avg_pit_duration"),
    )
    laps_agg = laps.group_by("race_id").agg(
        pl.col("lap").max().alias("total_laps"),
    )

    df = (
        races.select("race_id", "season", "round", "race_name", "circuit_id", "race_date")
        .join(winners, on="race_id", how="left")
        .join(pole, on="race_id", how="left")
        .join(fastest, on="race_id", how="left")
        .join(dnfs, on="race_id", how="left")
        .join(pit_agg, on="race_id", how="left")
        .join(laps_agg, on="race_id", how="left")
        .with_columns(
            (pl.col("n_pit_stops").fill_null(0) /
             pl.col("n_starters").cast(pl.Float64)).alias("avg_stops_per_driver"),
        )
        .sort(["season", "round"])
        .collect()
    )
    write(df, "intermediate", "race_facts")
    return df


if __name__ == "__main__":
    build()
