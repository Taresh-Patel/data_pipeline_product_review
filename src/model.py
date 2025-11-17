# scripts/model.py
import os
from pathlib import Path
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


def add_sentiment(
    input_path="data/processed/reviews_products.processed.csv",
    output_path="data/processed/reviews_products_with_sentiment.csv",
    model_dir="sst2_model"
):
    """
    Adds sentiment predictions using a local DistilBERT SST-2 model.
    Creates 'sentiment' and 'confidence' columns.
    """

    # Offline mode
    os.environ["TRANSFORMERS_OFFLINE"] = "1"  #Run in offline mode

    # Load data
    df = pd.read_csv(input_path)

    # Detect text column
    text_col = None
    for c in df.columns:
        if "review" in c.lower() or "text" in c.lower() or "comment" in c.lower():
            text_col = c
            break
    if not text_col:
        raise ValueError("Could not find a review text column in the dataset.")

    # Load local model + tokenizer
    tok = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
    mdl = AutoModelForSequenceClassification.from_pretrained(model_dir, local_files_only=True)
    mdl.eval()

    # Tokenize all texts (batched for speed)
    texts = df[text_col].astype(str).tolist()
    inputs = tok(texts, padding=True, truncation=True, return_tensors="pt")

    # Inference
    with torch.no_grad():
        outputs = mdl(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

    # Convert to labels + confidences
    predicted_labels = torch.argmax(probs, dim=1).tolist()
    confidences = probs.max(dim=1).values.tolist()

    # Map labels to human-readable classes
    label_map = {0: "NEGATIVE", 1: "POSITIVE"}
    sentiments = [label_map[i] for i in predicted_labels]

    # Add to DataFrame
    df["sentiment"] = sentiments
    df["confidence"] = confidences

    # Save
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f" Sentiment analysis complete → {output_path}")
    return df


if __name__ == "__main__":
    add_sentiment()
