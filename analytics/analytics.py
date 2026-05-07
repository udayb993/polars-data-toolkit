"""
Analytics module for Polars-based e-commerce data toolkit.
Provides filter, aggregation, join, and utility functions for data analysis.
"""

import polars as pl
from typing import List, Optional


# ============================================================================
# FILTER FUNCTIONS
# ============================================================================

def filter_active_customers(df: pl.DataFrame) -> pl.DataFrame:
    """
    Filter customers to only active ones.
    
    Args:
        df: DataFrame with customer data containing 'is_active' column
    
    Returns:
        Filtered DataFrame with only active customers
    """
    return df.filter(pl.col("is_active") == True)


def filter_orders_by_status(df: pl.DataFrame, status: str) -> pl.DataFrame:
    """
    Filter orders by status.
    
    Args:
        df: DataFrame with order data containing 'status' column
        status: Status string to filter by (e.g., "delivered", "pending")
    
    Returns:
        Filtered DataFrame with orders matching the given status
    """
    return df.filter(pl.col("status") == status)


def filter_orders_by_date_range(
    df: pl.DataFrame, start: str, end: str
) -> pl.DataFrame:
    """
    Filter orders by date range.
    
    Args:
        df: DataFrame with order data containing 'order_date' column
        start: Start date as string in format "YYYY-MM-DD"
        end: End date as string in format "YYYY-MM-DD"
    
    Returns:
        Filtered DataFrame with orders within the date range (inclusive)
    """
    return df.filter(
        (pl.col("order_date") >= start) & (pl.col("order_date") <= end)
    )


def filter_products_by_category(df: pl.DataFrame, category: str) -> pl.DataFrame:
    """
    Filter products by category.
    
    Args:
        df: DataFrame with product data containing 'category' column
        category: Category string to filter by
    
    Returns:
        Filtered DataFrame with products in the given category
    """
    return df.filter(pl.col("category") == category)


def filter_high_value_orders(df: pl.DataFrame, threshold: float) -> pl.DataFrame:
    """
    Filter orders by minimum total amount.
    
    Args:
        df: DataFrame with order data containing 'total_amount' column
        threshold: Minimum order amount threshold
    
    Returns:
        Filtered DataFrame with orders exceeding the threshold
    """
    return df.filter(pl.col("total_amount") > threshold)


# ============================================================================
# AGGREGATION FUNCTIONS
# ============================================================================

def revenue_by_country(
    customers_df: pl.DataFrame, orders_df: pl.DataFrame
) -> pl.DataFrame:
    """
    Calculate total revenue grouped by country.
    
    Args:
        customers_df: DataFrame with customer data
        orders_df: DataFrame with order data
    
    Returns:
        DataFrame with country and total_revenue columns
    """
    result = (
        orders_df
        .join(customers_df, on="customer_id", how="left")
        .group_by("country")
        .agg(pl.col("total_amount").sum().alias("total_revenue"))
        .sort("total_revenue", descending=True)
    )
    return result


def orders_per_customer(orders_df: pl.DataFrame) -> pl.DataFrame:
    """
    Calculate count of orders per customer.
    
    Args:
        orders_df: DataFrame with order data
    
    Returns:
        DataFrame with customer_id and order_count columns, sorted descending
    """
    result = (
        orders_df
        .group_by("customer_id")
        .agg(pl.col("order_id").count().alias("order_count"))
        .sort("order_count", descending=True)
    )
    return result


def avg_order_value_by_status(orders_df: pl.DataFrame) -> pl.DataFrame:
    """
    Calculate average order value grouped by status.
    
    Args:
        orders_df: DataFrame with order data
    
    Returns:
        DataFrame with status and avg_total_amount columns
    """
    result = (
        orders_df
        .group_by("status")
        .agg(pl.col("total_amount").mean().alias("avg_total_amount"))
        .sort("avg_total_amount", descending=True)
    )
    return result


def top_selling_products(
    order_items_df: pl.DataFrame, n: int = 10
) -> pl.DataFrame:
    """
    Get top N products by total quantity sold.
    
    Args:
        order_items_df: DataFrame with order item data
        n: Number of top products to return (default: 10)
    
    Returns:
        DataFrame with product_id and total_quantity_sold, sorted descending
    """
    result = (
        order_items_df
        .group_by("product_id")
        .agg(pl.col("quantity").sum().alias("total_quantity_sold"))
        .sort("total_quantity_sold", descending=True)
        .head(n)
    )
    return result


def revenue_by_category(
    order_items_df: pl.DataFrame, products_df: pl.DataFrame
) -> pl.DataFrame:
    """
    Calculate total revenue grouped by product category.
    
    Args:
        order_items_df: DataFrame with order item data
        products_df: DataFrame with product data
    
    Returns:
        DataFrame with category and total_revenue columns
    """
    result = (
        order_items_df
        .join(products_df, on="product_id", how="left")
        .group_by("category")
        .agg(pl.col("subtotal").sum().alias("total_revenue"))
        .sort("total_revenue", descending=True)
    )
    return result


# ============================================================================
# JOIN FUNCTIONS
# ============================================================================

def enrich_orders_with_customers(
    orders_df: pl.DataFrame, customers_df: pl.DataFrame
) -> pl.DataFrame:
    """
    Join orders with customer information.
    
    Args:
        orders_df: DataFrame with order data
        customers_df: DataFrame with customer data
    
    Returns:
        Enriched DataFrame with both order and customer columns
    """
    result = orders_df.join(customers_df, on="customer_id", how="left")
    return result


def enrich_order_items_with_products(
    order_items_df: pl.DataFrame, products_df: pl.DataFrame
) -> pl.DataFrame:
    """
    Join order items with product information.
    
    Args:
        order_items_df: DataFrame with order item data
        products_df: DataFrame with product data
    
    Returns:
        Enriched DataFrame with both order item and product columns
    """
    result = order_items_df.join(products_df, on="product_id", how="left")
    return result


def build_full_order_detail(
    orders_df: pl.DataFrame,
    customers_df: pl.DataFrame,
    order_items_df: pl.DataFrame,
    products_df: pl.DataFrame,
) -> pl.DataFrame:
    """
    Build a comprehensive detail table joining all 4 main tables.
    
    Args:
        orders_df: DataFrame with order data
        customers_df: DataFrame with customer data
        order_items_df: DataFrame with order item data
        products_df: DataFrame with product data
    
    Returns:
        Flat DataFrame with all meaningful columns from all tables
    """
    result = (
        order_items_df
        .join(orders_df, on="order_id", how="left")
        .join(customers_df, on="customer_id", how="left")
        .join(products_df, on="product_id", how="left")
        .select([
            "order_item_id",
            "order_id",
            "order_date",
            "product_id",
            "product_name",
            "category",
            "customer_id",
            "first_name",
            "last_name",
            "country",
            "quantity",
            "unit_price",
            "subtotal",
            "status",
            "total_amount",
        ])
    )
    return result


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def summarise_nulls(df: pl.DataFrame) -> pl.DataFrame:
    """
    Summarize null values in each column.
    
    Args:
        df: DataFrame to analyze
    
    Returns:
        DataFrame with column names, null counts, and null percentages
    """
    null_counts = df.null_count()
    total_rows = len(df)
    
    columns_info = []
    for col_name in df.columns:
        null_count = null_counts[0, col_name]
        null_pct = (null_count / total_rows * 100) if total_rows > 0 else 0
        columns_info.append({
            "column_name": col_name,
            "null_count": null_count,
            "null_percentage": round(null_pct, 2),
        })
    
    result = pl.DataFrame(columns_info)
    return result


def detect_duplicates(df: pl.DataFrame, subset: List[str]) -> pl.DataFrame:
    """
    Detect duplicate rows based on a subset of columns.
    
    Args:
        df: DataFrame to check for duplicates
        subset: List of column names to check for duplicates
    
    Returns:
        DataFrame containing only duplicate rows (appears more than once)
    """
    result = (
        df
        .with_row_count("row_count")
        .with_columns(
            pl.col(subset).is_duplicated().alias("is_dup")
        )
        .filter(pl.col("is_dup"))
        .drop("is_dup", "row_count")
    )
    return result


def column_summary(df: pl.DataFrame) -> pl.DataFrame:
    """
    Generate summary statistics for each column.
    
    Args:
        df: DataFrame to summarize
    
    Returns:
        DataFrame with column name, dtype, null count, and statistical summary
    """
    summary_data = []
    
    for col_name in df.columns:
        col_data = df[col_name]
        dtype = str(col_data.dtype)
        null_count = col_data.null_count()
        
        summary = {
            "column_name": col_name,
            "dtype": dtype,
            "null_count": null_count,
        }
        
        # Add statistics for numeric columns
        if dtype in ["Int64", "Float64", "Int32", "Float32"]:
            summary["min"] = col_data.min()
            summary["max"] = col_data.max()
            summary["mean"] = round(col_data.mean(), 2) if col_data.mean() is not None else None
        else:
            summary["min"] = None
            summary["max"] = None
            summary["mean"] = None
        
        summary_data.append(summary)
    
    result = pl.DataFrame(summary_data)
    return result
