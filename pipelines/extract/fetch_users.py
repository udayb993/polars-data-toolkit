"""Fetch users (customers) from DummyJSON API."""
import json
from pathlib import Path
import httpx


def fetch_users() -> list[dict]:
    """
    Fetch users from DummyJSON API.
    
    Returns:
        List of user dictionaries with keys: id, firstName, lastName, email, age,
        gender, address, phone, username
    
    Raises:
        httpx.HTTPError: If API call fails
    """
    url = "https://dummyjson.com/users?limit=100&skip=0"
    
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        users = data.get("users", [])
        
        # Save raw response
        output_dir = Path(__file__).parent.parent.parent / "data" / "raw"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "users_raw.json"
        
        with open(output_file, "w") as f:
            json.dump(users, f, indent=2)
        
        print(f"✓ Fetched {len(users)} users → data/raw/users_raw.json")
        return users
        
    except httpx.HTTPError as e:
        print(f"✗ Error fetching users: {e}")
        raise


if __name__ == "__main__":
    fetch_users()
