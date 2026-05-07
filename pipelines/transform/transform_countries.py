"""Transform raw countries data to staged CSV with Polars."""
import json
from pathlib import Path
import polars as pl


def transform_countries() -> pl.DataFrame:
    """
    Transform raw countries JSON to staged CSV.
    
    Loads data/raw/countries_raw.json and produces data/staged/countries.csv
    with columns: country_name, official_name, region, subregion, population,
    currency_code, currency_name, flag_emoji
    
    Returns:
        Polars DataFrame with transformed countries
    """
    # Load raw data
    raw_dir = Path(__file__).parent.parent.parent / "data" / "raw"
    raw_file = raw_dir / "countries_raw.json"
    
    with open(raw_file, "r") as f:
        countries = json.load(f)
    
    # Create DataFrame from list of dicts
    df = pl.DataFrame(countries)
    
    # Extract nested fields
    countries_data = []
    for country in countries:
        name = country.get("name", {})
        currencies = country.get("currencies", {})
        flags = country.get("flags", {})
        
        # Get first currency code and name
        currency_code = "Unknown"
        currency_name = "Unknown"
        if currencies:
            currency_code = list(currencies.keys())[0]
            currency_name = currencies[currency_code].get("name", "Unknown")
        
        # Get flag emoji
        flag_emoji = flags.get("emoji", "")
        
        countries_data.append({
            "country_name": name.get("common", ""),
            "official_name": name.get("official", ""),
            "region": country.get("region", ""),
            "subregion": country.get("subregion") or "Unknown",
            "population": country.get("population", 0),
            "currency_code": currency_code,
            "currency_name": currency_name,
            "flag_emoji": flag_emoji,
        })
    
    df = pl.DataFrame(countries_data).with_columns([
        pl.col("country_name").cast(pl.Utf8),
        pl.col("official_name").cast(pl.Utf8),
        pl.col("region").cast(pl.Utf8),
        pl.col("subregion").cast(pl.Utf8),
        pl.col("population").cast(pl.Int64),
        pl.col("currency_code").cast(pl.Utf8),
        pl.col("currency_name").cast(pl.Utf8),
        pl.col("flag_emoji").cast(pl.Utf8),
    ])
    
    # Save to staged
    output_dir = Path(__file__).parent.parent.parent / "data" / "staged"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "countries.csv"
    
    df.write_csv(output_file)
    
    print(f"✓ Transformed {df.height} countries ({df.width} cols) → data/staged/countries.csv")
    return df


if __name__ == "__main__":
    transform_countries()
