# Polars E-Commerce Data Pipeline

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


## Project Overview

This is a complete, production-ready Polars-based e-commerce data pipeline designed to test agentic AI coding capabilities. The pipeline:

1. **Fetches real data** from two public APIs (DummyJSON and REST Countries)
2. **Transforms and cleans** data using Polars with type safety and null handling
3. **Builds analytical datasets** (marts) by joining and aggregating staged data
4. **Validates data quality** with comprehensive pytest test suite

**Why this exists:** To test AI agents' ability to implement complete, multi-file data engineering workflows with proper testing, error handling, and best practices.

---

## Architecture

The pipeline follows a classic 3-layer ETL architecture:

### Layer 1: EXTRACT (`pipelines/extract/`)
Fetches raw JSON from public APIs and saves to `data/raw/` as-is.
- `fetch_products.py` — DummyJSON products endpoint
- `fetch_users.py` — DummyJSON users endpoint
- `fetch_carts.py` — DummyJSON carts endpoint
- `fetch_countries.py` — REST Countries endpoint

### Layer 2: TRANSFORM (`pipelines/transform/`)
Cleans, normalizes, and type-casts raw data using Polars. Outputs structured CSVs to `data/staged/`.
- `transform_products.py` — products with calculated original price
- `transform_users.py` — customers with full name concatenation
- `transform_carts.py` — orders and order_items (1-to-many split)
- `transform_countries.py` — countries with nested field extraction

### Layer 3: LOAD (`pipelines/load/`)
Builds final analytical datasets by joining staged tables. Outputs to `data/marts/`.
- `build_order_summary.py` — complete order view with customer/product details
- `build_customer_ltv.py` — customer metrics with LTV segment
- `build_category_revenue.py` — revenue analytics by product category
- `build_monthly_trend.py` — monthly revenue and discount trends

### Analytics Module (`analytics/analytics.py`)
20+ reusable functions for common operations:
- **Filters:** by category, by LTV segment, by region, high-value orders, discounted items
- **Aggregations:** revenue by category, top products, customer order counts, monthly trends
- **Joins:** enrich orders with customers, enrich items with products, full order detail
- **Utilities:** null summaries, duplicate detection, column statistics, foreign key validation

---

## Data Sources

All data is free, publicly accessible, requires no authentication, and returns JSON.

### API 1: DummyJSON (https://dummyjson.com)
Used for e-commerce core tables:
- `GET /products?limit=100&skip=0` — 100 products with category, price, discount, rating
- `GET /users?limit=100&skip=0` — 100 users with name, email, address, age
- `GET /carts?limit=100&skip=0` — 100 carts with items and totals

### API 2: REST Countries (https://restcountries.com)
Used for geography dimension:
- `GET /v3.1/all?fields=name,region,subregion,currencies,population,flags` — 250+ countries

---

## Folder Structure

```
polars-ecommerce-pipeline/
├── .gitignore                                # FIRST file created (critical)
├── LICENSE                                   # MIT License
├── README.md                                 # This file
├── requirements.txt                          # Dependencies: polars, httpx, pytest
├── tasks.md                                  # Agent tasks (Easy/Medium/Hard)
│
├── data/
│   ├── raw/                                 # Raw JSON from APIs (generated)
│   │   ├── .gitkeep
│   │   ├── products_raw.json
│   │   ├── users_raw.json
│   │   ├── carts_raw.json
│   │   └── countries_raw.json
│   │
│   ├── staged/                              # Clean, normalized CSVs
│   │   ├── .gitkeep
│   │   ├── products.csv
│   │   ├── customers.csv
│   │   ├── orders.csv
│   │   ├── order_items.csv
│   │   └── countries.csv
│   │
│   └── marts/                               # Analytical datasets
│       ├── .gitkeep
│       ├── order_summary.csv
│       ├── customer_ltv.csv
│       ├── category_revenue.csv
│       └── monthly_trend.csv
│
├── pipelines/
│   ├── __init__.py
│   ├── extract/                             # Layer 1: Fetch raw data
│   │   ├── __init__.py
│   │   ├── fetch_products.py
│   │   ├── fetch_users.py
│   │   ├── fetch_carts.py
│   │   └── fetch_countries.py
│   │
│   ├── transform/                           # Layer 2: Clean & normalize
│   │   ├── __init__.py
│   │   ├── transform_products.py
│   │   ├── transform_users.py
│   │   ├── transform_carts.py
│   │   └── transform_countries.py
│   │
│   └── load/                                # Layer 3: Build marts
│       ├── __init__.py
│       ├── build_order_summary.py
│       ├── build_customer_ltv.py
│       ├── build_category_revenue.py
│       └── build_monthly_trend.py
│
├── analytics/
│   ├── __init__.py
│   └── analytics.py                         # 20+ analytics functions
│
├── scripts/
│   └── run_pipeline.py                      # Master script (extract → transform → load)
│
└── tests/
    ├── __init__.py
    ├── conftest.py                          # Pytest fixtures
    │
    ├── test_extract/                        # Test raw data integrity
    │   ├── __init__.py
    │   ├── test_fetch_products.py
    │   ├── test_fetch_users.py
    │   ├── test_fetch_carts.py
    │   └── test_fetch_countries.py
    │
    ├── test_transform/                      # Test staged table schema & data quality
    │   ├── __init__.py
    │   ├── test_transform_products.py
    │   ├── test_transform_users.py
    │   ├── test_transform_carts.py
    │   └── test_transform_countries.py
    │
    └── test_marts/                          # Test analytical datasets
        ├── __init__.py
        ├── test_order_summary.py
        ├── test_customer_ltv.py
        ├── test_category_revenue.py
        └── test_monthly_trend.py
```

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/polars-ecommerce-pipeline.git
cd polars-ecommerce-pipeline
```

### 2. Create and activate virtual environment
```bash
# Create venv
python -m venv .venv

# Activate (Mac/Linux)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the complete pipeline
```bash
python scripts/run_pipeline.py
```

This runs all three stages in order:
- EXTRACT: Fetches ~100 products, ~100 users, ~100 carts, ~250 countries from APIs
- TRANSFORM: Cleans and normalizes data to 5 staged CSVs
- LOAD: Builds 4 analytical marts with joins and aggregations

### 5. Run all tests
```bash
pytest tests/ -v
```

Tests will skip gracefully if data files don't exist yet.

---

## Running Individual Stages

### Extract only
```bash
python pipelines/extract/fetch_products.py
python pipelines/extract/fetch_users.py
python pipelines/extract/fetch_carts.py
python pipelines/extract/fetch_countries.py
```

### Transform only
```bash
python pipelines/transform/transform_products.py
python pipelines/transform/transform_users.py
python pipelines/transform/transform_carts.py
python pipelines/transform/transform_countries.py
```

### Load only
```bash
python pipelines/load/build_order_summary.py
python pipelines/load/build_customer_ltv.py
python pipelines/load/build_category_revenue.py
python pipelines/load/build_monthly_trend.py
```

---

## Analytics Functions

The `analytics.py` module provides 20+ reusable functions:

### Filters
- `filter_by_category(products_df, category)` — products in given category
- `filter_high_value_orders(orders_df, threshold)` — orders > threshold
- `filter_by_ltv_segment(customer_ltv_df, segment)` — customers by High/Medium/Low
- `filter_by_region(countries_df, region)` — countries in given region
- `filter_discounted_items(order_items_df, min_discount)` — items with min discount

### Aggregations
- `revenue_by_category(order_items_df, products_df)` — total revenue per category
- `top_products_by_revenue(order_items_df, n=10)` — top N products by revenue
- `customer_order_counts(orders_df)` — order count per customer
- `monthly_revenue_trend(orders_df)` — revenue by month
- `avg_discount_by_category(order_items_df, products_df)` — avg discount per category

### Joins
- `enrich_orders_with_customers(orders_df, customers_df)` — add customer fields
- `enrich_order_items_with_products(order_items_df, products_df)` — add product fields
- `build_full_order_detail(...)` — join all 4 tables into flat master

### Utilities
- `summarise_nulls(df)` — null count and % per column
- `detect_duplicates(df, subset)` — find duplicate rows
- `column_summary(df)` — stats for each column
- `validate_foreign_key(child_df, parent_df, ...)` — check referential integrity

---

## Agent Tasks

See [tasks.md](tasks.md) for a detailed list of feature development tasks organized by difficulty:

- **Easy:** Add new filter/aggregation functions, add logging, extend marts
- **Medium:** Add new staged tables, new marts, quality report scripts
- **Hard:** Add validation layer, incremental loading, new dimensions

---

## Contributing Rules

When extending this pipeline, follow these rules:

1. **Always use Polars, never pandas** — type safety and performance
2. **Write a test for every new function** — quality gate
3. **Use `pathlib.Path` for all file paths** — cross-platform compatibility
4. **Never hardcode absolute paths** — use relative paths from `__file__`
5. **Never commit `.venv/` or generated CSVs** — use `.gitignore`
6. **Add docstrings to all functions** — clarity
7. **Keep tests independent** — use fixtures from `conftest.py`

---

## Testing

The test suite includes 60+ tests across three layers:

**Extract tests (16):** Validate raw JSON structure and data integrity
**Transform tests (30):** Validate staged CSV schema, types, and relationships
**Marts tests (20):** Validate analytical dataset calculations and business logic

Run with:
```bash
pytest tests/ -v                    # All tests
pytest tests/test_extract/ -v       # Only extract tests
pytest tests/test_transform/ -v     # Only transform tests
pytest tests/test_marts/ -v         # Only mart tests
```

Tests automatically skip if data files don't exist (they wait for prior stages).

---

## Technologies

- **Python 3.10+** — Programming language
- **Polars** — Fast, type-safe data frames
- **httpx** — Synchronous HTTP client
- **pytest** — Test framework
- **pathlib** — Cross-platform path handling

---

## License

MIT License. See [LICENSE](LICENSE) file.

---

## Notes for AI Agents

This repository is designed to be worked on by AI coding agents. Key considerations:

1. **Data regeneration:** Running `scripts/run_pipeline.py` requires internet access to fetch fresh data
2. **Test skipping:** Tests will skip (not fail) if input data isn't available
3. **Pure Polars:** All data operations must use Polars API only
4. **Referential integrity:** Foreign key relationships are tested
5. **Type safety:** All DataFrames use explicit dtypes
6. **Documentation:** Every function has a docstring explaining intent
│   ├── generate_orders.py                 # Generate 500 order records
│   └── generate_order_items.py            # Generate 1500 order item records
│
├── scripts/                                # Orchestration and processing scripts
│   ├── __init__.py
│   ├── run_all.py                         # Master script: generates all data
│   ├── create_views.py                    # Creates 5 derived views
│   └── create_joins.py                    # Creates 3 joined tables
│
├── analytics/                              # Analytics functions module
│   ├── __init__.py
│   └── analytics.py                       # 20+ data analysis functions
│
└── tests/                                  # Test suite with pytest
    ├── __init__.py
    ├── test_customers.py                  # Customer data validation
    ├── test_products.py                   # Product data validation
    ├── test_orders.py                     # Order data validation
    └── test_order_items.py                # Order item data validation
```

---

## Data Models

### Table 1: customers.csv (200 rows)
| Column | Type | Description |
|--------|------|-------------|
| customer_id | int | Primary key, 1-200 |
| first_name | string | Faker-generated first name |
| last_name | string | Faker-generated last name |
| email | string | Faker-generated email |
| country | string | One of: UK, US, Germany, France, India |
| signup_date | date | Random between 2020-01-01 and 2023-12-31 |
| is_active | boolean | 85% true, 15% false |

### Table 2: products.csv (50 rows)
| Column | Type | Description |
|--------|------|-------------|
| product_id | int | Primary key, 1-50 |
| product_name | string | Faker-generated product name |
| category | string | One of: Electronics, Clothing, Books, Home, Sports |
| price | float | Random between $5.00 and $500.00 |
| stock_quantity | int | Random between 0 and 1000 |

### Table 3: orders.csv (500 rows)
| Column | Type | Description |
|--------|------|-------------|
| order_id | int | Primary key, 1-500 |
| customer_id | int | Foreign key → customers.customer_id |
| order_date | date | Random between 2022-01-01 and 2024-01-01 |
| status | string | One of: pending, shipped, delivered, cancelled |
| total_amount | float | Sum of order_items subtotals (auto-calculated) |

### Table 4: order_items.csv (1500 rows)
| Column | Type | Description |
|--------|------|-------------|
| order_item_id | int | Primary key, 1-1500 |
| order_id | int | Foreign key → orders.order_id |
| product_id | int | Foreign key → products.product_id |
| quantity | int | Random between 1 and 10 |
| unit_price | float | Matches product.price at time of order |
| subtotal | float | quantity × unit_price (auto-calculated) |

---

## Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd polars-ecommerce-toolkit
```

### 2. Create Virtual Environment
```bash
# macOS / Linux
python -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Generate Data Locally
```bash
python scripts/run_all.py
```
This generates all base data files into the `data/` folder.

### 5. Create Derived Views
```bash
python scripts/create_views.py
```

### 6. Create Joined Tables
```bash
python scripts/create_joins.py
```

### 7. Run Tests
```bash
pytest tests/ -v
```

---

## Analytics Module

The `analytics/analytics.py` module provides 20+ functions:

### Filter Functions
- `filter_active_customers()` — Returns only active customers
- `filter_orders_by_status()` — Filter orders by status
- `filter_orders_by_date_range()` — Filter orders within date range
- `filter_products_by_category()` — Filter products by category
- `filter_high_value_orders()` — Filter orders above amount threshold

### Aggregation Functions
- `revenue_by_country()` — Total revenue grouped by customer country
- `orders_per_customer()` — Count of orders per customer
- `avg_order_value_by_status()` — Average order amount by status
- `top_selling_products()` — Top N products by quantity sold
- `revenue_by_category()` — Total revenue grouped by product category

### Join Functions
- `enrich_orders_with_customers()` — Join orders with customer info
- `enrich_order_items_with_products()` — Join items with product info
- `build_full_order_detail()` — Join all 4 tables into flat table

### Utility Functions
- `summarise_nulls()` — Count and percentage of nulls per column
- `detect_duplicates()` — Find rows duplicated on specified columns
- `column_summary()` — Generate statistical summary per column

---

## License

MIT License — see LICENSE file for details
