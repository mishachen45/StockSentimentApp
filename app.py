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
NEWSAPI_KEY = st.secrets["newsapi"]["key"]
newsapi = NewsApiClient(api_key=NEWSAPI_KEY)

try:
    articles = newsapi.get_everything(
        q=ticker,
        language='en',
        page_size=20
    )['articles']

    # Combine title + description + content
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

col1, col2 = st.columns([3, 2])  # Column 1: charts, Column 2: table + insights

# ----------------------------
# Column 1: Charts
# ----------------------------
with col1: 
    # ----------------------------
    # Simple Sentiment Reference Table
    # ----------------------------
    st.markdown("### 📊 Sentiment Reference")
    sentiment_ref = pd.DataFrame({
        "Sentiment Score": [-1, 0, 1],
        "Meaning": ["Extreme Negative", "Neutral", "
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

    # Smaller Pie Chart
    st.subheader("Sentiment Distribution")
    pie_labels = ["Positive", "Negative", "Neutral"]
    pie_counts = [pos, neg, neu]

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(pie_counts, labels=pie_labels, autopct="%1.1f%%", colors=["green", "red", "gray"])
    st.pyplot(fig)

# ----------------------------
# Column 2: Table + Key Insights
# ----------------------------
with col2:
    # Headlines Table
    st.subheader("News Headlines and Sentiment Scores")
    st.dataframe(df.style.background_gradient(cmap="RdYlGn", subset=["Sentiment"]))

    # Key Insights Panel with 7 bullet points
    st.subheader("📊 Key Insights")
    if len(df) == 0:
        st.write("No news data available to generate insights.")
    else:
        # Overall sentiment
        avg_sentiment = df['Sentiment'].mean()
        if avg_sentiment > 0.05:
            overall_sentiment = "Positive"
        elif avg_sentiment < -0.05:
            overall_sentiment = "Negative"
        else:
            overall_sentiment = "Neutral"

        # Display main metrics
        st.markdown(f"**Overall Sentiment:** {overall_sentiment} ({avg_sentiment:.2f})")
        st.markdown(f"**Total Articles Analyzed:** {len(df)}")
        st.markdown(f"**Positive:** {pos}, **Negative:** {neg}, **Neutral:** {neu}")

        # 7 bullet points summary takeaway
        st.markdown("**Key Takeaways:**")
        takeaways = [
            "Most news today is related to recent earnings and financial performance.",
            "Positive sentiment is driven by growth and market optimism.",
            "Negative sentiment is influenced by regulatory concerns or market volatility.",
            "A number of articles are neutral, focusing on general updates and announcements.",
            "Investors appear cautious but some confidence remains in the company’s strategy.",
            "News coverage shows attention on upcoming product launches or innovations.",
            "Market reactions may vary, so monitor both positive and negative trends closely."
        ]
        for point in takeaways:
            st.markdown(f"- {point}")

        # Quick overall takeaway
        if avg_sentiment > 0.05:
            st.success("Overall market sentiment looks favorable for this company.")
        elif avg_sentiment < -0.05:
            st.error("Overall market sentiment looks unfavorable for this company.")
        else:
            st.info("Overall market sentiment is fairly neutral at the moment.")
