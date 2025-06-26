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
        prev_high = float(df.iloc[i - 1]["High"])
        prev_low = float(df.iloc[i - 1]["Low"])
        curr_high = float(df.iloc[i]["High"])
        curr_low = float(df.iloc[i]["Low"])

        if curr_high < prev_high and curr_low > prev_low:
            df.loc[df.index[i], "InsideBar"] = True

    for i in range(2, len(df)):
        if df.iloc[i - 1]["InsideBar"] == True:
            mother_high = float(df.iloc[i - 1]["High"])
            mother_low = float(df.iloc[i - 1]["Low"])
            close = float(df.iloc[i]["Close"])
            high = float(df.iloc[i]["High"])
            low = float(df.iloc[i]["Low"])
            inside_range = mother_high - mother_low

            df.loc[df.index[i], "MotherHigh"] = mother_high
            df.loc[df.index[i], "MotherLow"] = mother_low
            df.loc[df.index[i], "InsideRange"] = inside_range

            if high > mother_high:
                df.loc[df.index[i], "LongBreakout"] = True
                df.loc[df.index[i], "Position"] = 1
                df.loc[df.index[i], "SL"] = mother_low
                df.loc[df.index[i], "Target"] = close + 2 * inside_range
            elif low < mother_low:
                df.loc[df.index[i], "ShortBreakout"] = True
                df.loc[df.index[i], "Position"] = -1
                df.loc[df.index[i], "SL"] = mother_high
                df.loc[df.index[i], "Target"] = close - 2 * inside_range

    return df
