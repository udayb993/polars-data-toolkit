"""marts.dnf_analysis — DNFs by constructor × cause × season + reliability score.

Practices: ``join`` with status reference for category, ``pivot`` to wide
form, reliability % = finished / starts.
"""
from __future__ import annotations

import polars as pl

from common.io import scan, write


def build() -> pl.DataFrame:
    results = scan("silver", "results").select(
        "season", "race_id", "driver_id", "constructor_id", "finished_flag", "finish_status"
    )
    status = scan("silver", "status").select("status", "status_category")

    enriched = results.join(status, left_on="finish_status", right_on="status", how="left").with_columns(
        pl.col("status_category").fill_null(pl.lit("other"))
    )

    long = (
        enriched.group_by(["season", "constructor_id", "status_category"])
        .agg(pl.len().alias("n"))
        .collect()
    )
    wide = long.pivot(values="n", index=["season", "constructor_id"], on="status_category").fill_null(0)

    reliability = (
        enriched.group_by(["season", "constructor_id"])
        .agg(
            pl.col("finished_flag").sum().alias("n_finished"),
            pl.len().alias("n_starts"),
        )
        .with_columns((pl.col("n_finished") / pl.col("n_starts")).alias("reliability"))
        .collect()
    )

    df = wide.join(reliability, on=["season", "constructor_id"], how="left").sort(
        ["season", "reliability"], descending=[False, True]
    )
    write(df, "marts", "dnf_analysis")
    return df


if __name__ == "__main__":
    build()
