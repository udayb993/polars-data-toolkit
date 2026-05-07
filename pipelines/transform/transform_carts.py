"""Transform raw carts data to staged orders and order_items CSVs with Polars."""
import json
from pathlib import Path
import polars as pl


def transform_carts() -> tuple[pl.DataFrame, pl.DataFrame]:
    """
    Transform raw carts JSON to staged orders and order_items CSVs.
    
    Loads data/raw/carts_raw.json and produces:
    - data/staged/orders.csv
    - data/staged/order_items.csv
    
    Returns:
        Tuple of (orders_df, order_items_df) DataFrames
    """
    # Load raw data
    raw_dir = Path(__file__).parent.parent.parent / "data" / "raw"
    raw_file = raw_dir / "carts_raw.json"
    
    with open(raw_file, "r") as f:
        carts = json.load(f)
    
    # Create orders DataFrame
    orders_data = []
    for cart in carts:
        order_month = f"2024-{(cart['id'] % 12) + 1:02d}"
        orders_data.append({
            "order_id": cart["id"],
            "customer_id": cart["userId"],
            "total_products": cart["totalProducts"],
            "total_quantity": cart["totalQuantity"],
            "total_amount": cart["total"],
            "discounted_total": cart["discountedTotal"],
            "discount_amount": cart["total"] - cart["discountedTotal"],
            "order_month": order_month,
        })
    
    orders_df = pl.DataFrame(orders_data).with_columns([
        pl.col("order_id").cast(pl.Int64),
        pl.col("customer_id").cast(pl.Int64),
        pl.col("total_products").cast(pl.Int64),
        pl.col("total_quantity").cast(pl.Int64),
        pl.col("total_amount").cast(pl.Float64),
        pl.col("discounted_total").cast(pl.Float64),
        pl.col("discount_amount").cast(pl.Float64),
        pl.col("order_month").cast(pl.Utf8),
    ])
    
    # Create order_items DataFrame by exploding products
    order_items_data = []
    order_item_id = 1
    
    for cart in carts:
        for product in cart.get("products", []):
            order_items_data.append({
                "order_item_id": order_item_id,
                "order_id": cart["id"],
                "product_id": product["id"],
                "product_name": product["title"],
                "quantity": product["quantity"],
                "unit_price": product["price"],
                "discount_pct": product["discountPercentage"],
                "subtotal": product["quantity"] * product["price"],
                "discounted_subtotal": product["quantity"] * product["price"] * (1 - product["discountPercentage"] / 100),
            })
            order_item_id += 1
    
    order_items_df = pl.DataFrame(order_items_data).with_columns([
        pl.col("order_item_id").cast(pl.Int64),
        pl.col("order_id").cast(pl.Int64),
        pl.col("product_id").cast(pl.Int64),
        pl.col("quantity").cast(pl.Int64),
        pl.col("unit_price").cast(pl.Float64),
        pl.col("discount_pct").cast(pl.Float64),
        pl.col("subtotal").cast(pl.Float64),
        pl.col("discounted_subtotal").cast(pl.Float64),
    ])
    
    # Save to staged
    output_dir = Path(__file__).parent.parent.parent / "data" / "staged"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    orders_file = output_dir / "orders.csv"
    order_items_file = output_dir / "order_items.csv"
    
    orders_df.write_csv(orders_file)
    order_items_df.write_csv(order_items_file)
    
    print(f"✓ Transformed {orders_df.height} orders ({orders_df.width} cols) → data/staged/orders.csv")
    print(f"✓ Transformed {order_items_df.height} order items ({order_items_df.width} cols) → data/staged/order_items.csv")
    
    return orders_df, order_items_df


if __name__ == "__main__":
    transform_carts()
