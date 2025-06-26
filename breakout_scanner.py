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

    # Step 1: Basic Calculations
    df["Prev_High"] = df["High"].shift(1)
    df["Prev_Low"] = df["Low"].shift(1)

    # Step 2: Identify Inside Bar (current bar is within previous bar's range)
    df["InsideBar"] = (df["High"] < df["Prev_High"]) & (df["Low"] > df["Prev_Low"])

    # Step 3: Prepare mother bar levels
    df["MotherHigh"] = df["Prev_High"]
    df["MotherLow"] = df["Prev_Low"]
    df["InsideRange"] = df["MotherHigh"] - df["MotherLow"]

    # Step 4: Safe Boolean flags
    df["LongBreakout"] = False
    df["ShortBreakout"] = False

    # Only evaluate breakout logic where previous candle was an inside bar
    for i in range(2, len(df)):
        if df.at[i-1, "InsideBar"]:
            if df.at[i, "High"] > df.at[i-1, "Prev_High"]:
                df.at[i, "LongBreakout"] = True
            elif df.at[i, "Low"] < df.at[i-1, "Prev_Low"]:
                df.at[i, "ShortBreakout"] = True

    # Step 5: Assign Positions
    df["Position"] = 0
    df.loc[df["LongBreakout"], "Position"] = 1
    df.loc[df["ShortBreakout"], "Position"] = -1

    # Step 6: SL and Target
    df["SL"] = None
    df["Target"] = None
    df.loc[df["Position"] == 1, "SL"] = df["MotherLow"]
    df.loc[df["Position"] == -1, "SL"] = df["MotherHigh"]
    df.loc[df["Position"] == 1, "Target"] = df["Close"] + 2 * df["InsideRange"]
    df.loc[df["Position"] == -1, "Target"] = df["Close"] - 2 * df["InsideRange"]

    return df
