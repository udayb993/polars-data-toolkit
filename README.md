# polars-data-toolkit

A multi-layer **Polars** ETL playground built on the public **[Ergast / Jolpica F1 API](https://github.com/jolpica/jolpica-f1)**. Designed to teach Polars syntax through realistic transformations on a small but rich relational dataset (~12 source tables, ~3 seasons, ~125k lap rows).

## Why this dataset

- 12 naturally-related source tables from a single free API (no auth).
- Real time dimension (race dates 2022–2024) → exercises window functions, `group_by_dynamic`, rolling aggregates.
- Mixed entity sizes: dimensions (drivers, constructors, circuits) are tiny; facts (lap_times) are large enough to demonstrate lazy/streaming.
- Rich joins: 1:N (race → results), self (driver vs teammate), semi/anti (filtering), asof-style (lap-vs-baseline).
- Fits on a laptop in seconds yet exercises every Polars feature you'd reach for in production.

## Architecture (5 layers)

```
bronze (raw API dump)        ─►  silver (typed + cleaned)
       │                              │
       │                              ├─►  intermediate (reusable building blocks)
       │                              │           │
       │                              │           └─►  marts (analytical outputs)
       │                              │                          │
       │                              │                          └─►  reports (CSV)
```

| Layer | Path | Format | What lives here |
|---|---|---|---|
| **Bronze** | `data/bronze/` | Parquet (string cols) | Faithful API dump, nested JSON kept as strings |
| **Silver** | `data/silver/` | Parquet (typed) | Cleaned, type-coerced, deduplicated, FK-ready |
| **Intermediate** | `data/intermediate/` | Parquet | Reusable derived facts feeding multiple marts |
| **Marts** | `data/marts/` | Parquet | Final analytical outputs |
| **Reports** | `data/reports/` | CSV | Human-readable slices of marts |

## Datasets at a glance

### Bronze (12 tables) — raw API
`seasons`, `circuits`, `races`, `drivers`, `constructors`, `status`, `results`, `qualifying`, `sprint_results`, `driver_standings`, `constructor_standings`, `pit_stops`, `lap_times`

### Silver (12 tables) — cleaned
Same shape as bronze plus:
- Lap-time strings (`"1:23.456"`) parsed into `Duration`.
- JSON sub-objects (`Location`, `FastestLap`, ...) decoded with `pl.Struct` schemas.
- Surrogate `race_id` (e.g. `2023_05`) for stable joins.
- Conditional time fields combined into UTC timestamps.
- Status reason categorised into `finished | lapped | mechanical | accident | disqualified | other` (Polars `Enum`).

### Intermediate (8 tables) — reusable building blocks
| Table | What it computes |
|---|---|
| `race_facts` | Per-race wide fact: pole, winner, fastest lap, n_dnfs, n_pit_stops |
| `driver_race_performance` | Per driver per race: positions gained, total pit time, avg lap pace, pace-vs-winner ratio, pace-vs-teammate delta (window) |
| `constructor_race_performance` | Per constructor per race: combined points, double-DNF/double-podium flags |
| `lap_pace_normalized` | Per lap: ratio vs median lap of top-5 finishers (semi-join + window) |
| `pit_stop_efficiency` | Per stop: rank within race / constructor-season / circuit-all-time |
| `qualifying_vs_race` | Per driver per race: actual vs expected points (grid lookup), positions gained |
| `driver_form` | Rolling 5-race avg points, podium rate, DNF rate per driver |
| `championship_state` | Cumulative points + live standings + gap-to-leader after each race |

### Marts (9 tables) — analytical outputs
| Mart | Description |
|---|---|
| `championship_progression` | Live standings + delta vs prev race + mathematically-eliminated flag |
| `teammate_h2h` | Self-join: head-to-head per driver pair per season |
| `circuit_difficulty_index` | Composite Z-scored difficulty per circuit |
| `pit_crew_ranking` | Per constructor per season: median/p95/IQR of stop times + rank |
| `driver_overperformance` | Drivers ranked by points-vs-grid-expectation |
| `dnf_analysis` | Pivot of DNF causes by constructor × season, with reliability % |
| `pace_evolution` | Monthly lap-pace trend per driver (group_by_dynamic on race_date) |
| `race_narrative` | Per race story: pole, winner, biggest mover, biggest faller |
| `season_summary` | Per season: champion, title margin, n distinct winners |

### Reports
A few CSVs in `data/reports/` for human consumption: `season_summary.csv`, `final_standings.csv`, `race_narrative.csv`.

## Polars features practised

| Feature | Where |
|---|---|
| `LazyFrame` + `scan_parquet` | All silver/intermediate transforms |
| `over()` window functions | `driver_race_performance`, `championship_state`, `championship_progression` |
| `rolling_*` | `driver_form` |
| `group_by_dynamic` | `pace_evolution` |
| `cum_sum`, `cum_count`, `rank` | `championship_state`, `pit_stop_efficiency` |
| Self joins | `teammate_h2h` |
| Semi / anti joins | `lap_pace_normalized`, FK validation tests |
| `pivot` | `dnf_analysis` |
| `str.json_decode` + `pl.Struct` | All silver decoders |
| `pl.Enum` | `silver/status.py` |
| `pl.SQLContext` | `analytics/__init__.py` |
| Duration parsing & arithmetic | `silver/_expressions.py`, lap/pit math |
| `min_horizontal`, `coalesce`, `when/then/otherwise` | `silver/qualifying.py`, `silver/status.py` |

## Quick start

```powershell
python -m pip install -r requirements.txt

# Single season, full pipeline
$env:SEASONS = "2023"
python scripts/run_pipeline.py

# Or only the bottom of the stack
python scripts/run_pipeline.py --layer marts --skip-bronze --skip-silver --skip-intermediate

# All three seasons (slower; respects API rate limits)
$env:SEASONS = "2022,2023,2024"
python scripts/run_pipeline.py
```

## Tests

```powershell
python -m pytest -q                                  # quick run (~3s, 176 tests)
python -m pytest                                     # verbose, per-test progress
python -m pytest tests/silver/test_results.py        # one file
python -m pytest tests/silver/                       # one layer
python -m pytest -k "qualifying or pole"             # filter by keyword
```

> If `pytest` alone is not recognized in PowerShell, use `python -m pytest`. The pip-installed `pytest.exe` shim lives in your user `Scripts/` folder which may not be on `PATH`.

The suite is organised **one test module per table** under `tests/silver/`, `tests/intermediate/`, and `tests/marts/`. Each table gets at least three checks covering:

- **Primary-key uniqueness** — `(race_id, driver_id)`, `(season, constructor_id)`, etc.
- **Schema / dtype** — every key column has the expected `pl.Int32`, `pl.Date`, `pl.Duration("us")`, `pl.Enum`, ...
- **Null discipline** — required key columns are non-null; nullable measure columns are documented.
- **Value ranges** — positions in `1..30`, points in `0..26`, lap_time medians in `60..130s`, lat/lon bounded, etc.
- **Allowed-value sets** — `status_category` is one of 6 enum members, `circuit_id` is snake_case, driver `code` matches `^[A-Z]{3}$`.
- **Cross-table arithmetic** — `positions_gained == grid - finish`, `total_overperformance == points - expected`, race_id derives from `season_round`.
- **Sequence properties** — `cumulative_points` monotonic per (season, driver), `stop_number` dense per (race, driver), standings dense `1..N` per season.

Plus cross-cutting suites:
- **Referential integrity** — every FK in fact tables resolves against its dimension.
- **Business rules** — champion has max points, rolling rates ∈ [0, 1], teammate-pair uniqueness.
- **Analytics SQL** — `pl.SQLContext` registers all marts and a sample query runs.

A session-scoped fixture in `tests/conftest.py` builds the lake once (only fetching missing bronze tables), so the whole suite runs in a few seconds against a populated `data/`.

## Project layout

```
bronze/extract.py             # API → data/bronze/*.parquet (one fn per table)
silver/<table>.py             # data/bronze → data/silver (one module per table)
intermediate/<table>.py       # data/silver  → data/intermediate
marts/<table>.py              # data/intermediate → data/marts
analytics/__init__.py         # pl.SQLContext + report writers
scripts/run_pipeline.py       # CLI driver (--layer, --skip-*)
common/                       # Ergast HTTP client, IO helpers, logging
tests/                        # pytest suite
```

## Configuration

Environment variables:
- `SEASONS` — comma-separated list, e.g. `"2023"` or `"2022,2023,2024"`. Default `2022,2023,2024`.
- `LOG_LEVEL` — `DEBUG | INFO | WARNING | ERROR`.

## API source

Data is fetched from the [Jolpica Ergast mirror](https://api.jolpi.ca/ergast/f1) — the maintained successor to the deprecated `ergast.com` API. Free, no auth, ~4 req/s rate limit (the client throttles automatically).

## License

MIT — see [LICENSE](LICENSE).
