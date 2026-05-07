"""Build category revenue mart."""
from pathlib import Path
import polars as pl


def build_category_revenue() -> pl.DataFrame:
    """
    Build category revenue mart.
    
    Joins order_items with products to analyze revenue by category.
    Produces data/marts/category_revenue.csv
    
    Returns:
        Polars DataFrame with category revenue metrics
    """
    data_dir = Path(__file__).parent.parent.parent / "data"
    
    # Load staged data
    order_items = pl.read_csv(data_dir / "staged" / "order_items.csv")
    products = pl.read_csv(data_dir / "staged" / "products.csv")
    
    # Join order_items with products
    result = order_items.join(products, on="product_id", how="inner")
    
    # Aggregate by category
    result = result.group_by("category").agg([
        pl.col("order_id").n_unique().alias("total_orders"),
        pl.col("quantity").sum().alias("total_units_sold"),
        pl.col("subtotal").sum().alias("gross_revenue"),
        pl.col("discounted_subtotal").sum().alias("discounted_revenue"),
        (pl.col("subtotal").sum() - pl.col("discounted_subtotal").sum())
            .alias("total_discount_given"),
        pl.col("unit_price").mean().alias("avg_unit_price"),
        pl.col("discount_pct").mean().alias("avg_discount_pct"),
    ])
    
    # Add top product per category
    top_products = order_items.join(products, on="product_id", how="inner").group_by("category").agg([
        pl.col("product_name").sort_by(pl.col("quantity").sum().over("product_name")).last()
            .alias("top_product")
    ])
    
    result = result.join(top_products, on="category", how="left")
    
    # Reorder columns
    result = result.select([
        "category",
        "total_orders",
        "total_units_sold",
        "gross_revenue",
        "discounted_revenue",
        "total_discount_given",
        "avg_unit_price",
        "avg_discount_pct",
        "top_product",
    ])
    
    # Save to marts
    output_dir = data_dir / "marts"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "category_revenue.csv"
    
    result.write_csv(output_file)
    
    print(f"✓ Built category revenue: {result.height} rows ({result.width} cols) → data/marts/category_revenue.csv")
    return result


if __name__ == "__main__":
    build_category_revenue()
