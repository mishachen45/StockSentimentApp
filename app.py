import streamlit as st
import pandas as pd
from textblob import TextBlob
from newsapi import NewsApiClient
import matplotlib.pyplot as plt
import plotly.express as px

# ----------------------------
# Page configuration
# ----------------------------
st.set_page_config(
    page_title="Stock News Sentiment",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📈 Stock News Sentiment Analyzer")
st.markdown("Analyze recent news headlines for any company and visualize sentiment. Powered by NewsAPI and TextBlob.")

# ----------------------------
# Sidebar input
# ----------------------------
st.sidebar.header("User Input")
ticker = st.sidebar.text_input("Enter a company ticker (e.g., AAPL, TSLA):", "AAPL")

# ----------------------------
# Fetch news from NewsAPI
# ----------------------------
# Make sure your NewsAPI key is in Streamlit Secrets
NEWSAPI_KEY = st.secrets["newsapi"]["key"]
newsapi = NewsApiClient(api_key=NEWSAPI_KEY)

try:
    articles = newsapi.get_everything(
        q=ticker,
        language='en',
        page_size=20  # max for free NewsAPI
    )['articles']

    # Combine title + description + content for sentiment analysis
    headlines = []
    for a in articles:
        text = a.get('title') or ''
        text += ' ' + (a.get('description') or '')
        text += ' ' + (a.get('content') or '')
        if text.strip():
            headlines.append(text)

except:
    st.warning("Could not fetch news. Showing placeholder headlines.")
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
# Summary metrics
# ----------------------------
pos = sum(s > 0 for s in sentiments)
neg = sum(s < 0 for s in sentiments)
neu = sum(s == 0 for s in sentiments)

col1, col2, col3 = st.columns(3)
col1.metric("Positive Headlines", pos)
col2.metric("Negative Headlines", neg)
col3.metric("Neutral Headlines", neu)

# ----------------------------
# Sentiment Bar Chart (colored)
# ----------------------------
st.subheader("Sentiment Bar Chart")
fig_bar = px.bar(
    df,
    x="Headline",
    y="Sentiment",
    color=df["Sentiment"] > 0,
    color_discrete_map={True: "green", False: "red"},
    labels={"color": "Positive?"},
    height=400
)
st.plotly_chart(fig_bar, use_container_width=True)

# ----------------------------
# Pie chart
# ----------------------------
st.subheader("Sentiment Distribution")
pie_labels = ["Positive", "Negative", "Neutral"]
pie_counts = [pos, neg, neu]

fig, ax = plt.subplots()
ax.pie(pie_counts, labels=pie_labels, autopct="%1.1f%%", colors=["green", "red", "gray"])
st.pyplot(fig)

# ----------------------------
# Headlines table
# ----------------------------
st.subheader("News Headlines and Sentiment Scores")
st.dataframe(df.style.background_gradient(cmap="RdYlGn", subset=["Sentiment"]))
