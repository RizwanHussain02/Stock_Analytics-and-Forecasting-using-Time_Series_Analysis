import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import datetime
from pages.utils.plotly_figure import plotly_table, candlestick, RSI, MACD, line_chart, moving_average, close_chart

# setting page configuration
st.set_page_config(
    page_title = "Stock Analysis",
    page_icon = "page_with_curl",
    layout = "wide"
)

st.title("Stock Analysis")

col1, col2, col3 = st.columns(3)

today = datetime.date.today()

with col1:
    ticker_symbol = st.text_input("Enter Stock Ticker", "TSLA")
with col2:
    start_date = st.date_input("Choose Start Date", datetime.date(today.year - 1, today.month, today.day))
with col3:
    end_date = st.date_input("Choose End Date", datetime.date(today.year, today.month, today.day))

tick = (ticker_symbol or "").strip()
st.subheader(tick if tick else "(no ticker)")

if not tick:
    st.warning("Please enter a stock ticker symbol.")
    st.stop()

stock = yf.Ticker(tick)

def _safe_info(ticker_obj: yf.Ticker) -> dict:
    try:
        # yfinance may raise here (network/API/rate-limit) or return None
        info = getattr(ticker_obj, "info", None)
        return info or {}
    except Exception:
        return {}


def _safe_history(symbol: str, period: str = "max") -> pd.DataFrame:
    # Prefer yf.download: generally returns empty DF instead of crashing in scraper.
    try:
        df = yf.download(
            symbol,
            period=period,
            interval="1d",
            auto_adjust=False,
            actions=False,
            progress=False,
            threads=False,
        )
        if isinstance(df, pd.DataFrame) and not df.empty:
            return df
    except Exception:
        pass

    # Some environments intermittently return empty for period='max'.
    # Retry using an explicit start date.
    if str(period).lower() == "max":
        for start in ("1900-01-01", "1970-01-01", "2000-01-01"):
            try:
                df = yf.download(
                    symbol,
                    start=start,
                    interval="1d",
                    auto_adjust=False,
                    actions=False,
                    progress=False,
                    threads=False,
                )
                if isinstance(df, pd.DataFrame) and not df.empty:
                    return df
            except Exception:
                continue

        # Last resort: try a smaller period.
        try:
            df = yf.download(
                symbol,
                period="10y",
                interval="1d",
                auto_adjust=False,
                actions=False,
                progress=False,
                threads=False,
            )
            if isinstance(df, pd.DataFrame) and not df.empty:
                return df
        except Exception:
            pass

    # Fallback to Ticker.history (can still fail on Yahoo payload issues)
    try:
        df = yf.Ticker(symbol).history(period=period)
        if isinstance(df, pd.DataFrame) and not df.empty:
            return df
    except Exception:
        pass

    return pd.DataFrame()


def _normalize_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    # yfinance can return MultiIndex columns even for a single ticker.
    # For this app we expect simple columns: Open/High/Low/Close/Volume.
    if not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame()

    if isinstance(df.columns, pd.MultiIndex):
        # Common case: level0 = [Open, High, Low, Close, Volume], level1 = [<ticker>]
        # If only one ticker present, drop the ticker level.
        if df.columns.nlevels >= 2:
            level_1_vals = df.columns.get_level_values(-1)
            if len(set(map(str, level_1_vals))) == 1:
                df = df.copy()
                df.columns = df.columns.get_level_values(0)
            else:
                # Multiple tickers: keep only the selected symbol if present.
                try:
                    df = df.xs(tick, axis=1, level=-1, drop_level=True)
                except Exception:
                    return pd.DataFrame()

    # Some yfinance outputs use lowercase or include 'Adj Close'; standardize minimally.
    rename_map = {c: str(c).title() for c in df.columns}
    df = df.rename(columns=rename_map)
    return df


def _get_close_scalar(df: pd.DataFrame, idx: int) -> float | None:
    if not isinstance(df, pd.DataFrame) or df.empty:
        return None
    if "Close" not in df.columns:
        return None
    val = df["Close"].iloc[idx]
    # If it's still a Series (unexpected), take first non-null element.
    if isinstance(val, pd.Series):
        val = val.dropna().iloc[0] if not val.dropna().empty else None
    try:
        return float(val) if val is not None else None
    except Exception:
        return None

info = _safe_info(stock)
summary = info.get("longBusinessSummary")
if summary:
    st.write(summary)

if info:
    if info.get("sector") is not None:
        st.write("**Sector:**", info.get("sector"))
    if info.get("fullTimeEmployees") is not None:
        st.write("**Full Time Employees:**", info.get("fullTimeEmployees"))
    if info.get("website") is not None:
        st.write("**Website:**", info.get("website"))
else:
    st.info("Unable to load company profile (Yahoo Finance may be rate-limiting or the ticker is invalid).")

col1, col2 = st.columns(2)

with col1:
    df = pd.DataFrame(index = ['Market Cap', 'Beta', 'EPS', 'PE Ration', 'avg Volume'])
    df[''] = [
        info.get('marketCap'),
        info.get('beta'),
        info.get('trailingEps'),
        info.get('trailingPE'),
        info.get('averageVolume'),
    ]
    fig_df = plotly_table(df)
    st.plotly_chart(fig_df, use_container_width=True)

with col2:
    df = pd.DataFrame(index = ['Quick Ratio','Revenue per Share','Profit Margin','Return on Equity','Debt to Equity'])
    df[''] = [
        info.get('quickRatio'),
        info.get('revenuePerShare'),
        info.get('profitMargins'),
        info.get('returnOnEquity'),
        info.get('debtToEquity'),
    ]
    fig_df = plotly_table(df)
    st.plotly_chart(fig_df, use_container_width=True)

data = yf.download(
    tick,
    start=start_date,
    end=end_date,
    auto_adjust=False,
    actions=False,
    progress=False,
    threads=False,
)

data = _normalize_ohlc(data)

if not isinstance(data, pd.DataFrame) or data.empty:
    st.error("No price data returned for the selected date range. Check the ticker symbol and try again.")
    st.stop()

col1, col2, col3 = st.columns(3)
if len(data) >= 2:
    last_close = _get_close_scalar(data, -1)
    prev_close = _get_close_scalar(data, -2)
    if last_close is not None and prev_close is not None:
        daily_change = last_close - prev_close
        col1.metric("Daily Change", str(round(last_close, 2)), str(round(daily_change, 2)))
    else:
        col1.metric("Daily Change", "N/A", "N/A")
else:
    col1.metric("Daily Change", "N/A", "N/A")

last_10_days = data.tail(10).sort_index(ascending=False).round(3)
fig_df = plotly_table(last_10_days)

st.write("##### Historical Data (Last 10 Days)")
st.plotly_chart(fig_df, use_container_width=True)

col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12 = st.columns([1,1,1,1,1,1,1,1,1,1,1,1])
num_period = ''
with col1:
    if st.button("5D"):
        num_period = '5d'
with col2:
    if st.button("1M"):
        num_period = '1mo'
with col3:
    if st.button("3M"):
        num_period = '3mo'
with col4:
    if st.button("6M"):
        num_period = '6mo'
with col5:
    if st.button("YTD"):
        num_period = 'ytd'
with col6:
    if st.button("1Y"):
        num_period = '1y'
with col7:
    if st.button("MAX"):
        num_period = 'max'

col1, col2, col3 = st.columns([1,1,4])
with col1:
    chart_type = st.selectbox('',('Candle','Line'))
with col2:
    if chart_type == 'Candle':
        indicators = st.selectbox('',('RSI', 'MACD'))
    else:
        indicators = st.selectbox('',('RSI', 'Moving Average', 'MACD'))

data1 = _normalize_ohlc(_safe_history(tick, period='max'))
new_df1 = data1

if data1.empty:
    st.warning(
        "Unable to load full historical history (MAX) from Yahoo Finance right now. "
        "Showing charts using the selected date range instead."
    )
    data1 = data.copy()
    new_df1 = data1
if num_period == '':

    if chart_type == 'Candle' and indicators == 'RSI':
       st.plotly_chart(candlestick(data1, '1y'), use_container_width=True)
       st.plotly_chart(RSI(data1, '1y'), use_container_width=True)
    
    if chart_type == 'Candle' and indicators == 'MACD':
       st.plotly_chart(candlestick(data1, '1y'), use_container_width=True)
       st.plotly_chart(MACD(data1, '1y'), use_container_width=True)

    if chart_type == 'Line' and indicators == 'RSI':
       st.plotly_chart(line_chart(data1, '1y'), use_container_width=True)
       st.plotly_chart(RSI(data1, '1y'), use_container_width=True)
    
    if chart_type == 'Line' and indicators == 'Moving Average':
       st.plotly_chart(line_chart(data1, '1y'), use_container_width=True)
       st.plotly_chart(moving_average(data1, '1y'), use_container_width=True)
    
    if chart_type == 'Line' and indicators == 'MACD':
       st.plotly_chart(line_chart(data1, '1y'), use_container_width=True)
       st.plotly_chart(MACD(data1, '1y'), use_container_width=True)

else:

    if chart_type == 'Candle' and indicators == 'RSI':
       st.plotly_chart(candlestick(new_df1, num_period), use_container_width=True)
       st.plotly_chart(RSI(new_df1, num_period), use_container_width=True)

    if chart_type == 'Candle' and indicators == 'MACD':
       st.plotly_chart(candlestick(new_df1, num_period), use_container_width=True)
       st.plotly_chart(MACD(new_df1, num_period), use_container_width=True)
    
    if chart_type == 'Line' and indicators == 'RSI':
       st.plotly_chart(close_chart(new_df1, num_period), use_container_width=True)
       st.plotly_chart(RSI(new_df1, num_period), use_container_width=True)
    
    if chart_type == 'Line' and indicators == 'Moving Average':
       st.plotly_chart(line_chart(new_df1, num_period), use_container_width=True)
       st.plotly_chart(moving_average(new_df1, num_period), use_container_width=True)
    
    if chart_type == 'Line' and indicators == 'MACD':
       st.plotly_chart(close_chart(new_df1, num_period), use_container_width=True)
       st.plotly_chart(MACD(new_df1, num_period), use_container_width=True)