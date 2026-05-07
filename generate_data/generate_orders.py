"""
Generate order data.
Creates 500 order records with references to existing customers.
"""

import polars as pl
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

def generate_orders(n: int = 500, max_customer_id: int = 200) -> pl.DataFrame:
    """
    Generate n order records.
    
    Args:
        n: Number of orders to generate (default: 500)
        max_customer_id: Maximum customer_id to reference (default: 200)
    
    Returns:
        DataFrame with order data
    """
    orders = []
    statuses = ["pending", "shipped", "delivered", "cancelled"]
    
    # Random order dates between 2022-01-01 and 2024-01-01
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2024, 1, 1)
    days_between = (end_date - start_date).days
    
    for i in range(1, n + 1):
        random_days = fake.random.randint(0, days_between)
        order_date = start_date + timedelta(days=random_days)
        
        order = {
            "order_id": i,
            "customer_id": fake.random.randint(1, max_customer_id),
            "order_date": order_date.date(),
            "status": fake.random_element(statuses),
            "total_amount": 0.0,  # Will be updated after order_items are created
        }
        orders.append(order)
    
    df = pl.DataFrame(orders)
    return df

if __name__ == "__main__":
    df = generate_orders()
    print(df)
