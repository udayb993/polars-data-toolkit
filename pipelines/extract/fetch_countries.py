"""Fetch countries from REST Countries API."""
import json
from pathlib import Path
import httpx


def fetch_countries() -> list[dict]:
    """
    Fetch countries from REST Countries API.
    
    Returns:
        List of country dictionaries with keys: name, region, subregion,
        currencies, population, flags
    
    Raises:
        httpx.HTTPError: If API call fails
    """
    url = "https://restcountries.com/v3.1/all?fields=name,region,subregion,currencies,population,flags"
    
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        countries = response.json()
        
        # Save raw response
        output_dir = Path(__file__).parent.parent.parent / "data" / "raw"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "countries_raw.json"
        
        with open(output_file, "w") as f:
            json.dump(countries, f, indent=2)
        
        print(f"✓ Fetched {len(countries)} countries → data/raw/countries_raw.json")
        return countries
        
    except httpx.HTTPError as e:
        print(f"✗ Error fetching countries: {e}")
        raise


if __name__ == "__main__":
    fetch_countries()
