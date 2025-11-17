from pathlib import Path
import pandas as pd

def transform_data(df_reviews, products_df):
    """
    - Flatten products_df['rating'] -> rating_rate, rating_count
    - Harmonize key (productId -> product_id)
    - Left-join reviews to products on product_id == id
    - Write CSV to data/processed/
    """

    df_reviews = df_reviews.copy()
    products_df = products_df.copy()

    # 1) Flatten rating
    if "rating" in products_df.columns:
        rating_df = pd.json_normalize(products_df["rating"]).add_prefix("rating_")
        products_df = products_df.drop(columns=["rating"]).reset_index(drop=True).join(rating_df)

    # 2) Harmonize key
    if "product_id" not in df_reviews.columns and "productId" in df_reviews.columns:
        df_reviews = df_reviews.rename(columns={"productId": "product_id"})

    # 3) Comparable types
    if "product_id" in df_reviews.columns:
        df_reviews["product_id"] = pd.to_numeric(df_reviews["product_id"], errors="coerce")
    if "id" in products_df.columns:
        products_df["id"] = pd.to_numeric(products_df["id"], errors="coerce")

    # 4) Left join
    combined_df = df_reviews.merge(products_df, left_on="product_id", right_on="id", how="left")

    # 5) Write CSV (absolute path)
    base_dir = Path(__file__).resolve().parent.parent
    out_dir = base_dir / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "reviews_products.processed.csv"
    combined_df.to_csv(csv_path, index=False)

    print(f"Combined data saved to: {csv_path}")
    return combined_df