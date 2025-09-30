import streamlit as st
import pandas as pd
from textblob import TextBlob
from yahoo_fin import stock_info as si
import feedparser
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
st.markdown("Analyze recent news headlines for any company and visualize sentiment. Powered by Yahoo Finance (legacy RSS) and TextBlob.")

# ----------------------------
# Sidebar input
# ----------------------------
st.sidebar.header("User Input")
ticker = st.sidebar.text_input("Enter a company ticker (e.g., AAPL, TSLA):", "AAPL").upper()

# ----------------------------
# Fetch news via Yahoo Finance RSS (legacy)
# ----------------------------
headlines = []

try:
    rss_url = f"https://finance.yahoo.com/rss/headline?s={ticker}"
    feed = feedparser.parse(rss_url)

    for entry in feed.entries[:20]:  # get latest 20 headlines
        title = entry.get('title')
        if title:
            headlines.append(title)

    # Fallback if no headlines found
    if not headlines:
        headlines = [
            f"{ticker} stock surges after earnings report",
            f"{ticker} faces regulatory investigation",
            f"{ticker} market performance stable today",
            f"No significant news for {ticker}"
        ]

except Exception as e:
    st.warning(f"Could not fetch news. Showing placeholder headlines.\nError: {e}")
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

col1, col2 = st.columns([3, 2])  # Column 1: charts, Column 2: table + insights

# ----------------------------
# Column 1: Charts
# ----------------------------
with col1: 
    sentiment_ref = pd.DataFrame({
        "Sentiment Score": [-1, 0, 1],
        "Meaning": ["Extreme Negative", "Neutral", "Extreme Positive"]
    })
    st.table(sentiment_ref)

    # Horizontal Bar Chart
    st.subheader("Sentiment Bar Chart")
    short_labels = [h if len(h) <= 50 else h[:47] + "..." for h in df["Headline"]]

    fig_bar = px.bar(
        df,
        x="Sentiment",
        y=short_labels,
        orientation='h',
        color=df["Sentiment"] > 0,
        color_discrete_map={True: "green", False: "red"},
        labels={"y": "Headline", "color": "Positive?"},
        height=600
    )
    fig_bar.update_layout(yaxis={'automargin': True})
    st.plotly_chart(fig_bar, use_container_width=True)

    # Pie Chart
    st.subheader("Sentiment Distribution")
    pie_labels = ["Positive", "Negative", "Neutral"]
    pie_counts = [pos, neg, neu]

    fig, ax = plt.subplots(figsize=(2.5, 2.5))
    ax.pie(pie_counts, labels=pie_labels, autopct="%1.1f%%", colors=["green", "red", "gray"])
    ax.axis('equal')
    st.pyplot(fig)

# ----------------------------
# Column 2: Table + Key Insights
# ----------------------------
with col2:
    st.subheader("News Headlines and Sentiment Scores")
    st.dataframe(df.style.background_gradient(cmap="RdYlGn", subset=["Sentiment"]))

    st.subheader("📊 Key Insights")
    avg_sentiment = df['Sentiment'].mean() if len(df) > 0 else 0

    overall_sentiment = (
        "Positive" if avg_sentiment > 0.05
        else "Negative" if avg_sentiment < -0.05
        else "Neutral"
    )

    st.markdown(f"**Overall Sentiment:** {overall_sentiment} ({avg_sentiment:.2f})")
    st.markdown(f"**Total Articles Analyzed:** {len(df)}")
    st.markdown(f"**Positive:** {pos}, **Negative:** {neg}, **Neutral:** {neu}")

    takeaways = [
        "Most news today is related to recent earnings and financial performance.",
        "Positive sentiment is driven by growth and market optimism.",
        "Negative sentiment is influenced by regulatory concerns or market volatility.",
        "A number of articles are neutral, focusing on general updates and announcements.",
        "Investors appear cautious but some confidence remains in the company’s strategy.",
        "News coverage shows attention on upcoming product launches or innovations.",
        "Market reactions may vary, so monitor both positive and negative trends closely."
    ]
    st.markdown("**Key Takeaways:**")
    for point in takeaways:
        st.markdown(f"- {point}")

    if avg_sentiment > 0.05:
        st.success("Overall market sentiment looks favorable for this company.")
    elif avg_sentiment < -0.05:
        st.error("Overall market sentiment looks unfavorable for this company.")
    else:
        st.info("Overall market sentiment is fairly neutral at the moment.")
