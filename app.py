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

col1, col2, col3 = st.columns(3)
col1.metric("Positive Headlines", pos)
col2.metric("Negative Headlines", neg)
col3.metric("Neutral Headlines", neu)

# ----------------------------
# Layout: Charts + Table + Insights
# ----------------------------
main_col, table_col = st.columns([3, 2])  # 3:2 ratio

with main_col:
    # ----------------------------
    # Horizontal Bar Chart
    # ----------------------------
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

    # ----------------------------
    # Smaller Pie Chart
    # ----------------------------
    st.subheader("Sentiment Distribution")
    pie_labels = ["Positive", "Negative", "Neutral"]
    pie_counts = [pos, neg, neu]

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(pie_counts, labels=pie_labels, autopct="%1.1f%%", colors=["green", "red", "gray"])
    st.pyplot(fig)

    # ----------------------------
    # Key Insights Panel
    # ----------------------------
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

        # Most positive / negative headlines
        most_pos_idx = df['Sentiment'].idxmax()
        most_neg_idx = df['Sentiment'].idxmin()

        # Display insights
        st.markdown(f"**Overall Sentiment:** {overall_sentiment} ({avg_sentiment:.2f})")
        st.markdown(f"**Total Articles Analyzed:** {len(df)}")
        st.markdown(f"**Positive:** {pos}, **Negative:** {neg}, **Neutral:** {neu}")
        st.markdown(f"**Most Positive Headline:** {df['Headline'][most_pos_idx]}")
        st.markdown(f"**Most Negative Headline:** {df['Headline'][most_neg_idx]}")

        # Quick takeaway
        if avg_sentiment > 0.05:
            st.success("Market sentiment looks favorable for this company.")
        elif avg_sentiment < -0.05:
            st.error("Market sentiment looks unfavorable for this company.")
        else:
            st.info("Market sentiment is fairly neutral at the moment.")

with table_col:
    # ----------------------------
    # Headlines Table
    # ----------------------------
    st.subheader("News Headlines and Sentiment Scores")
    st.dataframe(df.style.background_gradient(cmap="RdYlGn", subset=["Sentiment"]))
