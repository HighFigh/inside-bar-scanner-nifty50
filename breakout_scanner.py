import yfinance as yf
import pandas as pd

def fetch_data(symbol, interval="15m", period="5d"):
    df = yf.download(symbol, interval=interval, period=period, progress=False)
    return df.dropna()

def detect_inside_bar_breakouts(df):
    df["InsideBar"] = (df["High"] < df["High"].shift(1)) & (df["Low"] > df["Low"].shift(1))
    df["MotherHigh"] = df["High"].shift(1)
    df["MotherLow"] = df["Low"].shift(1)
    df["InsideRange"] = df["MotherHigh"] - df["MotherLow"]
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
