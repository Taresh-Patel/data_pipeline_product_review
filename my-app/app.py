import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="🛍️ Product Reviews Insights", layout="wide")

st.title("🛍️ Product Reviews Insights")
st.caption("Mini dashboard powered by your ETL + DistilBERT sentiment model")


# 1) LOAD DATA
LOCAL_CSV = Path("data/processed/reviews_products_with_sentiment.csv")

def load_data() -> pd.DataFrame:
    if not LOCAL_CSV.exists():
        st.error(f"CSV not found at: {LOCAL_CSV.resolve()}")
        st.stop()
    return pd.read_csv(LOCAL_CSV)

df = load_data()

# 2) KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("Reviews", f"{len(df):,}")
c2.metric("Products", f"{df['id'].nunique() if 'id' in df else df.shape[0]:,}")
c3.metric("Positivity %", f"{(df['sentiment'].eq('POSITIVE').mean()*100):.1f}%" if "sentiment" in df else "—")
c4.metric("Avg confidence", f"{df['confidence'].mean():.2f}" if "confidence" in df else "—")

st.divider()

# 3) VISUALIZATION PLACEHOLDERS


# fig1 = ...
# st.plotly_chart(fig1, use_container_width=True)

# fig2 = ...
# st.pyplot(fig2, use_container_width=True)

# fig3 = ...
# st.plotly_chart(fig3, use_container_width=True)

# 4) DATA PREVIEW
st.subheader("Sample of Data")
st.dataframe(df.head(100), use_container_width=True)
