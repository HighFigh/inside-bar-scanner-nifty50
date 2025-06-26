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

    # Identify Inside Bars
    for i in range(1, len(df)):
        prev_high = df.iloc[i - 1]["High"]
        prev_low = df.iloc[i - 1]["Low"]
        curr_high = df.iloc[i]["High"]
        curr_low = df.iloc[i]["Low"]

        if curr_high < prev_high and curr_low > prev_low:
            df.iloc[i, df.columns.get_loc("InsideBar")] = True

    # Check for breakout after inside bar
    for i in range(2, len(df)):
        if df.iloc[i - 1]["InsideBar"]:
            mother_high = df.iloc[i - 1]["High"]
            mother_low = df.iloc[i - 1]["Low"]
            inside_range = mother_high - mother_low
            close_price = df.iloc[i]["Close"]

            df.iloc[i, df.columns.get_loc("MotherHigh")] = mother_high
            df.iloc[i, df.columns.get_loc("MotherLow")] = mother_low
            df.iloc[i, df.columns.get_loc("InsideRange")] = inside_range

            if df.iloc[i]["High"] > mother_high:
                df.iloc[i, df.columns.get_loc("LongBreakout")] = True
                df.iloc[i, df.columns.get_loc("Position")] = 1
                df.iloc[i, df.columns.get_loc("SL")] = mother_low
                df.iloc[i, df.columns.get_loc("Target")] = close_price + 2 * inside_range

            elif df.iloc[i]["Low"] < mother_low:
                df.iloc[i, df.columns.get_loc("ShortBreakout")] = True
                df.iloc[i, df.columns.get_loc("Position")] = -1
                df.iloc[i, df.columns.get_loc("SL")] = mother_high
                df.iloc[i, df.columns.get_loc("Target")] = close_price - 2 * inside_range

    return df
