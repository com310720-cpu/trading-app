import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Pro-Trader AI", layout="wide")
st.title("🎯 Global Trade Master (No-Error Version)")

# Sidebar
symbol = st.sidebar.text_input("Enter Symbol (e.g. ^NSEI, BTC-USD, CL=F)", "^NSEI")
tf = st.sidebar.selectbox("Timeframe", ["1m", "5m", "15m"])

# Data Fetch
data = yf.download(symbol, period="2d", interval=tf)

if not data.empty:
    # Manual Technical Analysis (No extra library needed)
    data['EMA_9'] = data['Close'].ewm(span=9, adjust=False).mean()
    data['EMA_21'] = data['Close'].ewm(span=21, adjust=False).mean()
    
    # RSI Calculation
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))

    last = data.iloc[-1]
    prev = data.iloc[-2]

    # Display Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Price", f"{last['Close']:.2f}")
    c2.metric("RSI", f"{last['RSI']:.2f}")
    c3.metric("Trend", "Bullish" if last['EMA_9'] > last['EMA_21'] else "Bearish")

    # Signal Logic
    st.divider()
    if (last['EMA_9'] > last['EMA_21']) and (prev['EMA_9'] <= prev['EMA_21']):
        st.success(f"🚀 BUY ALERT: Entry at {last['Close']:.2f} | SL: {last['Close']*0.995:.2f}")
        st.toast("BUY ENTRY!")
    elif (last['EMA_9'] < last['EMA_21']) and (prev['EMA_9'] >= prev['EMA_21']):
        st.error(f"📉 SELL ALERT: Entry at {last['Close']:.2f} | SL: {last['Close']*1.005:.2f}")
        st.toast("SELL EXIT!")
    else:
        st.info("⌛ Waiting for Crossover...")

    st.line_chart(data[['Close', 'EMA_9', 'EMA_21']])
else:
    st.warning("Data fetch nahi ho raha. Check symbol.")
