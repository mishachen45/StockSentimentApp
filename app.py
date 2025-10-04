import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob
import datetime
import feedparser

# =========================
# 🎨 PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Stock Sentiment Analyzer",
    page_icon="📊",
    layout="wide",
)

# =========================
# 💅 CUSTOM STYLES
# =========================
st.markdown("""
    <style>
        body {
            background-color: #f8fafc;
            color: #111827;
        }
        h1, h2, h3, h4 {
            color: #0b132b;
            font-weight: 700;
        }
        .stTextInput>div>div>input {
            border-radius: 12px;
            border: 1px solid #d1d5db;
            padding: 10px;
            font-size: 16px;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.6rem;
            color: #2563eb;
        }
    </style>
""", unsafe_allow_html=True)

# =========================
# 🧠 FUNCTIONS
# =========================
def analyze_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity

def get_news(ticker):
    """Fetch up to 20 Yahoo Finance news articles."""
    urls = [
        f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US",
        f"https://finance.yahoo.com/rss/headline?s={ticker}"
    ]
    articles = []
    for url in urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.title
            link = entry.link
            date = datetime.datetime(*entry.published_parsed[:6])
            sentiment = analyze_sentiment(title)
            articles.append({"Title": title, "Date": date, "Sentiment": sentiment, "Link": link})
        if len(articles) >= 20:
            break
    return pd.DataFrame(articles[:20])

# =========================
# 🧭 HEADER
# =========================
st.title("📊 Stock Sentiment Analyzer")
st.markdown("Analyze real-time stock market sentiment from Yahoo Finance news — clean, fast, and accurate.")

# =========================
# 🔍 INPUT
# =========================
ticker = st.text_input("Enter Stock Ticker (e.g. AAPL, TSLA, NVDA):", "").upper()

if ticker:
    df = get_news(ticker)
    if not df.empty:
        avg_sent = df["Sentiment"].mean()

        # =========================
        # 🧱 METRICS
        # =========================
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Sentiment", f"{avg_sent:.2f}")
        with col2:
            st.metric("Positive Articles", f"{(df['Sentiment'] > 0).sum()}")
        with col3:
            st.metric("Negative Articles", f"{(df['Sentiment'] < 0).sum()}")

        st.markdown("### 📰 News Headlines")

        # =========================
        # 📊 CHARTS
        # =========================
        col_pie, col_bar = st.columns([1.2, 1])

        # --- PIE CHART ---
        with col_pie:
            st.markdown("#### Sentiment Distribution")
            sentiment_labels = df["Sentiment"].apply(
                lambda x: "Positive" if x > 0 else ("Negative" if x < 0 else "Neutral")
            )
            sentiment_counts = sentiment_labels.value_counts()
            colors = ["green" if label == "Positive" else "red" if label == "Negative" else "gray"
                      for label in sentiment_counts.index]
            fig1, ax1 = plt.subplots(figsize=(5, 5))
            ax1.pie(sentiment_counts, labels=sentiment_counts.index, autopct="%1.1f%%",
                    startangle=90, colors=colors)
            ax1.axis("equal")
            st.pyplot(fig1)

        # --- BAR CHART ---
        with col_bar:
            st.markdown("#### Sentiment Scores by Article")
            df_sorted = df.sort_values("Sentiment", ascending=False)
            df_sorted["ShortTitle"] = df_sorted["Title"].apply(
                lambda t: " ".join(t.split()[:8]) + ("..." if len(t.split()) > 8 else "")
            )
            fig2, ax2 = plt.subplots(figsize=(7, 8))  # taller chart
            ax2.barh(df_sorted["ShortTitle"], df_sorted["Sentiment"],
                     color=["green" if s > 0 else "red" if s < 0 else "gray" for s in df_sorted["Sentiment"]])
            ax2.set_xlabel("Sentiment Score")
            plt.tight_layout()
            st.pyplot(fig2)

        # =========================
        # 🗞 NEWS TABLE
        # =========================
        st.markdown("#### 🧾 Detailed Headlines")
        st.dataframe(
            df[["Date", "Title", "Sentiment"]],
            use_container_width=True,
            hide_index=True,
            height=700
        )

    else:
        st.warning("No news articles found for this ticker.")
else:
    st.info("👆 Enter a stock symbol above to start analyzing sentiment.")
