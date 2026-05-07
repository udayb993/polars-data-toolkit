"""
Create derived views from the base data using Polars.
Generates aggregations and filtered views saved as CSV files.
"""

from pathlib import Path
import polars as pl

def main():
    """Create all derived views and save as CSV files."""
    
    # Determine data directory
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("Creating derived views...")
    print("=" * 60)
    
    # Load base data
    print("\nLoading base data...")
    customers = pl.read_csv(str(data_dir / "customers.csv"))
    products = pl.read_csv(str(data_dir / "products.csv"))
    orders = pl.read_csv(str(data_dir / "orders.csv"))
    order_items = pl.read_csv(str(data_dir / "order_items.csv"))
    print("Base data loaded.")
    
    # 1. Active customers view
    print("\n1. Creating active_customers_view...")
    active_customers = customers.filter(pl.col("is_active") == True)
    active_customers.write_csv(str(data_dir / "active_customers_view.csv"))
    print(f"   ✓ Saved: active_customers_view.csv ({len(active_customers)} rows)")
    
    # 2. High value orders view
    print("\n2. Creating high_value_orders_view...")
    high_value_orders = orders.filter(pl.col("total_amount") > 100)
    high_value_orders.write_csv(str(data_dir / "high_value_orders_view.csv"))
    print(f"   ✓ Saved: high_value_orders_view.csv ({len(high_value_orders)} rows)")
    
    # 3. Product sales summary view
    print("\n3. Creating product_sales_summary_view...")
    product_sales_summary = (
        order_items
        .join(products, on="product_id", how="left")
        .group_by("product_id")
        .agg(
            pl.col("product_name").first().alias("product_name"),
            pl.col("quantity").sum().alias("total_quantity_sold"),
            pl.col("subtotal").sum().alias("total_revenue"),
        )
        .sort("product_id")
    )
    product_sales_summary.write_csv(str(data_dir / "product_sales_summary_view.csv"))
    print(f"   ✓ Saved: product_sales_summary_view.csv ({len(product_sales_summary)} rows)")
    
    # 4. Customer order summary view
    print("\n4. Creating customer_order_summary_view...")
    customer_order_summary = (
        orders
        .join(customers, on="customer_id", how="left")
        .group_by("customer_id")
        .agg(
            pl.col("first_name").first().alias("first_name"),
            pl.col("last_name").first().alias("last_name"),
            pl.col("order_id").count().alias("order_count"),
            pl.col("total_amount").sum().alias("total_spend"),
        )
        .sort("customer_id")
    )
    customer_order_summary.write_csv(str(data_dir / "customer_order_summary_view.csv"))
    print(f"   ✓ Saved: customer_order_summary_view.csv ({len(customer_order_summary)} rows)")
    
    # 5. Category revenue view
    print("\n5. Creating category_revenue_view...")
    category_revenue = (
        order_items
        .join(products, on="product_id", how="left")
        .group_by("category")
        .agg(
            pl.col("subtotal").sum().alias("total_revenue"),
            pl.col("quantity").sum().alias("total_quantity_sold"),
        )
        .sort("category")
    )
    category_revenue.write_csv(str(data_dir / "category_revenue_view.csv"))
    print(f"   ✓ Saved: category_revenue_view.csv ({len(category_revenue)} rows)")
    
    print("\n" + "=" * 60)
    print("All views created successfully!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
