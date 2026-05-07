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
pytest -q
```

Covers:
- **Schema / smoke**: every silver table exists, has expected keys, no duplicate keys (`tests/test_silver.py`).
- **Referential integrity**: every FK resolves (`tests/test_referential_integrity.py`).
- **Business rules**: champion has max points, cumulative points are monotonic, rolling rates are bounded, teammate-pair uniqueness (`tests/test_business_rules.py`).
- **SQL context**: marts queryable with `pl.SQLContext` (`tests/test_analytics_sql.py`).

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
