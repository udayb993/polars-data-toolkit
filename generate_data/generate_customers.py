"""
Generate customer data.
Creates 200 customer records with realistic names, emails, and metadata.
"""

import polars as pl
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

def generate_customers(n: int = 200) -> pl.DataFrame:
    """
    Generate n customer records.
    
    Args:
        n: Number of customers to generate (default: 200)
    
    Returns:
        DataFrame with customer data
    """
    customers = []
    countries = ["UK", "US", "Germany", "France", "India"]
    
    for i in range(1, n + 1):
        # Random signup date between 2020-01-01 and 2023-12-31
        start_date = datetime(2020, 1, 1)
        end_date = datetime(2023, 12, 31)
        days_between = (end_date - start_date).days
        random_days = fake.random.randint(0, days_between)
        signup_date = start_date + timedelta(days=random_days)
        
        customer = {
            "customer_id": i,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "country": fake.random_element(countries),
            "signup_date": signup_date.date(),
            "is_active": fake.boolean(chance_of_getting_true=85),  # 85% active
        }
        customers.append(customer)
    
    df = pl.DataFrame(customers)
    return df

if __name__ == "__main__":
    df = generate_customers()
    print(df)
