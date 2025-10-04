import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob
from yahoo_fin import stock_info as si
import datetime

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
            background-color: #f7f9fc;
            color: #1a1a1a;
        }
        .main {
            padding: 2rem;
        }
        h1, h2, h3 {
            color: #0b132b;
            font-weight: 700;
        }
        .stTextInput>div>div>input {
            border-radius: 12px;
            border: 1px solid #d9e3f0;
            padding: 10px;
            font-size: 16px;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.6rem;
            color: #0073e6;
        }
        /* Card-like container */
        .card {
            background: white;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
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
    try:
        news_list = si.get_yf_rss(ticker)
        news = []
        for item in news_list:
            title = item["title"]
            link = item["link"]
            date = datetime.datetime.strptime(item["published"], "%Y-%m-%dT%H:%M:%SZ")
            sentiment = analyze_sentiment(title)
            news.append({"Title": title, "Date": date, "Sentiment": sentiment, "Link": link})
        return pd.DataFrame(news)
    except Exception as e:
        st.error(f"Could not fetch news. Error: {e}")
        return pd.DataFrame(columns=["Title", "Date", "Sentiment", "Link"])

# =========================
# 🧭 HEADER
# =========================
st.title("📊 Stock Sentiment Analyzer")
st.markdown("Get real-time market sentiment from recent stock news — clean, fast, and insightful.")

# =========================
# 🔍 INPUT
# =========================
ticker = st.text_input("Enter Stock Ticker (e.g. AAPL, TSLA, NVDA):", "").upper()

if ticker:
    df = get_news(ticker)
    if not df.empty:
        avg_sent = df["Sentiment"].mean()

        # =========================
        # 🧱 LAYOUT — METRICS
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
        # 📊 LAYOUT — CHARTS
        # =========================
        col_pie, col_bar = st.columns([1.2, 1])
        with col_pie:
            st.markdown("#### Sentiment Distribution")
            sentiment_counts = df["Sentiment"].apply(
                lambda x: "Positive" if x > 0 else ("Negative" if x < 0 else "Neutral")
            ).value_counts()
            fig1, ax1 = plt.subplots(figsize=(5, 5))
            ax1.pie(sentiment_counts, labels=sentiment_counts.index, autopct="%1.1f%%", startangle=90)
            ax1.axis("equal")
            st.pyplot(fig1)

        with col_bar:
            st.markdown("#### Sentiment Scores by Article")
            fig2, ax2 = plt.subplots(figsize=(6, 5))
            df_sorted = df.sort_values("Sentiment", ascending=False)
            ax2.barh(df_sorted["Title"].head(10), df_sorted["Sentiment"].head(10))
            ax2.set_xlabel("Sentiment")
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
