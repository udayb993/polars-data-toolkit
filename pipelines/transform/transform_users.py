"""Transform raw users data to staged customers CSV with Polars."""
import json
from pathlib import Path
import polars as pl


def transform_users() -> pl.DataFrame:
    """
    Transform raw users JSON to staged customers CSV.
    
    Loads data/raw/users_raw.json and produces data/staged/customers.csv
    with columns: customer_id, first_name, last_name, full_name, email,
    age, gender, city, country, phone, username
    
    Returns:
        Polars DataFrame with transformed customers
    """
    # Load raw data
    raw_dir = Path(__file__).parent.parent.parent / "data" / "raw"
    raw_file = raw_dir / "users_raw.json"
    
    with open(raw_file, "r") as f:
        users = json.load(f)
    
    # Create DataFrame from list of dicts
    df = pl.DataFrame(users)
    
    # Extract city and state from address
    df = df.with_columns([
        pl.col("address").struct.field("city").alias("city"),
        pl.col("address").struct.field("state").alias("state"),
    ])
    
    # Transform columns
    df = df.select([
        pl.col("id").cast(pl.Int64).alias("customer_id"),
        pl.col("firstName").alias("first_name"),
        pl.col("lastName").alias("last_name"),
        (pl.col("firstName") + pl.lit(" ") + pl.col("lastName")).alias("full_name"),
        pl.col("email"),
        pl.col("age").cast(pl.Int64),
        pl.col("gender"),
        pl.col("city"),
        pl.col("state").alias("country"),
        pl.col("phone"),
        pl.col("username"),
    ])
    
    # Save to staged
    output_dir = Path(__file__).parent.parent.parent / "data" / "staged"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "customers.csv"
    
    df.write_csv(output_file)
    
    print(f"✓ Transformed {df.height} customers ({df.width} cols) → data/staged/customers.csv")
    return df


if __name__ == "__main__":
    transform_users()
