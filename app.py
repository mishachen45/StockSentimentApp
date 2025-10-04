import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from yahoo_fin import stock_info as si
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from textwrap import shorten

st.set_page_config(page_title="📈 Stock Sentiment Dashboard", layout="wide")

st.markdown(
    """
    <style>
    body { background-color: #f8fafc; color: #0f172a; }
    .main { background-color: #ffffff; border-radius: 20px; padding: 25px; box-shadow: 0 0 15px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #0f172a !important; font-weight: 700; }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📊 Stock News Sentiment Analyzer (FinBERT Powered)")

# --- Load FinBERT ---
@st.cache_resource
def load_finbert():
    tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
    model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
    return tokenizer, model

tokenizer, model = load_finbert()

def analyze_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    scores = torch.nn.functional.softmax(outputs.logits, dim=-1)
    labels = ['negative', 'neutral', 'positive']
    sentiment = labels[torch.argmax(scores)]
    score = scores[0][torch.argmax(scores)].item()
    if sentiment == "positive":
        return 1 * score
    elif sentiment == "negative":
        return -1 * score
    else:
        return 0

# --- Sidebar ---
st.sidebar.header("🔎 Search Settings")
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g. AAPL, TSLA):", "AAPL").upper()

# --- Fetch News ---
def fetch_news(ticker):
    try:
        news = si.get_news(ticker)
        df = pd.DataFrame(news)
        if df.empty:
            return None
        df = df.head(20)  # Fetch up to 20 recent news
        df["title"] = df["title"].astype(str)
        df["Sentiment Score"] = df["title"].apply(analyze_sentiment)
        df["Summary"] = df["title"].apply(lambda x: shorten(x, width=80, placeholder="..."))
        return df
    except Exception as e:
        st.error(f"Could not fetch news. Error: {e}")
        return None

df = fetch_news(ticker)

if df is not None:
    st.subheader(f"📰 Latest News for {ticker}")

    # --- Sentiment Distribution ---
    sentiment_counts = {
        "Positive": (df["Sentiment Score"] > 0).sum(),
        "Neutral": (df["Sentiment Score"] == 0).sum(),
        "Negative": (df["Sentiment Score"] < 0).sum(),
    }

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 🥧 Sentiment Distribution")
        fig1, ax1 = plt.subplots(figsize=(4, 4))
        ax1.pie(
            sentiment_counts.values(),
            labels=sentiment_counts.keys(),
            autopct="%1.1f%%",
            startangle=90,
            colors=["#22c55e", "#cbd5e1", "#ef4444"]
        )
        ax1.axis("equal")
        st.pyplot(fig1)

    with col2:
        st.markdown("### 📊 Sentiment Score by Article")
        fig2, ax2 = plt.subplots(figsize=(7, 6))
        df_sorted = df.sort_values(by="Sentiment Score", ascending=False)
        ax2.barh(
            df_sorted["Summary"],
            df_sorted["Sentiment Score"],
            color=df_sorted["Sentiment Score"].apply(lambda x: "#22c55e" if x > 0 else "#ef4444" if x < 0 else "#94a3b8")
        )
        ax2.set_xlabel("Sentiment Score")
        ax2.set_ylabel("Headline (shortened)")
        st.pyplot(fig2)

    # --- News Table ---
    st.markdown("### 🗞️ News Headlines")
    st.dataframe(
        df[["title", "publisher", "Sentiment Score"]].rename(columns={"title": "Headline", "publisher": "Source"}),
        use_container_width=True,
        height=700
    )

else:
    st.warning("No news available for this ticker. Try another one.")
