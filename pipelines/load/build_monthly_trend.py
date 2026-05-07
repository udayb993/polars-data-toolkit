"""Build monthly revenue trend mart."""
from pathlib import Path
import polars as pl


def build_monthly_trend() -> pl.DataFrame:
    """
    Build monthly revenue trend mart.
    
    Aggregates orders by month to show revenue trends.
    Produces data/marts/monthly_trend.csv
    
    Returns:
        Polars DataFrame with monthly revenue metrics
    """
    data_dir = Path(__file__).parent.parent.parent / "data"
    
    # Load staged data
    orders = pl.read_csv(data_dir / "staged" / "orders.csv")
    
    # Aggregate by month
    result = orders.group_by("order_month").agg([
        pl.col("order_id").count().alias("total_orders"),
        pl.col("total_amount").sum().alias("total_revenue"),
        pl.col("discounted_total").sum().alias("total_discounted_revenue"),
        pl.col("discount_amount").sum().alias("total_discount_given"),
        pl.col("total_amount").mean().alias("avg_order_value"),
    ])
    
    # Add average discount percentage
    result = result.with_columns([
        (pl.col("total_discount_given") / pl.col("total_revenue") * 100)
            .alias("avg_discount_pct")
    ])
    
    # Sort by month ascending
    result = result.sort("order_month")
    
    # Select final columns
    result = result.select([
        "order_month",
        "total_orders",
        "total_revenue",
        "total_discounted_revenue",
        "total_discount_given",
        "avg_order_value",
        "avg_discount_pct",
    ])
    
    # Save to marts
    output_dir = data_dir / "marts"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "monthly_trend.csv"
    
    result.write_csv(output_file)
    
    print(f"✓ Built monthly trend: {result.height} rows ({result.width} cols) → data/marts/monthly_trend.csv")
    return result


if __name__ == "__main__":
    build_monthly_trend()
