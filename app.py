import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from breakout_scanner import detect_inside_bar_breakouts
from telegram_bot import send_alert

st.set_page_config(page_title="Inside Bar Breakout Scanner - Nifty 50", layout="wide")
st.title("📈 Inside Bar Breakout Scanner - Nifty 50 (Daily Candle)")

nifty50_list = [
    "RELIANCE.NS", "SBIN.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "ITC.NS", "LT.NS", "HCLTECH.NS", "ASIANPAINT.NS"
]

symbol = st.selectbox("Select a Stock from Nifty 50:", nifty50_list)
days = st.slider("Number of days to fetch", 10, 120, 30)

if st.button("🔍 Scan Now"):
    with st.spinner(f"Fetching data for {symbol}..."):
        try:
            df = yf.download(symbol, period=f"{days}d", interval="1d")
            df = df[["Open", "High", "Low", "Close"]]
            df.dropna(inplace=True)
            df = detect_inside_bar_breakouts(df)

            st.success("Scan complete.")
            st.dataframe(df.tail(10))

            # Detect last breakout
            long_breakouts = df[df["LongBreakout"] == True]
            short_breakouts = df[df["ShortBreakout"] == True]

            if not long_breakouts.empty:
                last = long_breakouts.iloc[-1]
                msg = f"📈 <b>Long Breakout</b> detected on <b>{symbol}</b> at {last.name.strftime('%Y-%m-%d')} - Close: {last['Close']:.2f}"
                send_alert(msg)

            if not short_breakouts.empty:
                last = short_breakouts.iloc[-1]
                msg = f"📉 <b>Short Breakout</b> detected on <b>{symbol}</b> at {last.name.strftime('%Y-%m-%d')} - Close: {last['Close']:.2f}"
                send_alert(msg)

        except Exception as e:
            st.error("⚠️ Failed to fetch or process data.")
            st.exception(e)
