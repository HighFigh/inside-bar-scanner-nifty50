import yfinance as yf
import pandas as pd

def fetch_data(symbol, interval="15m", period="5d"):
    try:
        df = yf.download(symbol, interval=interval, period=period, progress=False)
        if df.empty:
            return None
        df.dropna(inplace=True)

        # Convert UTC to IST
        df.index = df.index.tz_localize("UTC").tz_convert("Asia/Kolkata")

        return df
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None


def detect_inside_bar_breakouts(df):
    if df is None or len(df) < 3:
        return df

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
        prev_high = float(df["High"].iloc[i - 1])
        prev_low = float(df["Low"].iloc[i - 1])
        curr_high = float(df["High"].iloc[i])
        curr_low = float(df["Low"].iloc[i])

        if curr_high < prev_high and curr_low > prev_low:
            df.loc[df.index[i], "InsideBar"] = True

    for i in range(2, len(df)):
        inside_bar = df["InsideBar"].iloc[i - 1]
        if inside_bar:
            mother_high = float(df["High"].iloc[i - 1])
            mother_low = float(df["Low"].iloc[i - 1])
            close = float(df["Close"].iloc[i])
            high = float(df["High"].iloc[i])
            low = float(df["Low"].iloc[i])
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
