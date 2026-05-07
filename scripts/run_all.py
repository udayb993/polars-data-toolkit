"""
Master script to generate all data and save as CSV files.
Orchestrates the generation of customers, products, orders, and order items.
Also updates order totals based on order items.
"""

import sys
from pathlib import Path
import polars as pl

# Add parent directory to path to import generate_data module
sys.path.insert(0, str(Path(__file__).parent.parent))

from generate_data.generate_customers import generate_customers
from generate_data.generate_products import generate_products
from generate_data.generate_orders import generate_orders
from generate_data.generate_order_items import generate_order_items

def main():
    """Generate all data and save to CSV files."""
    
    # Determine data directory
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("Generating e-commerce data...")
    print("=" * 60)
    
    # 1. Generate customers
    print("\n1. Generating customers...")
    customers_df = generate_customers(n=200)
    customers_path = data_dir / "customers.csv"
    customers_df.write_csv(str(customers_path))
    print(f"   ✓ Saved: {customers_path.name}")
    print(f"   Rows: {len(customers_df)}")
    
    # 2. Generate products
    print("\n2. Generating products...")
    products_df = generate_products(n=50)
    products_path = data_dir / "products.csv"
    products_df.write_csv(str(products_path))
    print(f"   ✓ Saved: {products_path.name}")
    print(f"   Rows: {len(products_df)}")
    
    # 3. Generate orders
    print("\n3. Generating orders...")
    orders_df = generate_orders(n=500, max_customer_id=200)
    orders_path = data_dir / "orders.csv"
    # Don't save yet - need to update totals first
    print(f"   Generated {len(orders_df)} orders")
    
    # 4. Generate order items
    print("\n4. Generating order items...")
    order_items_df = generate_order_items(
        n=1500,
        max_order_id=500,
        max_product_id=50,
        products_df=products_df,
    )
    order_items_path = data_dir / "order_items.csv"
    order_items_df.write_csv(str(order_items_path))
    print(f"   ✓ Saved: {order_items_path.name}")
    print(f"   Rows: {len(order_items_df)}")
    
    # 5. Update order totals based on order items
    print("\n5. Calculating order totals...")
    order_totals = (
        order_items_df
        .group_by("order_id")
        .agg(pl.col("subtotal").sum().alias("total_amount"))
    )
    
    # Join back to orders and update
    orders_df = (
        orders_df
        .join(order_totals, on="order_id", how="left")
        .with_columns(
            pl.col("total_amount_right")
            .fill_null(0.0)
            .alias("total_amount_updated")
        )
        .select(["order_id", "customer_id", "order_date", "status", "total_amount_updated"])
        .rename({"total_amount_updated": "total_amount"})
    )
    
    orders_df.write_csv(str(orders_path))
    print(f"   ✓ Saved: {orders_path.name}")
    print(f"   Rows: {len(orders_df)}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("Data generation complete!")
    print("=" * 60)
    print(f"\nFiles saved to: {data_dir}")
    print(f"  - customers.csv ({len(customers_df)} rows)")
    print(f"  - products.csv ({len(products_df)} rows)")
    print(f"  - orders.csv ({len(orders_df)} rows)")
    print(f"  - order_items.csv ({len(order_items_df)} rows)")
    print("\n")

if __name__ == "__main__":
    main()
