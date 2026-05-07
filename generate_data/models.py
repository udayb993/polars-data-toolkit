"""
Data model schemas for e-commerce tables.
Defines the expected Polars schema for each table.
"""

import polars as pl

CUSTOMER_SCHEMA = {
    "customer_id": pl.Int64,
    "first_name": pl.Utf8,
    "last_name": pl.Utf8,
    "email": pl.Utf8,
    "country": pl.Utf8,
    "signup_date": pl.Date,
    "is_active": pl.Boolean,
}

PRODUCT_SCHEMA = {
    "product_id": pl.Int64,
    "product_name": pl.Utf8,
    "category": pl.Utf8,
    "price": pl.Float64,
    "stock_quantity": pl.Int64,
}

ORDER_SCHEMA = {
    "order_id": pl.Int64,
    "customer_id": pl.Int64,
    "order_date": pl.Date,
    "status": pl.Utf8,
    "total_amount": pl.Float64,
}

ORDER_ITEM_SCHEMA = {
    "order_item_id": pl.Int64,
    "order_id": pl.Int64,
    "product_id": pl.Int64,
    "quantity": pl.Int64,
    "unit_price": pl.Float64,
    "subtotal": pl.Float64,
}
