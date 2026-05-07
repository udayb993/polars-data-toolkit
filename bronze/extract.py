"""Bronze layer — raw API dump.

Each ``fetch_*`` function:
1. Hits the Ergast/Jolpica endpoint (paginated where required).
2. Flattens just enough to make the result a flat list of dicts.
3. Writes a Parquet file to ``data/bronze/<name>.parquet``.

We keep all fields as **strings** at this layer.  Type coercion happens in
silver – this preserves the bronze contract that "what we wrote == what the
API gave us".
"""
from __future__ import annotations

import json
import logging
from typing import Iterable

import polars as pl

from common.ergast_client import fetch_all, iter_inner
from common.io import write
from config import SEASONS

log = logging.getLogger(__name__)


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def _to_df(rows: Iterable[dict]) -> pl.DataFrame:
    """Build a string-only DataFrame from a list of (possibly nested) dicts.

    Nested dicts/lists are stringified as JSON so bronze stays schema-stable
    even when fields appear/disappear (e.g. ``FastestLap`` only present for
    finishers).  Silver will parse them.
    """
    norm: list[dict] = []
    for r in rows:
        flat: dict = {}
        for k, v in r.items():
            if isinstance(v, (dict, list)):
                flat[k] = json.dumps(v, ensure_ascii=False)
            elif v is None:
                flat[k] = None
            else:
                flat[k] = str(v)
        norm.append(flat)
    if not norm:
        return pl.DataFrame()
    # Union of all keys → consistent schema across pages.
    all_keys = sorted({k for r in norm for k in r})
    norm = [{k: r.get(k) for k in all_keys} for r in norm]
    return pl.DataFrame(norm, schema={k: pl.Utf8 for k in all_keys})


# ----------------------------------------------------------------------------
# Per-season tables (one row per season, no cross-product needed)
# ----------------------------------------------------------------------------

def fetch_seasons() -> None:
    rows = []
    for y in SEASONS:
        rows.append({"season": str(y), "url": f"https://en.wikipedia.org/wiki/{y}_Formula_One_World_Championship"})
    write(_to_df(rows), "bronze", "seasons")


def fetch_circuits() -> None:
    rows: list[dict] = []
    for y in SEASONS:
        pages = fetch_all(f"{y}/circuits")
        for c in iter_inner(pages, "CircuitTable", "Circuits"):
            c = dict(c)
            c["season"] = str(y)
            rows.append(c)
    write(_to_df(rows), "bronze", "circuits")


def fetch_races() -> None:
    rows: list[dict] = []
    for y in SEASONS:
        pages = fetch_all(f"{y}/races")
        rows.extend(iter_inner(pages, "RaceTable", "Races"))
    write(_to_df(rows), "bronze", "races")


def fetch_drivers() -> None:
    rows: list[dict] = []
    for y in SEASONS:
        pages = fetch_all(f"{y}/drivers")
        for d in iter_inner(pages, "DriverTable", "Drivers"):
            d = dict(d)
            d["season"] = str(y)
            rows.append(d)
    write(_to_df(rows), "bronze", "drivers")


def fetch_constructors() -> None:
    rows: list[dict] = []
    for y in SEASONS:
        pages = fetch_all(f"{y}/constructors")
        for c in iter_inner(pages, "ConstructorTable", "Constructors"):
            c = dict(c)
            c["season"] = str(y)
            rows.append(c)
    write(_to_df(rows), "bronze", "constructors")


def fetch_status() -> None:
    pages = fetch_all("status", limit=100)
    rows = iter_inner(pages, "StatusTable", "Status")
    write(_to_df(rows), "bronze", "status")


# ----------------------------------------------------------------------------
# Per-season but exploded by race (results, qualifying, sprint, standings)
# ----------------------------------------------------------------------------

def _explode_results(pages: list[dict], inner_key: str) -> list[dict]:
    """Flatten ``Races[*].<inner_key>[*]`` → list of rows with race coords."""
    out: list[dict] = []
    for race in iter_inner(pages, "RaceTable", "Races"):
        coords = {
            "season": race.get("season"),
            "round": race.get("round"),
            "raceName": race.get("raceName"),
            "date": race.get("date"),
        }
        for row in race.get(inner_key, []):
            r = dict(row)
            r.update(coords)
            out.append(r)
    return out


def fetch_results() -> None:
    rows: list[dict] = []
    for y in SEASONS:
        pages = fetch_all(f"{y}/results", limit=100)
        rows.extend(_explode_results(pages, "Results"))
    write(_to_df(rows), "bronze", "results")


def fetch_qualifying() -> None:
    rows: list[dict] = []
    for y in SEASONS:
        pages = fetch_all(f"{y}/qualifying", limit=100)
        rows.extend(_explode_results(pages, "QualifyingResults"))
    write(_to_df(rows), "bronze", "qualifying")


def fetch_sprint_results() -> None:
    rows: list[dict] = []
    for y in SEASONS:
        try:
            pages = fetch_all(f"{y}/sprint", limit=100)
        except Exception as e:  # noqa: BLE001 – endpoint may 404 for early seasons
            log.warning("sprint fetch failed for %s: %s", y, e)
            continue
        rows.extend(_explode_results(pages, "SprintResults"))
    write(_to_df(rows), "bronze", "sprint_results")


def fetch_driver_standings() -> None:
    """Final season standings (one row per driver per season)."""
    rows: list[dict] = []
    for y in SEASONS:
        pages = fetch_all(f"{y}/driverstandings", limit=100)
        for sl in iter_inner(pages, "StandingsTable", "StandingsLists"):
            for d in sl.get("DriverStandings", []):
                r = dict(d)
                r["season"] = sl.get("season")
                r["round"] = sl.get("round")
                rows.append(r)
    write(_to_df(rows), "bronze", "driver_standings")


def fetch_constructor_standings() -> None:
    rows: list[dict] = []
    for y in SEASONS:
        pages = fetch_all(f"{y}/constructorstandings", limit=100)
        for sl in iter_inner(pages, "StandingsTable", "StandingsLists"):
            for c in sl.get("ConstructorStandings", []):
                r = dict(c)
                r["season"] = sl.get("season")
                r["round"] = sl.get("round")
                rows.append(r)
    write(_to_df(rows), "bronze", "constructor_standings")


# ----------------------------------------------------------------------------
# Per-race tables — one HTTP call per race (potentially heavy)
# ----------------------------------------------------------------------------

def _race_rounds() -> list[tuple[int, int]]:
    """Read ``bronze.races`` for season+round pairs, so we don't refetch races."""
    from common.io import read
    df = read("bronze", "races").select(["season", "round"]).unique()
    return [(int(s), int(r)) for s, r in df.iter_rows()]


def fetch_pit_stops() -> None:
    rows: list[dict] = []
    for season, rnd in _race_rounds():
        try:
            pages = fetch_all(f"{season}/{rnd}/pitstops", limit=100)
        except Exception as e:  # noqa: BLE001
            log.warning("pitstops missing %s r%s: %s", season, rnd, e)
            continue
        for race in iter_inner(pages, "RaceTable", "Races"):
            for ps in race.get("PitStops", []):
                r = dict(ps)
                r["season"] = race.get("season")
                r["round"] = race.get("round")
                rows.append(r)
    write(_to_df(rows), "bronze", "pit_stops")


def fetch_lap_times() -> None:
    rows: list[dict] = []
    for season, rnd in _race_rounds():
        try:
            # ``laps`` row count is laps × drivers (~1000); use a large page
            # so each race needs only ~1 HTTP call.
            pages = fetch_all(f"{season}/{rnd}/laps", limit=1000)
        except Exception as e:  # noqa: BLE001
            log.warning("laps missing %s r%s: %s", season, rnd, e)
            continue
        for race in iter_inner(pages, "RaceTable", "Races"):
            for lap in race.get("Laps", []):
                lap_no = lap.get("number")
                for t in lap.get("Timings", []):
                    rows.append({
                        "season": race.get("season"),
                        "round": race.get("round"),
                        "lap": lap_no,
                        "driverId": t.get("driverId"),
                        "position": t.get("position"),
                        "time": t.get("time"),
                    })
    write(_to_df(rows), "bronze", "lap_times")


# ----------------------------------------------------------------------------
# Registry / CLI
# ----------------------------------------------------------------------------

# Order matters – ``pit_stops`` and ``lap_times`` depend on ``races``.
TASKS: dict[str, callable] = {
    "seasons": fetch_seasons,
    "circuits": fetch_circuits,
    "races": fetch_races,
    "drivers": fetch_drivers,
    "constructors": fetch_constructors,
    "status": fetch_status,
    "results": fetch_results,
    "qualifying": fetch_qualifying,
    "sprint_results": fetch_sprint_results,
    "driver_standings": fetch_driver_standings,
    "constructor_standings": fetch_constructor_standings,
    "pit_stops": fetch_pit_stops,
    "lap_times": fetch_lap_times,
}


def run_all() -> None:
    for name, fn in TASKS.items():
        log.info("== bronze: %s ==", name)
        fn()
