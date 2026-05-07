"""
Create joined tables combining data from multiple sources.
Generates master detail tables and enriched data views.
"""

from pathlib import Path
import polars as pl

def main():
    """Create all joined tables and save as CSV files."""
    
    # Determine data directory
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("Creating joined tables...")
    print("=" * 60)
    
    # Load base data
    print("\nLoading base data...")
    customers = pl.read_csv(str(data_dir / "customers.csv"))
    products = pl.read_csv(str(data_dir / "products.csv"))
    orders = pl.read_csv(str(data_dir / "orders.csv"))
    order_items = pl.read_csv(str(data_dir / "order_items.csv"))
    print("Base data loaded.")
    
    # 1. Orders with customer info
    print("\n1. Creating orders_with_customer_info...")
    orders_with_customers = (
        orders
        .join(customers, on="customer_id", how="left")
        .select([
            "order_id",
            "order_date",
            "status",
            "total_amount",
            "first_name",
            "last_name",
            "country",
        ])
    )
    orders_with_customers.write_csv(str(data_dir / "orders_with_customer_info.csv"))
    print(f"   ✓ Saved: orders_with_customer_info.csv ({len(orders_with_customers)} rows)")
    
    # 2. Order items with product info
    print("\n2. Creating order_items_with_product_info...")
    order_items_with_products = (
        order_items
        .join(products, on="product_id", how="left")
        .select([
            "order_item_id",
            "order_id",
            "product_name",
            "category",
            "quantity",
            "unit_price",
            "subtotal",
        ])
    )
    order_items_with_products.write_csv(str(data_dir / "order_items_with_product_info.csv"))
    print(f"   ✓ Saved: order_items_with_product_info.csv ({len(order_items_with_products)} rows)")
    
    # 3. Full order detail (all 4 tables joined)
    print("\n3. Creating full_order_detail...")
    full_order_detail = (
        order_items
        .join(orders, on="order_id", how="left")
        .join(customers, on="customer_id", how="left")
        .join(products, on="product_id", how="left")
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
    full_order_detail.write_csv(str(data_dir / "full_order_detail.csv"))
    print(f"   ✓ Saved: full_order_detail.csv ({len(full_order_detail)} rows)")
    
    print("\n" + "=" * 60)
    print("All joins created successfully!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
