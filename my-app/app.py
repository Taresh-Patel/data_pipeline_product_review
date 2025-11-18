import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="🛍️ Product Reviews Insights", layout="wide")

st.title("🛍️ Product Reviews Insights: Sentiment, Ratings & Sales")
st.caption("Mini dashboard powered ETL + DistilBERT sentiment model")

# ---- Data loading ----
LOCAL_CSV = Path("data/processed/reviews_products_with_sentiment.csv")
RAW_URL = "https://raw.githubusercontent.com/Tech-creator-neo/test_pipeline/main/data/processed/reviews_products_with_sentiment.csv"

@st.cache_data(ttl=300)
def load_data() -> pd.DataFrame:
    # Prefer local file (when running locally) else fall back to GitHub raw
    if LOCAL_CSV.exists():
        return pd.read_csv(LOCAL_CSV)
    return pd.read_csv(RAW_URL)

df = load_data()

# ---- Sidebar filters ----
st.sidebar.header("Filters")
# Sentiment filter
sentiments = sorted(df["sentiment"].dropna().unique()) if "sentiment" in df else []
selected_sentiments = st.sidebar.multiselect("Sentiment", sentiments, default=sentiments)

# Category filter (if present)
cats = sorted(df["category"].dropna().unique()) if "category" in df else []
selected_cats = st.sidebar.multiselect("Category", cats, default=cats)

# Price range (if present)
if "price" in df:
    min_price = float(df["price"].min())
    max_price = float(df["price"].max())
    price_range = st.sidebar.slider("Price range", min_price, max_price, (min_price, max_price))
else:
    price_range = None

# Apply filters
df_f = df.copy()
if selected_sentiments:
    df_f = df_f[df_f["sentiment"].isin(selected_sentiments)]
if selected_cats:
    df_f = df_f[df_f["category"].isin(selected_cats)]
if price_range is not None and "price" in df_f:
    lo, hi = price_range
    df_f = df_f[(df_f["price"] >= lo) & (df_f["price"] <= hi)]

# ---- KPIs ----
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Reviews", f"{len(df_f):,}")
with c2:
    st.metric("Products", f"{df_f['id'].nunique() if 'id' in df_f else df_f.shape[0]:,}")
with c3:
    st.metric("Positivity %", f"{(df_f['sentiment'].eq('POSITIVE').mean()*100):.1f}%" if 'sentiment' in df_f else "—")
with c4:
    st.metric("Avg confidence", f"{df_f['confidence'].mean():.2f}" if 'confidence' in df_f else "—")

st.divider()

# ---- 1) Sentiment distribution ----
if "sentiment" in df_f:
    fig1 = px.histogram(df_f, x="sentiment", color="sentiment", title="Sentiment Distribution")
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("No 'sentiment' column found.")

# ---- 2) Model confidence by sentiment ----
if {"sentiment", "confidence"}.issubset(df_f.columns):
    avg_conf = df_f.groupby("sentiment", as_index=False)["confidence"].mean()
    fig2 = px.bar(avg_conf, x="sentiment", y="confidence", color="sentiment",
                  title="Model Confidence by Sentiment", text="confidence")
    fig2.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    st.plotly_chart(fig2, use_container_width=True)

# ---- 3) Ratings vs sentiment ----
if {"sentiment", "rating_rate"}.issubset(df_f.columns):
    fig3 = px.box(df_f, x="sentiment", y="rating_rate", color="sentiment",
                  title="Ratings vs Sentiment")
    st.plotly_chart(fig3, use_container_width=True)

# ---- 4) Sentiment by category ----
if {"category", "sentiment"}.issubset(df_f.columns):
    sent_by_cat = df_f.groupby(["category", "sentiment"]).size().reset_index(name="count")
    fig4 = px.bar(sent_by_cat, x="category", y="count", color="sentiment",
                  title="Sentiment by Product Category", barmode="group")
    st.plotly_chart(fig4, use_container_width=True)

# ---- Table (head) ----
st.subheader("Sample of current data")
st.dataframe(df_f.head(100), use_container_width=True)
