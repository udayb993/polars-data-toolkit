"""Referential integrity across silver tables."""
from __future__ import annotations

import polars as pl

from common.io import read


def _orphans(child: pl.DataFrame, parent: pl.DataFrame, key: str) -> int:
    return child.join(parent.select(key), on=key, how="anti").height


def test_results_driver_fk():
    assert _orphans(read("silver", "results"), read("silver", "drivers"), "driver_id") == 0


def test_results_constructor_fk():
    assert _orphans(read("silver", "results"), read("silver", "constructors"), "constructor_id") == 0


def test_results_race_fk():
    assert _orphans(read("silver", "results"), read("silver", "races"), "race_id") == 0


def test_pit_stops_race_fk():
    assert _orphans(read("silver", "pit_stops"), read("silver", "races"), "race_id") == 0


def test_lap_times_race_fk():
    assert _orphans(read("silver", "lap_times"), read("silver", "races"), "race_id") == 0


def test_qualifying_driver_fk():
    assert _orphans(read("silver", "qualifying"), read("silver", "drivers"), "driver_id") == 0
