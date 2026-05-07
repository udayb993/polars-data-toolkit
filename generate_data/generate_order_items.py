"""
Generate order items data.
Creates 1500 order item records with references to existing orders and products.
Calculates subtotals and can be used to update order totals.
"""

import polars as pl
from faker import Faker

fake = Faker()

def generate_order_items(
    n: int = 1500,
    max_order_id: int = 500,
    max_product_id: int = 50,
    products_df: pl.DataFrame = None,
) -> pl.DataFrame:
    """
    Generate n order item records.
    
    Args:
        n: Number of order items to generate (default: 1500)
        max_order_id: Maximum order_id to reference (default: 500)
        max_product_id: Maximum product_id to reference (default: 50)
        products_df: DataFrame with product prices (optional, for realistic pricing)
    
    Returns:
        DataFrame with order item data
    """
    order_items = []
    
    # Create a price lookup if products_df is provided
    price_map = {}
    if products_df is not None:
        for row in products_df.iter_rows(named=True):
            price_map[row["product_id"]] = row["price"]
    
    for i in range(1, n + 1):
        product_id = fake.random.randint(1, max_product_id)
        quantity = fake.random.randint(1, 10)
        
        # Use actual product price if available, otherwise use random price
        if product_id in price_map:
            unit_price = price_map[product_id]
        else:
            unit_price = round(fake.random.uniform(5.00, 500.00), 2)
        
        subtotal = round(quantity * unit_price, 2)
        
        order_item = {
            "order_item_id": i,
            "order_id": fake.random.randint(1, max_order_id),
            "product_id": product_id,
            "quantity": quantity,
            "unit_price": unit_price,
            "subtotal": subtotal,
        }
        order_items.append(order_item)
    
    df = pl.DataFrame(order_items)
    return df

if __name__ == "__main__":
    df = generate_order_items()
    print(df)
