from datetime import date, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

# CONSTANTS
END = date.today()
START = END - timedelta(365)

# Data handling
def get_stock_data(ticker, start, end):
    try:
        data = yf.download(ticker, start, end, auto_adjust=False)
        if data.empty:
            return None, f"No data found for {ticker}"
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data, f"Successfully loaded data for {ticker}"
    except Exception as e:
        return None, f"Error {e}"

# Streamlit UI
st.set_page_config(page_title="Stock Tracker", layout="wide")
st.title("📈 Stock Price Tracker")

with st.sidebar:
    st.header("Settings")
    ticker = st.text_input("Ticker symbol:", "AAPL").upper()
    custom_start = st.date_input("Start Date:", value=START)
    ma_window = st.slider("Moving Average Window:", 5, 200, 20)

if ticker:
    data, message = get_stock_data(ticker, custom_start, END)
    st.info(message)
    
    if data is not None:
        # Calculate moving average
        data['MA'] = data['Close'].rolling(window=ma_window).mean()
        
        latest = data['Close'].iloc[-1]
        start_price = data['Close'].iloc[0]
        change = ((latest - start_price) / start_price) * 100
        
        tab1, tab2, tab3 = st.tabs(["Chart", "Statistics", "Raw Data"])
        
        with tab1:
            st.subheader("Price Trend with Moving Average")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Current Price", f"${latest:.2f}")
            with col2:
                st.metric("Cumulative Change", f"{change:.2f}%")
            with col3:
                st.metric("Trading Days", len(data))
            
            fig = px.line(data, y=['Close', 'MA'], title=f"{ticker} Stock Price & {ma_window}-Day MA")
            fig.update_layout(hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.subheader("Statistics (% Change from Day 1)")
            
            # Calculate % change relative to first day
            first_price = data['Close'].iloc[0]
            pct_change_from_start = ((data['Close'] / first_price) - 1) * 100
            stats = pct_change_from_start.describe()
            
            # Calculate volatility (daily returns standard deviation)
            daily_returns = data['Close'].pct_change().dropna()
            volatility = daily_returns.std() * 100  # Convert to percentage
            
            col = st.columns(1)[0]
            with col:
                st.metric("Count", f"{int(stats['count'])}")
                st.metric("Mean", f"{stats['mean']:.2f}%")
                st.metric("Std Dev", f"{stats['std']:.2f}%")
                st.metric("Min", f"{stats['min']:.2f}%")
                st.metric("25%", f"{stats['25%']:.2f}%")
                st.metric("Median", f"{stats['50%']:.2f}%")
                st.metric("75%", f"{stats['75%']:.2f}%")
                st.metric("Max", f"{stats['max']:.2f}%")
                st.metric("Volatility", f"{volatility:.2f}%")
        
        with tab3:
            st.subheader("Raw Data")
            st.dataframe(data[['Open', 'High', 'Low', 'Close']],
                        use_container_width=True)
