"""Build customer lifetime value (LTV) mart."""
from pathlib import Path
import polars as pl


def build_customer_ltv() -> pl.DataFrame:
    """
    Build customer LTV mart.
    
    Aggregates customer spending and order metrics, assigns LTV segment.
    Produces data/marts/customer_ltv.csv
    
    Returns:
        Polars DataFrame with customer LTV metrics
    """
    data_dir = Path(__file__).parent.parent.parent / "data"
    
    # Load staged data
    customers = pl.read_csv(data_dir / "staged" / "customers.csv")
    orders = pl.read_csv(data_dir / "staged" / "orders.csv")
    
    # Join and aggregate
    result = orders.join(customers, on="customer_id", how="inner")
    
    result = result.group_by("customer_id").agg([
        pl.col("full_name").first(),
        pl.col("email").first(),
        pl.col("city").first(),
        pl.col("order_id").count().alias("total_orders"),
        pl.col("discounted_total").sum().alias("total_spent"),
        pl.col("discounted_total").mean().alias("avg_order_value"),
        pl.col("total_quantity").sum().alias("total_items_bought"),
    ])
    
    # Add LTV segment
    result = result.with_columns([
        pl.when(pl.col("total_spent") > 1000)
            .then(pl.lit("High"))
            .when(pl.col("total_spent") >= 500)
            .then(pl.lit("Medium"))
            .otherwise(pl.lit("Low"))
            .alias("ltv_segment")
    ])
    
    # Reorder columns
    result = result.select([
        "customer_id",
        "full_name",
        "email",
        "city",
        "total_orders",
        "total_spent",
        "avg_order_value",
        "total_items_bought",
        "ltv_segment",
    ])
    
    # Save to marts
    output_dir = data_dir / "marts"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "customer_ltv.csv"
    
    result.write_csv(output_file)
    
    print(f"✓ Built customer LTV: {result.height} rows ({result.width} cols) → data/marts/customer_ltv.csv")
    return result


if __name__ == "__main__":
    build_customer_ltv()
