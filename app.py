import streamlit as st
import pandas as pd
from textblob import TextBlob
import feedparser
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------
# Page configuration
# ----------------------------
st.set_page_config(
    page_title="Stock News Dashboard",
    layout="wide"
)

st.title("📊 Stock News Sentiment Dashboard")
st.markdown(
    "Analyze recent news headlines and summaries for any company. "
    "Powered by Yahoo Finance RSS + TextBlob."
)

# ----------------------------
# Sidebar input
# ----------------------------
st.sidebar.header("User Input")
ticker = st.sidebar.text_input("Enter company ticker:", "AAPL").upper()
num_articles = st.sidebar.slider("Number of news articles:", 5, 30, 20)

# ----------------------------
# Fetch RSS feed
# ----------------------------
headlines, links = [], []
try:
    feed = feedparser.parse(f"https://finance.yahoo.com/rss/headline?s={ticker}")
    for entry in feed.entries[:num_articles]:
        title = entry.get('title', '')
        summary = entry.get('summary', '')
        link = entry.get('link', '#')
        text = f"{title} {summary}".strip()
        if text:
            headlines.append(text)
            links.append(link)
    if not headlines:
        headlines = ["No news available"]
        links = ["#"]
except Exception as e:
    st.warning(f"Could not fetch news: {e}")
    headlines = ["No news available"]
    links = ["#"]

# ----------------------------
# Sentiment analysis
# ----------------------------
sentiments = [TextBlob(h).sentiment.polarity for h in headlines]
df = pd.DataFrame({"Headline": headlines, "Sentiment": sentiments, "Link": links})

pos = sum(s>0 for s in sentiments)
neg = sum(s<0 for s in sentiments)
neu = sum(s==0 for s in sentiments)
avg_sent = df['Sentiment'].mean() if len(df)>0 else 0
overall_sent = "Positive" if avg_sent>0.05 else "Negative" if avg_sent<-0.05 else "Neutral"

# ----------------------------
# Dashboard Layout
# ----------------------------
# Top metrics
with st.container():
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Articles", len(df))
    col2.metric("Positive", pos)
    col3.metric("Negative", neg)
    col4.metric("Neutral", neu)

sentiment_color = "green" if overall_sent=="Positive" else "red" if overall_sent=="Negative" else "gray"
st.markdown(f"**Overall Sentiment:** <span style='color:{sentiment_color}'>{overall_sent} ({avg_sent:.2f})</span>", unsafe_allow_html=True)

st.markdown("---")

# Charts and table side by side
with st.container():
    chart_col, news_col = st.columns([2, 3])

    # Left column: Charts
    with chart_col:
        st.subheader("Sentiment Distribution")
        fig_pie = go.Figure(data=[go.Pie(
            labels=["Positive","Negative","Neutral"],
            values=[pos, neg, neu],
            marker_colors=["green","red","gray"],
            hoverinfo="label+percent+value",
            textinfo="label+percent"
        )])
        fig_pie.update_layout(height=500, width=500, margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig_pie, use_container_width=True)

        st.subheader("Headlines Sentiment")
        short_labels = [h if len(h)<=60 else h[:57]+"..." for h in df["Headline"]]
        fig_bar = px.bar(
            df,
            x="Sentiment",
            y=short_labels,
            orientation='h',
            color=df["Sentiment"].apply(lambda x: "Positive" if x>0 else "Negative" if x<0 else "Neutral"),
            color_discrete_map={"Positive":"green","Negative":"red","Neutral":"gray"},
            labels={"y":"Headline"},
            hover_data={"Headline":True,"Sentiment":True}
        )
        fig_bar.update_layout(yaxis={'automargin': True}, height=500)
        st.plotly_chart(fig_bar, use_container_width=True)

    # Right column: News table
    with news_col:
        st.subheader("News Headlines")
        df_display = df.copy()
        df_display["Headline"] = df_display.apply(lambda row: f"[{row['Headline']}]({row['Link']})", axis=1)
        st.dataframe(
            df_display.style.format({"Sentiment":"{:.2f}"}).background_gradient(cmap="RdYlGn", subset=["Sentiment"]),
            height=800
        )

# Key takeaways
st.markdown("---")
st.subheader("Key Takeaways")
takeaways = [
    "Most news today relates to earnings and financial performance.",
    "Positive sentiment driven by growth and optimism.",
    "Negative sentiment influenced by regulatory concerns or market volatility.",
    "Several articles are neutral, giving general updates.",
    "Investors appear cautious but confident in company strategy.",
    "Attention on upcoming products or innovations.",
    "Market reactions vary; monitor trends closely."
]
for t in takeaways:
    st.markdown(f"- {t}")
