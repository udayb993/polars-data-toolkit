"""marts.season_summary — one row per season."""
from __future__ import annotations

import polars as pl

from common.io import scan, write


def build() -> pl.DataFrame:
    ds = scan("silver", "driver_standings")
    cs = scan("silver", "constructor_standings")
    rf = scan("intermediate", "race_facts")

    champ = (
        ds.filter(pl.col("final_position") == 1)
        .select("season",
                pl.col("driver_id").alias("champion_driver_id"),
                pl.col("final_points").alias("champion_points"))
    )
    runner = (
        ds.filter(pl.col("final_position") == 2)
        .select("season", pl.col("final_points").alias("runner_up_points"))
    )
    cchamp = (
        cs.filter(pl.col("final_position") == 1)
        .select("season",
                pl.col("constructor_id").alias("champion_constructor_id"),
                pl.col("final_points").alias("constructor_champion_points"))
    )
    cruner = (
        cs.filter(pl.col("final_position") == 2)
        .select("season", pl.col("final_points").alias("constructor_runner_points"))
    )

    diversity = (
        rf.group_by("season").agg(
            pl.col("winner_driver_id").n_unique().alias("n_distinct_winners"),
            pl.col("winner_constructor_id").n_unique().alias("n_distinct_winning_constructors"),
            pl.col("race_id").count().alias("n_races"),
        )
    )

    df = (
        champ
        .join(runner, on="season", how="left")
        .join(cchamp, on="season", how="left")
        .join(cruner, on="season", how="left")
        .join(diversity, on="season", how="left")
        .with_columns(
            (pl.col("champion_points") - pl.col("runner_up_points")).alias("driver_title_margin"),
            (pl.col("constructor_champion_points") - pl.col("constructor_runner_points"))
              .alias("constructor_title_margin"),
        )
        .sort("season")
        .collect()
    )
    write(df, "marts", "season_summary")
    return df


if __name__ == "__main__":
    build()
