"""Analytics functions for Polars DataFrames."""
import polars as pl


# ============================================================================
# FILTER FUNCTIONS
# ============================================================================

def filter_by_category(products_df: pl.DataFrame, category: str) -> pl.DataFrame:
    """
    Filter products by category.
    
    Args:
        products_df: DataFrame with products
        category: Category name to filter by
        
    Returns:
        DataFrame with products in the given category
    """
    return products_df.filter(pl.col("category") == category)


def filter_high_value_orders(orders_df: pl.DataFrame, threshold: float) -> pl.DataFrame:
    """
    Filter orders above a spending threshold.
    
    Args:
        orders_df: DataFrame with orders
        threshold: Minimum total_amount to include
        
    Returns:
        DataFrame with orders where total_amount > threshold
    """
    return orders_df.filter(pl.col("total_amount") > threshold)


def filter_by_ltv_segment(customer_ltv_df: pl.DataFrame, segment: str) -> pl.DataFrame:
    """
    Filter customers by LTV segment.
    
    Args:
        customer_ltv_df: DataFrame with customer LTV metrics
        segment: LTV segment ("High", "Medium", or "Low")
        
    Returns:
        DataFrame with customers in the given segment
    """
    return customer_ltv_df.filter(pl.col("ltv_segment") == segment)


def filter_by_region(countries_df: pl.DataFrame, region: str) -> pl.DataFrame:
    """
    Filter countries by region.
    
    Args:
        countries_df: DataFrame with countries
        region: Region name to filter by
        
    Returns:
        DataFrame with countries in the given region
    """
    return countries_df.filter(pl.col("region") == region)


def filter_discounted_items(order_items_df: pl.DataFrame, min_discount: float) -> pl.DataFrame:
    """
    Filter order items with minimum discount percentage.
    
    Args:
        order_items_df: DataFrame with order items
        min_discount: Minimum discount_pct to include
        
    Returns:
        DataFrame with order items where discount_pct >= min_discount
    """
    return order_items_df.filter(pl.col("discount_pct") >= min_discount)


# ============================================================================
# AGGREGATION FUNCTIONS
# ============================================================================

def revenue_by_category(order_items_df: pl.DataFrame, products_df: pl.DataFrame) -> pl.DataFrame:
    """
    Calculate revenue by category.
    
    Args:
        order_items_df: DataFrame with order items
        products_df: DataFrame with products
        
    Returns:
        DataFrame grouped by category with total subtotal
    """
    result = order_items_df.join(products_df, on="product_id", how="left")
    return result.group_by("category").agg(
        pl.col("subtotal").sum().alias("total_revenue")
    ).sort("total_revenue", descending=True)


def top_products_by_revenue(order_items_df: pl.DataFrame, n: int = 10) -> pl.DataFrame:
    """
    Get top N products by total revenue.
    
    Args:
        order_items_df: DataFrame with order items
        n: Number of top products to return
        
    Returns:
        DataFrame with top N products sorted by subtotal descending
    """
    return order_items_df.group_by("product_name").agg(
        pl.col("subtotal").sum().alias("total_revenue"),
        pl.col("quantity").sum().alias("units_sold"),
    ).sort("total_revenue", descending=True).head(n)


def customer_order_counts(orders_df: pl.DataFrame) -> pl.DataFrame:
    """
    Count orders per customer.
    
    Args:
        orders_df: DataFrame with orders
        
    Returns:
        DataFrame with customer_id and order count, sorted descending
    """
    return orders_df.group_by("customer_id").agg(
        pl.col("order_id").count().alias("order_count")
    ).sort("order_count", descending=True)


def monthly_revenue_trend(orders_df: pl.DataFrame) -> pl.DataFrame:
    """
    Get revenue trend by month.
    
    Args:
        orders_df: DataFrame with orders
        
    Returns:
        DataFrame with order_month and total_amount, sorted ascending
    """
    return orders_df.group_by("order_month").agg(
        pl.col("total_amount").sum().alias("monthly_revenue")
    ).sort("order_month")


def avg_discount_by_category(order_items_df: pl.DataFrame, products_df: pl.DataFrame) -> pl.DataFrame:
    """
    Calculate average discount percentage by category.
    
    Args:
        order_items_df: DataFrame with order items
        products_df: DataFrame with products
        
    Returns:
        DataFrame grouped by category with average discount_pct
    """
    result = order_items_df.join(products_df, on="product_id", how="left")
    return result.group_by("category").agg(
        pl.col("discount_pct").mean().alias("avg_discount_pct")
    ).sort("avg_discount_pct", descending=True)


# ============================================================================
# JOIN FUNCTIONS
# ============================================================================

def enrich_orders_with_customers(orders_df: pl.DataFrame, customers_df: pl.DataFrame) -> pl.DataFrame:
    """
    Enrich orders with customer information.
    
    Args:
        orders_df: DataFrame with orders
        customers_df: DataFrame with customers
        
    Returns:
        Left joined DataFrame with customer fields added
    """
    return orders_df.join(customers_df, on="customer_id", how="left")


def enrich_order_items_with_products(order_items_df: pl.DataFrame, products_df: pl.DataFrame) -> pl.DataFrame:
    """
    Enrich order items with product information.
    
    Args:
        order_items_df: DataFrame with order items
        products_df: DataFrame with products
        
    Returns:
        Left joined DataFrame with product fields added
    """
    return order_items_df.join(products_df, on="product_id", how="left")


def build_full_order_detail(orders_df: pl.DataFrame, customers_df: pl.DataFrame,
                            order_items_df: pl.DataFrame, products_df: pl.DataFrame) -> pl.DataFrame:
    """
    Build comprehensive order detail table.
    
    Joins all four staged tables into one flat master table with all
    order, customer, item, and product information.
    
    Args:
        orders_df: DataFrame with orders
        customers_df: DataFrame with customers
        order_items_df: DataFrame with order items
        products_df: DataFrame with products
        
    Returns:
        Flattened DataFrame with all joined information
    """
    result = order_items_df.join(orders_df, on="order_id", how="inner")
    result = result.join(customers_df, on="customer_id", how="inner")
    result = result.join(products_df, on="product_id", how="inner")
    return result


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def summarise_nulls(df: pl.DataFrame) -> pl.DataFrame:
    """
    Summarize null counts and percentages per column.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        DataFrame with columns: column_name, null_count, null_pct
    """
    null_counts = []
    total_rows = df.height
    
    for col in df.columns:
        null_count = df.select(pl.col(col).is_null().sum()).item()
        null_pct = (null_count / total_rows * 100) if total_rows > 0 else 0
        null_counts.append({
            "column_name": col,
            "null_count": null_count,
            "null_pct": round(null_pct, 2),
        })
    
    return pl.DataFrame(null_counts)


def detect_duplicates(df: pl.DataFrame, subset: list) -> pl.DataFrame:
    """
    Detect duplicate rows based on column subset.
    
    Args:
        df: DataFrame to check
        subset: List of column names to check for duplicates
        
    Returns:
        DataFrame with duplicate rows
    """
    return df.filter(
        pl.col(subset[0]).is_duplicated() if len(subset) > 0 else pl.lit(False)
    ) if subset else df.filter(pl.lit(False))


def column_summary(df: pl.DataFrame) -> pl.DataFrame:
    """
    Generate summary statistics for all columns.
    
    Args:
        df: DataFrame to summarize
        
    Returns:
        DataFrame with columns: column_name, dtype, null_count, min, max, mean
    """
    summaries = []
    
    for col_name in df.columns:
        col_dtype = df.schema[col_name]
        null_count = df.select(pl.col(col_name).is_null().sum()).item()
        
        # Try to get statistics (only for numeric types)
        summary_dict = {
            "column_name": col_name,
            "dtype": str(col_dtype),
            "null_count": null_count,
        }
        
        try:
            stats = df.select([
                pl.col(col_name).min().alias("min"),
                pl.col(col_name).max().alias("max"),
                pl.col(col_name).mean().alias("mean"),
            ]).row(0)
            summary_dict["min"] = stats[0]
            summary_dict["max"] = stats[1]
            summary_dict["mean"] = round(stats[2], 2) if stats[2] is not None else None
        except:
            summary_dict["min"] = None
            summary_dict["max"] = None
            summary_dict["mean"] = None
        
        summaries.append(summary_dict)
    
    return pl.DataFrame(summaries)


def validate_foreign_key(child_df: pl.DataFrame, parent_df: pl.DataFrame,
                         child_col: str, parent_col: str) -> dict:
    """
    Validate foreign key relationship between two tables.
    
    Args:
        child_df: DataFrame with foreign key column
        parent_df: DataFrame with primary key column
        child_col: Column name in child_df
        parent_col: Column name in parent_df
        
    Returns:
        Dictionary with validation result:
        {
            "valid": bool,
            "orphan_count": int,
            "orphan_values": list
        }
    """
    parent_values = set(parent_df.select(parent_col).to_series().to_list())
    child_values = child_df.select(child_col).to_series()
    
    orphans = [v for v in child_values if v not in parent_values]
    
    return {
        "valid": len(orphans) == 0,
        "orphan_count": len(orphans),
        "orphan_values": orphans[:10],  # Return first 10 orphans
    }
