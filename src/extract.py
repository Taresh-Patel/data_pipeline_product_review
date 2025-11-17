from pathlib import Path
import pandas as pd
import requests
import mongomock

def extract_data():
    """
    - Reads local JSONL file from data/raw/product_reviews_sales.jsonl
    - Calls FakeStore API for products
    - Returns two DataFrames: reviews and products
    """

    # Get project root
    base_dir = Path(__file__).resolve().parent.parent

    # 1. Setup mock MongoDB (in-memory)
    client = mongomock.MongoClient()
    db = client.my_mock_database
    review_collection = db.reviews

    # 2. Read local JSONL data
    jsonl_path = base_dir / "data" / "raw" / "product_reviews_sales.jsonl"
    if not jsonl_path.exists():
        raise FileNotFoundError(f"Expected file not found: {jsonl_path}")

    df_reviews = pd.read_json(jsonl_path, lines=True)

    # 3. Fetch products from FakeStore API
    response = requests.get("https://fakestoreapi.com/products")
    response.raise_for_status()
    products = response.json()
    products_df = pd.DataFrame(products)

    return df_reviews, products_df