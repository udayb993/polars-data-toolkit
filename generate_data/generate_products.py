"""
Generate product data.
Creates 50 product records with realistic names, categories, and pricing.
"""

import polars as pl
from faker import Faker

fake = Faker()

def generate_products(n: int = 50) -> pl.DataFrame:
    """
    Generate n product records.
    
    Args:
        n: Number of products to generate (default: 50)
    
    Returns:
        DataFrame with product data
    """
    products = []
    categories = ["Electronics", "Clothing", "Books", "Home", "Sports"]
    
    for i in range(1, n + 1):
        product = {
            "product_id": i,
            "product_name": fake.word().capitalize() + " " + fake.word().capitalize(),
            "category": fake.random_element(categories),
            "price": round(fake.random.uniform(5.00, 500.00), 2),
            "stock_quantity": fake.random.randint(0, 1000),
        }
        products.append(product)
    
    df = pl.DataFrame(products)
    return df

if __name__ == "__main__":
    df = generate_products()
    print(df)
