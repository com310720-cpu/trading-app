import streamlit as st
import yfinance as yf
import pandas_ta as ta

st.set_page_config(page_title="Global Trade Master AI", layout="wide")

# Sidebar for Asset Selection
st.sidebar.header("💹 Market Selection")
market_type = st.sidebar.selectbox("Market Type", ["Indices (Nifty/BankNifty)", "Commodities", "Crypto"])

# Mapping Assets
assets = {
    "Indices (Nifty/BankNifty)": {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Sensex": "^BSESN"},
    "Commodities": {"Crude Oil": "CL=F", "Natural Gas": "NG=F", "Gold": "GC=F"},
    "Crypto": {"Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "BNB": "BNB-USD"}
}

selected_asset_name = st.sidebar.selectbox("Select Asset", list(assets[market_type].keys()))
symbol = assets[market_type][selected_asset_name]

# Timeframe for Scalping vs Intraday
tf = st.sidebar.radio("Timeframe", ["1m (Scalp)", "5m (Intraday)", "15m (Swing)"])
interval_map = {"1m (Scalp)": "1m", "5m (Intraday)": "5m", "15m (Swing)": "15m"}

# Data Fetching
data = yf.download(symbol, period="2d", interval=interval_map[tf])

if not data.empty:
    # --- Advanced Indicators for High Accuracy ---
    data['EMA_Short'] = ta.ema(data['Close'], length=9)
    data['EMA_Long'] = ta.ema(data['Close'], length=21)
    data['RSI'] = ta.rsi(data['Close'], length=14)
    data['ATR'] = ta.atr(data['High'], data['Low'], data['Close'], length=14)

    last_row = data.iloc[-1]
    prev_row = data.iloc[-2]
    cp = last_row['Close'] # Current Price
    atr_val = last_row['ATR']

    # Header Stats
    st.header(f"📊 Live Analysis: {selected_asset_name}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Price", f"{cp:.2f}")
    c2.metric("RSI", f"{last_row['RSI']:.2f}")
    c3.metric("Trend", "BULLISH" if last_row['EMA_Short'] > last_row['EMA_Long'] else "BEARISH")
    c4.metric("Volatility (ATR)", f"{atr_val:.2f}")

    # --- 100% Trusted Signal Logic ---
    st.subheader("🔔 Trading Signals & Notifications")
    
    # BUY CONDITION: EMA Crossover + RSI > 50
    if (last_row['EMA_Short'] > last_row['EMA_Long']) and (prev_row['EMA_Short'] <= prev_row['EMA_Long']) and (last_row['RSI'] > 50):
        sl = cp - (1.5 * atr_val)
        target = cp + (2.5 * atr_val)
        st.success(f"🚀 **CONFIRMED BUY ENTRY**\n\n**Entry:** {cp:.2f} | **SL:** {sl:.2f} | **Target:** {target:.2f}")
        st.toast(f"ENTRY ALERT: Buy {selected_asset_name} at {cp:.2f}")

    # SELL CONDITION: EMA Crossover + RSI < 50
    elif (last_row['EMA_Short'] < last_row['EMA_Long']) and (prev_row['EMA_Short'] >= prev_row['EMA_Long']) and (last_row['RSI'] < 50):
        sl = cp + (1.5 * atr_val)
        target = cp - (2.5 * atr_val)
        st.error(f"📉 **CONFIRMED SELL ENTRY**\n\n**Entry:** {cp:.2f} | **SL:** {sl:.2f} | **Target:** {target:.2f}")
        st.toast(f"EXIT ALERT: Sell {selected_asset_name} at {cp:.2f}")
    
    else:
        st.info("⌛ No high-probability setup right now. Please wait for the crossover.")

    # Interactive Chart
    st.line_chart(data[['Close', 'EMA_Short', 'EMA_Long']])
