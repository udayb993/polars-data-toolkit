# Polars E-Commerce Data Toolkit

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ⚠️ IMPORTANT: Do NOT Commit Local Files

**Do NOT commit `.venv/` or `data/*.csv`** — these are in `.gitignore` and should always stay local.
- `.venv/` contains large binary files (up to 178MB) that will cause GitHub push failures
- `data/*.csv` are generated locally and should not be version controlled

---

## Overview

This is a complete, production-ready Polars-based e-commerce data toolkit designed for testing agentic AI coding capabilities. It generates synthetic e-commerce data across four interconnected tables (customers, products, orders, order_items) and provides comprehensive analytics functions.

**Key Features:**
- ✅ Pure Python + Polars (no pandas)
- ✅ 4 fully normalized data tables with foreign key relationships
- ✅ Realistic data generation using Faker library
- ✅ Derived views and cross-table joins
- ✅ 20+ analytics functions (filtering, aggregation, joining, utilities)
- ✅ Comprehensive test suite with pytest
- ✅ Full data validation and quality checks

---

## Project Structure

```
polars-ecommerce-toolkit/
├── .gitignore                              # Git ignore rules (CRITICAL)
├── LICENSE                                 # MIT License
├── README.md                               # This file
├── requirements.txt                        # Python dependencies
│
├── data/                                   # Generated CSV files (local only, not committed)
│   ├── .gitkeep                           # Placeholder to track directory
│   ├── customers.csv                      # Generated: 200 customer records
│   ├── products.csv                       # Generated: 50 product records
│   ├── orders.csv                         # Generated: 500 order records
│   ├── order_items.csv                    # Generated: 1500 order item records
│   ├── *.csv (views)                      # Derived views from scripts/create_views.py
│   └── *.csv (joins)                      # Joined tables from scripts/create_joins.py
│
├── generate_data/                          # Data generation module
│   ├── __init__.py
│   ├── models.py                          # Schema definitions for all tables
│   ├── generate_customers.py              # Generate 200 customer records
│   ├── generate_products.py               # Generate 50 product records
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
