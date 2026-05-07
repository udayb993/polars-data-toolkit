"""Fetch products from DummyJSON API."""
import json
from pathlib import Path
import httpx


def fetch_products() -> list[dict]:
    """
    Fetch products from DummyJSON API.
    
    Returns:
        List of product dictionaries with keys: id, title, category, brand, price,
        discountPercentage, rating, stock, description
    
    Raises:
        httpx.HTTPError: If API call fails
    """
    url = "https://dummyjson.com/products?limit=100&skip=0"
    
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        products = data.get("products", [])
        
        # Save raw response
        output_dir = Path(__file__).parent.parent.parent / "data" / "raw"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "products_raw.json"
        
        with open(output_file, "w") as f:
            json.dump(products, f, indent=2)
        
        print(f"✓ Fetched {len(products)} products → data/raw/products_raw.json")
        return products
        
    except httpx.HTTPError as e:
        print(f"✗ Error fetching products: {e}")
        raise


if __name__ == "__main__":
    fetch_products()
