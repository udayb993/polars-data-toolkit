"""Build order summary mart by joining orders, order_items, and customers."""
from pathlib import Path
import polars as pl


def build_order_summary() -> pl.DataFrame:
    """
    Build order summary mart.
    
    Joins orders + order_items + customers to create a comprehensive order view.
    Produces data/marts/order_summary.csv
    
    Returns:
        Polars DataFrame with order summaries
    """
    data_dir = Path(__file__).parent.parent.parent / "data"
    
    # Load staged data
    orders = pl.read_csv(data_dir / "staged" / "orders.csv")
    order_items = pl.read_csv(data_dir / "staged" / "order_items.csv")
    customers = pl.read_csv(data_dir / "staged" / "customers.csv")
    
    # Join orders with customers
    result = orders.join(customers, left_on="customer_id", right_on="customer_id", how="left")
    
    # Select final columns
    result = result.select([
        pl.col("order_id"),
        pl.col("customer_id"),
        pl.col("full_name"),
        pl.col("email"),
        pl.col("city"),
        pl.col("total_amount"),
        pl.col("discounted_total"),
        pl.col("discount_amount"),
        pl.col("total_products"),
        pl.col("total_quantity"),
        pl.col("order_month"),
    ])
    
    # Save to marts
    output_dir = data_dir / "marts"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "order_summary.csv"
    
    result.write_csv(output_file)
    
    print(f"✓ Built order summary: {result.height} rows ({result.width} cols) → data/marts/order_summary.csv")
    return result


if __name__ == "__main__":
    build_order_summary()
