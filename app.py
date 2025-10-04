import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import feedparser
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import datetime

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="📊 Stock News Sentiment Analyzer", layout="wide")

st.markdown("""
<style>
body { background-color: #f8fafc; color: #0f172a; }
h1, h2, h3, h4 { color: #0f172a; font-weight: 700; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Stock News Sentiment Analyzer (FinBERT Powered)")

# =========================
# LOAD FINBERT
# =========================
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

# =========================
# USER INPUT
# =========================
ticker = st.text_input("Enter Stock Ticker (e.g. AAPL, TSLA):", "").upper()

# =========================
# FETCH NEWS VIA RSS
# =========================
def fetch_news_rss(ticker):
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries[:20]:  # up to 20 articles
        title = entry.title
        link = entry.link
        date = datetime.datetime(*entry.published_parsed[:6])
        sentiment = analyze_sentiment(title)
        articles.append({"Title": title, "Link": link, "Date": date, "Sentiment Score": sentiment})
    return pd.DataFrame(articles)

if ticker:
    df = fetch_news_rss(ticker)
    if df.empty:
        st.warning("No news articles found for this ticker.")
    else:
        # =========================
        # METRICS
        # =========================
        avg_sent = df["Sentiment Score"].mean()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Sentiment", f"{avg_sent:.2f}")
        with col2:
            st.metric("Positive Articles", f"{(df['Sentiment Score'] > 0).sum()}")
        with col3:
            st.metric("Negative Articles", f"{(df['Sentiment Score'] < 0).sum()}")

        # =========================
        # CHARTS: PIE + BAR (side by side)
        # =========================
        col_pie, col_bar = st.columns([1.2, 1])

        # --- PIE CHART ---
        with col_pie:
            st.markdown("### 🥧 Sentiment Distribution")
            sentiment_counts = {
                "Positive": (df["Sentiment Score"] > 0).sum(),
                "Neutral": (df["Sentiment Score"] == 0).sum(),
                "Negative": (df["Sentiment Score"] < 0).sum()
            }
            fig1, ax1 = plt.subplots(figsize=(5,7))
            ax1.pie(
                sentiment_counts.values(),
                labels=sentiment_counts.keys(),
                autopct="%1.1f%%",
                startangle=90,
                colors=["#22c55e", "#cbd5e1", "#ef4444"]
            )
            ax1.axis("equal")
            st.pyplot(fig1)

        # --- BAR CHART ---
        with col_bar:
            st.markdown("### 📊 Sentiment Score by Article")
            df_sorted = df.sort_values(by="Sentiment Score", ascending=False)
            df_sorted["ShortTitle"] = df_sorted["Title"].apply(
                lambda x: " ".join(x.split()[:8]) + ("..." if len(x.split())>8 else "")
            )

            # Taller figure to align with pie chart
            fig2, ax2 = plt.subplots(figsize=(6,7))
            bars = ax2.barh(
                df_sorted["ShortTitle"],
                df_sorted["Sentiment Score"],
                color=df_sorted["Sentiment Score"].apply(
                    lambda x: "#22c55e" if x>0 else "#ef4444" if x<0 else "#94a3b8"
                ),
                height=0.7  # thicker bars
            )

            # Font size and spacing
            ax2.set_yticks(range(len(df_sorted)))
            ax2.set_yticklabels(df_sorted["ShortTitle"], fontsize=14)
            ax2.set_xlabel("Sentiment Score", fontsize=14)
            ax2.set_ylabel("Headline (first 8 words)", fontsize=14)
            ax2.margins(y=0.15)
            ax2.invert_yaxis()  # largest score on top

            st.pyplot(fig2)

        # =========================
        # NEWS TABLE
        # =========================
        st.markdown("### 🗞️ News Headlines")
        st.dataframe(
            df[["Date","Title","Sentiment Score"]],
            use_container_width=True,
            height=700
        )
else:
    st.info("Enter a stock ticker to start analyzing sentiment.")
