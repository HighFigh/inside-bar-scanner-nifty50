import yfinance as yf
import pandas as pd

def fetch_data(symbol, interval="15m", period="5d"):
    try:
        df = yf.download(symbol, interval=interval, period=period, progress=False)
        if df.empty:
            return None
        return df.dropna()
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def detect_inside_bar_breakouts(df):
    if df is None or len(df) < 3:
        return df

    # Initialize new columns
    df["InsideBar"] = False
    df["LongBreakout"] = False
    df["ShortBreakout"] = False
    df["Position"] = 0
    df["SL"] = None
    df["Target"] = None
    df["MotherHigh"] = None
    df["MotherLow"] = None
    df["InsideRange"] = None

    # Loop to check each inside bar condition safely
    for i in range(1, len(df)):
        prev_high = df.iloc[i - 1]["High"]
        prev_low = df.iloc[i - 1]["Low"]
        curr_high = df.iloc[i]["High"]
        curr_low = df.iloc[i]["Low"]

        # Inside Bar condition
        if curr_high < prev_high and curr_low > prev_low:
            df.at[i, "InsideBar"] = True

    for i in range(2, len(df)):
        if df.at[i - 1, "InsideBar"]:
            mother_high = df.at[i - 1, "High"]
            mother_low = df.at[i - 1, "Low"]
            inside_range = mother_high - mother_low
            close_price = df.at[i, "Close"]

            df.at[i, "MotherHigh"] = mother_high
            df.at[i, "MotherLow"] = mother_low
            df.at[i, "InsideRange"] = inside_range

            # Long Breakout
            if df.at[i, "High"] > mother_high:
                df.at[i, "LongBreakout"] = True
                df.at[i, "Position"] = 1
                df.at[i, "SL"] = mother_low
                df.at[i, "Target"] = close_price + 2 * inside_range

            # Short Breakout
            elif df.at[i, "Low"] < mother_low:
                df.at[i, "ShortBreakout"] = True
                df.at[i, "Position"] = -1
                df.at[i, "SL"] = mother_high
                df.at[i, "Target"] = close_price - 2 * inside_range

    return df
