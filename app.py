import streamlit as st
import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt

# ----------------------------
# Page configuration
# ----------------------------
st.set_page_config(page_title="Stock News Sentiment", layout="wide")
st.title("🚀 Stock News Sentiment Analyzer")

st.info("Enter a ticker symbol below to fetch the latest news and sentiment analysis.")

# ----------------------------
# User input: ticker
# ----------------------------
ticker = st.text_input("Enter a company ticker (e.g., AAPL, TSLA):", "AAPL").upper()

# ----------------------------
# Initialize news variables
# ----------------------------
headlines = []
api_ready = False

# ----------------------------
# Attempt to load NewsAPI
# ----------------------------
try:
    from newsapi import NewsApiClient
    NEWSAPI_KEY = st.secrets["newsapi"]["key"]
    newsapi = NewsApiClient(api_key=NEWSAPI_KEY)
    api_ready = True
except KeyError:
    st.warning("⚠️ NewsAPI key not found in Secrets. Using placeholder headlines.")
except ImportError:
    st.warning("⚠️ NewsAPI library not installed. Using placeholder headlines.")

# ----------------------------
# Fetch news safely
# ----------------------------
if api_ready:
    try:
        articles = newsapi.get_everything(q=ticker, language='en', page_size=20)['articles']
        headlines = [a['title'] for a in articles if a['title'] is not None]
        if not headlines:
            st.warning("No news found for this ticker. Using placeholder headlines.")
            api_ready = False
    except Exception as e:
        st.warning(f"Could not fetch news: {e}")
        api_ready = False

# ----------------------------
# Use placeholder if API fails
# ----------------------------
if not api_ready:
    headlines = [
        f"{ticker} stock surges after earnings report",
        f"{ticker} faces regulatory investigation",
        f"{ticker} market performance stable today",
        f"No significant news for {ticker}"
    ]

# ----------------------------
# Sentiment analysis
# ----------------------------
sentiments = [TextBlob(h).sentiment.polarity for h in headlines]
df = pd.DataFrame({"Headline": headlines, "Sentiment": sentiments})

# ----------------------------
# Bar chart
# ----------------------------
st.subheader("📊 Sentiment Bar Chart")
st.bar_chart(df["Sentiment"])

# ----------------------------
# Pie chart
# ----------------------------
st.subheader("📈 Sentiment Distribution")
pos = sum(s > 0 for s in sentiments)
neg = sum(s < 0 for s in sentiments)
neu = sum(s == 0 for s in sentiments)

pie_labels = ["Positive", "Negative", "Neutral"]
pie_counts = [pos, neg, neu]

fig, ax = plt.subplots()
ax.pie(pie_counts, labels=pie_labels, autopct="%1.1f%%", colors=["green", "red", "gray"])
st.pyplot(fig)

# ----------------------------
# Headlines table
# ----------------------------
st.subheader("📰 News Headlines and Sentiment Scores")
st.dataframe(df)
