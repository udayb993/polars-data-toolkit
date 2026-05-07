"""silver.status — DNF / finishing status reference, with categorisation.

Practices: ``when/then/otherwise`` chains, ``Enum`` dtype.
"""
from __future__ import annotations

import polars as pl

from common.io import scan, write

DNF_CATEGORIES = pl.Enum(["finished", "lapped", "mechanical", "accident", "disqualified", "other"])


def _categorise() -> pl.Expr:
    s = pl.col("status").str.to_lowercase()
    return (
        pl.when(s == "finished").then(pl.lit("finished"))
        .when(s.str.contains(r"\+\d+ lap")).then(pl.lit("lapped"))
        .when(s.str.contains("disqualified|excluded")).then(pl.lit("disqualified"))
        .when(s.str.contains("collision|accident|spun off|damage")).then(pl.lit("accident"))
        .when(s.str.contains(
            "engine|gearbox|hydraulic|electric|brake|suspension|transmission|"
            "wheel|tyre|fuel|clutch|power unit|cooling|exhaust|battery|driveshaft|"
            "differential|radiator|oil|water|mechanical|technical|overheating|"
            "puncture|spark|alternator|throttle|steering"
        )).then(pl.lit("mechanical"))
        .otherwise(pl.lit("other"))
        .cast(DNF_CATEGORIES)
    )


def build() -> pl.DataFrame:
    df = (
        scan("bronze", "status")
        .select(
            pl.col("statusId").cast(pl.Int32).alias("status_id"),
            pl.col("status"),
            pl.col("count").cast(pl.Int64).alias("historical_count"),
            _categorise().alias("status_category"),
        )
        .sort("status_id")
        .collect()
    )
    write(df, "silver", "status")
    return df


if __name__ == "__main__":
    build()
