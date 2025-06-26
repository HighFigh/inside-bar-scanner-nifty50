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

    # Calculate Inside Bar condition
    df["InsideBar"] = (df["High"] < df["High"].shift(1)) & (df["Low"] > df["Low"].shift(1))
    df["MotherHigh"] = df["High"].shift(1)
    df["MotherLow"] = df["Low"].shift(1)
    df["InsideRange"] = df["MotherHigh"] - df["MotherLow"]

    # Initialize columns
    df["LongBreakout"] = False
    df["ShortBreakout"] = False

    # Avoid NaNs by filtering valid rows only
    valid_rows = df["InsideBar"].shift(1).fillna(False) & df["MotherHigh"].notna() & df["MotherLow"].notna()

    df.loc[valid_rows & (df["High"] > df["MotherHigh"]), "LongBreakout"] = True
    df.loc[valid_rows & (df["Low"] < df["MotherLow"]), "ShortBreakout"] = True

    df["Position"] = 0
    df.loc[df["LongBreakout"], "Position"] = 1
    df.loc[df["ShortBreakout"], "Position"] = -1

    df["SL"] = None
    df["Target"] = None
    df.loc[df["Position"] == 1, "SL"] = df["MotherLow"]
    df.loc[df["Position"] == -1, "SL"] = df["MotherHigh"]
    df.loc[df["Position"] == 1, "Target"] = df["Close"] + 2 * df["InsideRange"]
    df.loc[df["Position"] == -1, "Target"] = df["Close"] - 2 * df["InsideRange"]

    return df
