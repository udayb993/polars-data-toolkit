# Agent Tasks for Polars E-Commerce Data Pipeline

This file lists tasks for AI agents to work on the repository, organized by difficulty level.

## Easy Tasks

- [ ] Add a new analytics function: `filter_by_city(customers_df, city)` with a test
- [ ] Add a new analytics function: `top_customers_by_orders(orders_df, n=10)` with a test
- [ ] Add a new view to `build_monthly_trend.py`: add a column for cumulative revenue
- [ ] Add a new extract script: `fetch_quotes.py` that fetches from https://dummyjson.com/quotes
- [ ] Add null count logging to each transform script

## Medium Tasks

- [ ] Add a new staged table: `data/staged/reviews.csv`
      - Fetch from https://dummyjson.com/comments and transform it with:
        - review_id, user_id, product_id (mapped from postId), body, likes
      - Add tests for it in `test_transform/`

- [ ] Add a new mart: `data/marts/discount_analysis.csv`
      - Show total discount given per category per month
      - Add tests for it in `test_marts/`

- [ ] Add a data quality report script: `scripts/run_quality_checks.py`
      - That runs `summarise_nulls` and `detect_duplicates` on all staged tables
      - and prints a report

- [ ] Add `avg_discount_pct` to `monthly_trend` mart and update its test

## Hard Tasks

- [ ] Add a new pipeline stage: `pipelines/validate/`
      - That validates referential integrity across all staged tables
      - before the load stage runs. If validation fails, raise an error
      - and do not proceed to load.

- [ ] Add a suppliers dimension
      - fetch from a generated source,
      - link to products, add to category_revenue mart

- [ ] Add incremental loading
      - modify `run_pipeline.py` to check if raw data already exists
      - and skip fetch if it does (add --force flag to re-fetch)

- [ ] Add a new mart: `customer_country_analysis.csv`
      - Join customers + countries (match on country name) to get region,
      - subregion, and currency for each customer.
      - Then aggregate spend by region.
