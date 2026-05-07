"""Transform raw products data to staged CSV with Polars."""
import json
from pathlib import Path
import polars as pl


def transform_products() -> pl.DataFrame:
    """
    Transform raw products JSON to staged CSV.
    
    Loads data/raw/products_raw.json and produces data/staged/products.csv
    with columns: product_id, product_name, category, brand, price,
    original_price, discount_pct, rating, stock_quantity, description
    
    Returns:
        Polars DataFrame with transformed products
    """
    # Load raw data
    raw_dir = Path(__file__).parent.parent.parent / "data" / "raw"
    raw_file = raw_dir / "products_raw.json"
    
    with open(raw_file, "r") as f:
        products = json.load(f)
    
    # Create DataFrame from list of dicts
    df = pl.DataFrame(products)
    
    # Transform columns
    df = df.select([
        pl.col("id").cast(pl.Int64).alias("product_id"),
        pl.col("title").alias("product_name"),
        pl.col("category"),
        pl.col("brand").fill_null("Unknown"),
        pl.col("price").cast(pl.Float64),
        (pl.col("price") / (1 - pl.col("discountPercentage") / 100))
            .round(2).alias("original_price"),
        pl.col("discountPercentage").alias("discount_pct").cast(pl.Float64),
        pl.col("rating").cast(pl.Float64),
        pl.col("stock").cast(pl.Int64).alias("stock_quantity"),
        pl.col("description").alias("description"),
    ])
    
    # Save to staged
    output_dir = Path(__file__).parent.parent.parent / "data" / "staged"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "products.csv"
    
    df.write_csv(output_file)
    
    print(f"✓ Transformed {df.height} products ({df.width} cols) → data/staged/products.csv")
    return df


if __name__ == "__main__":
    transform_products()
