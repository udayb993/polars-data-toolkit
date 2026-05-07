"""Fetch carts (orders) from DummyJSON API."""
import json
from pathlib import Path
import httpx


def fetch_carts() -> list[dict]:
    """
    Fetch carts from DummyJSON API.
    
    Returns:
        List of cart dictionaries with keys: id, userId, total, discountedTotal,
        totalProducts, totalQuantity, products
    
    Raises:
        httpx.HTTPError: If API call fails
    """
    url = "https://dummyjson.com/carts?limit=100&skip=0"
    
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        carts = data.get("carts", [])
        
        # Save raw response
        output_dir = Path(__file__).parent.parent.parent / "data" / "raw"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "carts_raw.json"
        
        with open(output_file, "w") as f:
            json.dump(carts, f, indent=2)
        
        print(f"✓ Fetched {len(carts)} carts → data/raw/carts_raw.json")
        return carts
        
    except httpx.HTTPError as e:
        print(f"✗ Error fetching carts: {e}")
        raise


if __name__ == "__main__":
    fetch_carts()
