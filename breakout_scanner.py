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

    # Initialize columns
    df["InsideBar"] = False
    df["LongBreakout"] = False
    df["ShortBreakout"] = False
    df["Position"] = 0
    df["SL"] = None
    df["Target"] = None
    df["MotherHigh"] = None
    df["MotherLow"] = None
    df["InsideRange"] = None

    for i in range(1, len(df)):
        prev_high = float(df.at[df.index[i - 1], "High"])
        prev_low = float(df.at[df.index[i - 1], "Low"])
        curr_high = float(df.at[df.index[i], "High"])
        curr_low = float(df.at[df.index[i], "Low"])

        if curr_high < prev_high and curr_low > prev_low:
            df.at[df.index[i], "InsideBar"] = True

    for i in range(2, len(df)):
        if df.at[df.index[i - 1], "InsideBar"]:  # ✅ FIXED HERE
            mother_high = float(df.at[df.index[i - 1], "High"])
            mother_low = float(df.at[df.index[i - 1], "Low"])
            close = float(df.at[df.index[i], "Close"])
            high = float(df.at[df.index[i], "High"])
            low = float(df.at[df.index[i], "Low"])
            inside_range = mother_high - mother_low

            df.at[df.index[i], "MotherHigh"] = mother_high
            df.at[df.index[i], "MotherLow"] = mother_low
            df.at[df.index[i], "InsideRange"] = inside_range

            if high > mother_high:
                df.at[df.index[i], "LongBreakout"] = True
                df.at[df.index[i], "Position"] = 1
                df.at[df.index[i], "SL"] = mother_low
                df.at[df.index[i], "Target"] = close + 2 * inside_range
            elif low < mother_low:
                df.at[df.index[i], "ShortBreakout"] = True
                df.at[df.index[i], "Position"] = -1
                df.at[df.index[i], "SL"] = mother_high
                df.at[df.index[i], "Target"] = close - 2 * inside_range

    return df
