"""Master script to run the complete ETL pipeline."""
import sys
from pathlib import Path
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipelines.extract.fetch_products import fetch_products
from pipelines.extract.fetch_users import fetch_users
from pipelines.extract.fetch_carts import fetch_carts
from pipelines.extract.fetch_countries import fetch_countries

from pipelines.transform.transform_products import transform_products
from pipelines.transform.transform_users import transform_users
from pipelines.transform.transform_carts import transform_carts
from pipelines.transform.transform_countries import transform_countries

from pipelines.load.build_order_summary import build_order_summary
from pipelines.load.build_customer_ltv import build_customer_ltv
from pipelines.load.build_category_revenue import build_category_revenue
from pipelines.load.build_monthly_trend import build_monthly_trend


def get_file_size_kb(filepath: Path) -> float:
    """Get file size in kilobytes."""
    if filepath.exists():
        return filepath.stat().st_size / 1024
    return 0


def run_pipeline():
    """Execute the complete ETL pipeline."""
    print("\n" + "=" * 80)
    print("POLARS E-COMMERCE DATA PIPELINE")
    print("=" * 80 + "\n")
    
    data_dir = Path(__file__).parent.parent / "data"
    
    # ========================================================================
    # STEP 1: EXTRACT
    # ========================================================================
    print("=" * 80)
    print("STEP 1: EXTRACT - Fetching raw data from APIs")
    print("=" * 80 + "\n")
    
    try:
        fetch_products()
        fetch_users()
        fetch_carts()
        fetch_countries()
        print()
    except Exception as e:
        print(f"✗ Extract step failed: {e}")
        return False
    
    # ========================================================================
    # STEP 2: TRANSFORM
    # ========================================================================
    print("=" * 80)
    print("STEP 2: TRANSFORM - Cleaning and normalizing data")
    print("=" * 80 + "\n")
    
    try:
        transform_products()
        transform_users()
        transform_carts()
        transform_countries()
        print()
    except Exception as e:
        print(f"✗ Transform step failed: {e}")
        return False
    
    # ========================================================================
    # STEP 3: LOAD
    # ========================================================================
    print("=" * 80)
    print("STEP 3: LOAD - Building analytical marts")
    print("=" * 80 + "\n")
    
    try:
        build_order_summary()
        build_customer_ltv()
        build_category_revenue()
        build_monthly_trend()
        print()
    except Exception as e:
        print(f"✗ Load step failed: {e}")
        return False
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("=" * 80)
    print("PIPELINE SUMMARY")
    print("=" * 80 + "\n")
    
    print("{:<40} {:<15} {:<15}".format("FILE", "ROWS", "SIZE (KB)"))
    print("-" * 70)
    
    # Count rows in CSV files
    try:
        import polars as pl
        
        # Staged files
        for filename in ["products.csv", "customers.csv", "orders.csv", "order_items.csv", "countries.csv"]:
            filepath = data_dir / "staged" / filename
            if filepath.exists():
                df = pl.read_csv(filepath)
                size_kb = get_file_size_kb(filepath)
                print("{:<40} {:<15} {:<15.2f}".format(f"data/staged/{filename}", df.height, size_kb))
        
        print()
        
        # Mart files
        for filename in ["order_summary.csv", "customer_ltv.csv", "category_revenue.csv", "monthly_trend.csv"]:
            filepath = data_dir / "marts" / filename
            if filepath.exists():
                df = pl.read_csv(filepath)
                size_kb = get_file_size_kb(filepath)
                print("{:<40} {:<15} {:<15.2f}".format(f"data/marts/{filename}", df.height, size_kb))
        
    except ImportError:
        print("(Install polars to see row counts in summary)")
    
    print()
    print("=" * 80)
    print("✓ Pipeline completed successfully!")
    print("=" * 80 + "\n")
    
    return True


if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)
