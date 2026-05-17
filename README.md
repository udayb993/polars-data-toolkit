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

## Exploring the data

The pipeline writes parquet files; you have a few ways to query them.

### Polars (no extra deps)

```python
import polars as pl
pl.read_parquet("data/silver/results.parquet").filter(pl.col("season") == 2023)
```

### Polars SQL (no extra deps)

```python
from analytics import sql_context
ctx = sql_context()
ctx.execute("SELECT season, driver_champion FROM season_summary").collect()
```

### DuckDB (recommended for ad-hoc SQL & the DuckDB UI)

Install once:

```powershell
pip install -r requirements-dev.txt
```

Build a metadata-only DuckDB file that exposes each layer as a **schema** and each parquet as a **view**:

```powershell
python scripts/build_duckdb.py
# wrote data/lake.duckdb
```

`run_pipeline.py` rebuilds it automatically at the end of a full run (pass `--skip-duckdb` to opt out).

Then query:

```powershell
duckdb data/lake.duckdb           # CLI
duckdb -ui data/lake.duckdb       # browser UI: sidebar shows bronze/silver/intermediate/marts schemas
```

```sql
-- one row per layer / view count
SELECT table_schema, COUNT(*) FROM information_schema.tables
WHERE table_type = 'VIEW' GROUP BY 1;

-- top overperformers across all seasons
SELECT season, driver_id, total_overperformance
FROM marts.driver_overperformance
ORDER BY total_overperformance DESC LIMIT 10;

-- join across layers
SELECT r.race_name, d.full_name, res.points
FROM silver.results res
JOIN silver.races   r USING (race_id)
JOIN silver.drivers d USING (driver_id)
WHERE res.finish_position = 1 AND r.season = 2023
ORDER BY r.round;
```

The views point at the parquet files via `read_parquet(...)`, so `data/lake.duckdb` stays tiny (~50 KB) and always reflects the latest pipeline output without re-importing.

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

## Future Plans / Requirements

> The following section captures planned but not-yet-implemented work. It is written for future contributors (human or AI agents) to pick up and implement directly. Items are scoped, ordered, and include file-level hooks. **All data-frame work below must use Polars** (no pandas); persistence must use **Polars parquet writers** and the existing **DuckDB** facade.

### 1. Pipeline run-history (logging table)

Persist the execution history of every pipeline invocation so failures, durations, and row-counts at each step are queryable after the fact. Today there is no run-level or step-level history anywhere — `common/logging_setup.py` only configures `logging.basicConfig`, and `scripts/run_pipeline.py` uses `print(...)` for timings.

#### Storage strategy (Polars parquet + DuckDB views)

- Write **append-only parquet** under a new `data/_meta/` directory using `pl.DataFrame.write_parquet` (mirroring the existing pattern in [common/io.py](common/io.py)). One file per run, partitioned by `run_id`:
  - `data/_meta/pipeline_runs/run_id=<uuid>.parquet`
  - `data/_meta/pipeline_steps/run_id=<uuid>.parquet`
  - `data/_meta/logs/pipeline.log` (rotating text log, see §3)
- Expose both tables as **DuckDB views** in a new `_meta` schema inside `data/lake.duckdb`, mirroring the existing view-over-parquet pattern in [scripts/build_duckdb.py](scripts/build_duckdb.py):
  ```sql
  CREATE SCHEMA IF NOT EXISTS _meta;
  CREATE OR REPLACE VIEW _meta.pipeline_runs  AS
    SELECT * FROM read_parquet('data/_meta/pipeline_runs/*.parquet',  union_by_name=true);
  CREATE OR REPLACE VIEW _meta.pipeline_steps AS
    SELECT * FROM read_parquet('data/_meta/pipeline_steps/*.parquet', union_by_name=true);
  ```
  Guard the view creation so it skips cleanly when `data/_meta/` is empty (first-run case).
- Add `META_DIR = LAKE_DIR / "_meta"` to [config.py](config.py) and include it in the existing `_ensure_dirs` helper.

#### Schema

`pipeline_runs` — one row per `python -m scripts.run_pipeline` invocation:

| Column | Type | Notes |
|---|---|---|
| `run_id` | `Utf8` | UUID4, generated at run start |
| `started_at` | `Datetime` | UTC |
| `ended_at` | `Datetime` | UTC, nullable until finish |
| `status` | `Utf8` | `running` \| `succeeded` \| `failed` |
| `selected_layer` | `Utf8` | nullable; value of `--layer` if set |
| `skip_flags` | `Utf8` | JSON-encoded dict of skip booleans |
| `seasons` | `Utf8` | comma-joined value of `SEASONS` env |
| `total_seconds` | `Float64` | nullable until finish |
| `error_message` | `Utf8` | nullable |
| `git_sha` | `Utf8` | best-effort `git rev-parse HEAD`; nullable |
| `host` | `Utf8` | `socket.gethostname()` |
| `python_version` | `Utf8` | `sys.version.split()[0]` |

`pipeline_steps` — one row per task within a layer:

| Column | Type | Notes |
|---|---|---|
| `run_id` | `Utf8` | FK to `pipeline_runs.run_id` |
| `layer` | `Utf8` | `bronze` \| `silver` \| `intermediate` \| `marts` \| `reports` \| `duckdb` |
| `step_name` | `Utf8` | task name (e.g. `lap_times`, `season_summary`, `build`) |
| `started_at` | `Datetime` | UTC |
| `ended_at` | `Datetime` | UTC |
| `duration_ms` | `Int64` | |
| `status` | `Utf8` | `succeeded` \| `failed` \| `skipped` |
| `rows_written` | `Int64` | nullable; set by the task via recorder |
| `output_path` | `Utf8` | nullable; set by the task via recorder |
| `error_type` | `Utf8` | nullable |
| `error_message` | `Utf8` | nullable |
| `traceback_text` | `Utf8` | nullable; full `traceback.format_exc()` on failure |

#### Granularity

Per-task within each layer (not just per-layer):
- bronze → one row per endpoint in `bronze.extract.TASKS`
- silver → one row per table in `silver.runner.TASKS`
- intermediate → one row per task in `intermediate.runner.TASKS`
- marts → one row per task in `marts.runner.TASKS`
- reports → one row per CSV written in `analytics.write_reports`
- duckdb → one row (`step_name='build'`)

#### Failure semantics

**Preserve current abort-on-failure behaviour.** On a step exception: record the row with `status='failed'` + populated `error_*` / `traceback_text`, mark the run row `failed`, flush both parquet files, then **re-raise**. Downstream layers must not execute. (A future opt-in `--continue-on-error` flag is explicitly out of scope here.)

#### New module: `common/run_history.py`

Provide a small, Polars-native API:

```python
class RunRecorder:
    run_id: str
    def step(self, layer: str, step_name: str) -> "StepContext": ...  # context manager
    def finish(self, status: str, error: BaseException | None = None) -> None: ...

def start_run(selected_layer: str | None, skip_flags: dict, seasons: str) -> RunRecorder: ...
```

- `recorder.step(...)` is a context manager that captures `started_at`, times the block, on exception records `failed` + traceback and re-raises, on success records `succeeded`.
- The yielded `StepContext` exposes `.set_rows(n)` and `.set_output(path)` so each task can attach metadata.
- `finish(...)` builds two `pl.DataFrame` objects (one row of run, N rows of steps) with explicit `schema=` for stable column types, then calls `pl.DataFrame.write_parquet(META_DIR / "pipeline_runs"  / f"run_id={run_id}.parquet")` and the equivalent for steps.

#### Instrumentation points

Thread an **optional** `recorder: RunRecorder | None = None` argument through each `run_all` (optional → keeps direct callers and existing tests untouched):

- [bronze/extract.py](bronze/extract.py) `run_all` — wrap each entry in `TASKS` (~L249) with `recorder.step("bronze", name)` inside the loop at ~L266.
- [silver/runner.py](silver/runner.py) `run_all` (~L39) — wrap each entry in `TASKS` (~L22) with `recorder.step("silver", name)`.
- [intermediate/runner.py](intermediate/runner.py) `run_all` (~L29) — wrap each entry in `TASKS` (~L17) with `recorder.step("intermediate", name)`.
- [marts/runner.py](marts/runner.py) `run_all` (~L29) — wrap each entry in `TASKS` (~L16) with `recorder.step("marts", name)`.
- [analytics/__init__.py](analytics/__init__.py) `write_reports` (~L40) — wrap each per-report write in `recorder.step("reports", <name>)`.
- [scripts/run_pipeline.py](scripts/run_pipeline.py) `main` (~L29):
  - Generate `run_id`, call `start_run(...)` at the top.
  - Pass `recorder` into each `_run` call (~L53–L57) and into `write_reports`.
  - Wrap the optional DuckDB build block (~L59–L65) in `recorder.step("duckdb", "build")`.
  - On any exception: `recorder.finish("failed", error=e)` then re-raise.
  - On success: `recorder.finish("succeeded")`.

#### DuckDB facade update

In [scripts/build_duckdb.py](scripts/build_duckdb.py), after the existing schema/view block (~L48 / ~L69), create the `_meta` schema and views described above. The DB file stays a thin facade over parquet — no run history is ever written *into* DuckDB directly; DuckDB only reads the parquet files produced by `RunRecorder.finish`.

### 2. Logging upgrade (file sink + replace `print`)

- Extend [common/logging_setup.py](common/logging_setup.py): keep the existing `basicConfig` stream handler, **add** a `logging.handlers.RotatingFileHandler` writing to `data/_meta/logs/pipeline.log` (5 MB × 5 backups). Controllable via `LOG_FILE` env var; setting `LOG_FILE=""` disables the file sink. The `setup_logging()` signature must not change.
- Replace remaining `print(...)` calls in [scripts/run_pipeline.py](scripts/run_pipeline.py) (~L51, ~L64, ~L68) with `logger.info(...)`.
- Document the new env var alongside `SEASONS` / `LOG_LEVEL` in the Configuration section above.

### 3. Test coverage gaps

Add focused tests (existing tests must continue to pass unchanged because `recorder` is optional):

- `tests/common/test_run_history.py` — successful run writes both parquet files with expected Polars schema; failed step records `failed` + traceback and re-raises; `set_rows` / `set_output` propagate.
- `tests/scripts/test_run_pipeline.py` — monkeypatch each `run_all` to a no-op, assert one `succeeded` `pipeline_runs` row and the expected `pipeline_steps` rows per layer; monkeypatch one `run_all` to raise, assert run is `failed`, exception propagates, and the failing step row is persisted.
- `tests/common/test_io.py` — round-trip coverage for `lake_path`, `write_parquet`, `scan_parquet` (closes a real gap: `common/io.py` has no direct tests today).
- (Stretch) `tests/common/test_ergast_client.py` — retry/throttle behaviour of [common/ergast_client.py](common/ergast_client.py) with a mocked HTTP layer.

### 4. Verification checklist

1. `pytest -q` — all existing + new tests pass.
2. Skip-everything run (`--skip-bronze --skip-silver --skip-intermediate --skip-marts`) produces one `pipeline_runs` row with `status='succeeded'`.
3. Full run writes one run row + N task rows (bronze endpoints + silver tables + intermediate + marts + reports + `duckdb.build`).
4. Inject a raise in one silver task → run row `failed`, that step row has `failed` + non-empty `traceback_text`, exit non-zero, downstream layers not executed.
5. After `python -m scripts.build_duckdb`:
   ```
   duckdb data/lake.duckdb -c "SELECT layer, status, COUNT(*) FROM _meta.pipeline_steps GROUP BY 1,2 ORDER BY 1,2"
   ```
   returns rows grouped by layer × status.
6. `data/_meta/logs/pipeline.log` is created and rotates when oversized.

### 5. Explicitly out of scope (deferred follow-ups)

- Orchestrator-level retry policy for transform steps (HTTP retries already live in [common/ergast_client.py](common/ergast_client.py)).
- `--continue-on-error` mode and partial-success run status.
- Threading the recorder into bronze's per-race tolerant blocks (pit stops, laps, sprint) to surface their warn-and-skip events as `status='skipped'` step rows.
- Structured/JSON logging or replacing `logging.basicConfig`.
- Retention/pruning of `data/_meta/` parquet files (tiny, ~1 file per run).
- Any dashboard or web UI over run history.

## License

MIT — see [LICENSE](LICENSE).
