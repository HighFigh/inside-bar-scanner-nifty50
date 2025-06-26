import streamlit as st
from breakout_scanner import fetch_data, detect_inside_bar_breakouts
from nifty50_list import get_nifty50_symbols
import plotly.graph_objs as go

st.set_page_config(layout="wide")
st.title("📈 Inside Bar Breakout Scanner - Nifty 50")

symbols = get_nifty50_symbols()
selected_symbol = st.selectbox("Select a Stock from Nifty 50:", symbols)
interval = st.selectbox("Interval", ["15m", "1d"])
period = "5d" if interval == "15m" else "3mo"

df = fetch_data(selected_symbol, interval=interval, period=period)
df = detect_inside_bar_breakouts(df)

# Chart
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close"))

buys = df[df["Position"] == 1]
sells = df[df["Position"] == -1]

fig.add_trace(go.Scatter(x=buys.index, y=buys["Close"], mode="markers", name="Buy", marker=dict(color="green", size=10, symbol="triangle-up")))
fig.add_trace(go.Scatter(x=sells.index, y=sells["Close"], mode="markers", name="Sell", marker=dict(color="red", size=10, symbol="triangle-down")))

fig.update_layout(title=f"{selected_symbol} Inside Bar Breakouts", xaxis_title="Time", yaxis_title="Price")
st.plotly_chart(fig, use_container_width=True)

# Data Table
st.subheader("Breakout Signals")
st.dataframe(df[df["Position"] != 0][["Open", "High", "Low", "Close", "Position", "SL", "Target"]].sort_index(ascending=False))
