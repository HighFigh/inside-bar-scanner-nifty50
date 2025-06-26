import yfinance as yf
import pandas as pd

def fetch_data(symbol, interval="15m", period="5d"):
    """
    Fetch data from yfinance and return a cleaned DataFrame.
    """
    try:
        df = yf.download(symbol, interval=interval, period=period, progress=False)
        if df.empty:
            return None
        return df.dropna()
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def detect_inside_bar_breakouts(df):
    """
    Detect inside bar breakout patterns in the given DataFrame.
    Returns the DataFrame with additional columns:
      - InsideBar: Boolean flag if the candle is an inside bar.
      - MotherHigh/MotherLow: The high/low of the previous candle.
      - InsideRange: The range of the mother candle.
      - LongBreakout/ShortBreakout: Boolean flags for breakout signals.
      - Position: 1 for a long signal, -1 for a short signal, 0 otherwise.
      - SL: Calculated Stop Loss for the position.
      - Target: Calculated target price for the position.
    """
    # Guard: Ensure we have enough rows to compare (at least two rows needed)
    if df is None or len(df) < 2:
        return df

    df["InsideBar"] = (df["High"] < df["High"].shift(1)) & (df["Low"] > df["Low"].shift(1))
    df["MotherHigh"] = df["High"].shift(1)
    df["MotherLow"] = df["Low"].shift(1)
    df["InsideRange"] = df["MotherHigh"] - df["MotherLow"]

    # Use shift(1) on the InsideBar to refer to the candle before the current one
    df["LongBreakout"] = df["InsideBar"].shift(1) & (df["High"] > df["MotherHigh"])
    df["ShortBreakout"] = df["InsideBar"].shift(1) & (df["Low"] < df["MotherLow"])
    
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
