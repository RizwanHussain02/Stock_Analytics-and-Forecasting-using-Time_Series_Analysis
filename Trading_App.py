import streamlit as st

# ------------------ Page Configuration ------------------
st.set_page_config(
    page_title="Stock Time Series Analytics",
    page_icon="📈",
    layout="wide"
)

# ------------------ HERO SECTION ------------------
st.markdown("""
# 📈 Stock Time Series Analytics Platform  
### Analyze historical trends • Forecast future prices • Make data-driven decisions
""")

st.markdown(
    """
This interactive trading analytics application is designed to help users **analyze stock price behavior over time**
and **forecast future prices using time series models**.  
It focuses on **data analysis, visualization, and forecasting**, not automated trading.
"""
)
    
st.image("app.jpg", use_container_width=True)

# ------------------ QUICK OVERVIEW CARDS ------------------
st.markdown("### 🚀 What This Platform Offers")

col1, col2, col3 = st.columns(3)

with col1:
    st.info(
        "📊 **Stock Analysis**\n\n"
        "Explore historical price movements, trends, volatility, "
        "and technical indicators using time-indexed stock data."
    )

with col2:
    st.success(
        "🔮 **Stock Forecasting**\n\n"
        "Predict future closing prices using statistical "
        "time series forecasting models trained on historical data."
    )

with col3:
    st.warning(
        "📈 **Time Series Insights**\n\n"
        "Understand how stock prices evolve over time through "
        "rolling averages, differencing, and trend analysis."
    )

# ------------------ KEY FEATURES ------------------
st.markdown("---")
st.markdown("## 🔍 Key Features")

st.markdown("""
- 📅 **Time Series–Based Stock Data Analysis**  
- 📈 **Trend & Volatility Visualization** using rolling statistics  
- 🔮 **30-Day Stock Price Forecasting** with ARIMA-based models  
- 📊 **Interactive Charts & Indicators** (RSI, MACD, Moving Averages)  
- 🧠 **Analytics-Focused Insights** for informed decision-making  
""")

# ------------------ PLATFORM CAPABILITIES ------------------
st.markdown("---")
st.markdown("## Platform Capabilities")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Data Frequency", "Daily")
col2.metric("Forecast Horizon", "30 Days")
col3.metric("Model Type", "Time Series (ARIMA)")
col4.metric("Interface", "Interactive Dashboard")

# ------------------ HOW TO USE ------------------
st.markdown("---")
st.markdown("## 🧭 How to Use This App")

st.markdown("""
1️⃣ Open **Stock Analysis** from the sidebar to explore historical price trends  
2️⃣ View technical indicators and price movements over time  
3️⃣ Navigate to **Stock Prediction** to forecast future closing prices  
4️⃣ Use insights from both sections to support data-driven investment analysis  
""")

# ------------------ FOOTER ------------------
st.markdown("---")
st.caption(
    "This project demonstrates **Time Series Analysis and Forecasting** "
    "using Python and Streamlit."
)