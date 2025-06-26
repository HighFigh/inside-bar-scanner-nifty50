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

    # Add necessary columns
    df["InsideBar"] = False
    df["LongBreakout"] = False
    df["ShortBreakout"] = False
    df["Position"] = 0
    df["SL"] = None
    df["Target"] = None
    df["MotherHigh"] = None
    df["MotherLow"] = None
    df["InsideRange"] = None

    # Cache column indexes for speed and accuracy
    col_High = df.columns.get_loc("High")
    col_Low = df.columns.get_loc("Low")
    col_Close = df.columns.get_loc("Close")
    col_InsideBar = df.columns.get_loc("InsideBar")
    col_Long = df.columns.get_loc("LongBreakout")
    col_Short = df.columns.get_loc("ShortBreakout")
    col_Pos = df.columns.get_loc("Position")
    col_SL = df.columns.get_loc("SL")
    col_Target = df.columns.get_loc("Target")
    col_MH = df.columns.get_loc("MotherHigh")
    col_ML = df.columns.get_loc("MotherLow")
    col_IR = df.columns.get_loc("InsideRange")

    for i in range(1, len(df)):
        prev_high = df.iloc[i - 1, col_High]
        prev_low = df.iloc[i - 1, col_Low]
        curr_high = df.iloc[i, col_High]
        curr_low = df.iloc[i, col_Low]

        if float(curr_high) < float(prev_high) and float(curr_low) > float(prev_low):
            df.iat[i, col_InsideBar] = True

    for i in range(2, len(df)):
        if df.iat[i - 1, col_InsideBar]:
            mother_high = df.iat[i - 1, col_High]
            mother_low = df.iat[i - 1, col_Low]
            close = df.iat[i, col_Close]
            inside_range = mother_high - mother_low

            df.iat[i, col_MH] = mother_high
            df.iat[i, col_ML] = mother_low
            df.iat[i, col_IR] = inside_range

            if df.iat[i, col_High] > mother_high:
                df.iat[i, col_Long] = True
                df.iat[i, col_Pos] = 1
                df.iat[i, col_SL] = mother_low
                df.iat[i, col_Target] = close + 2 * inside_range

            elif df.iat[i, col_Low] < mother_low:
                df.iat[i, col_Short] = True
                df.iat[i, col_Pos] = -1
                df.iat[i, col_SL] = mother_high
                df.iat[i, col_Target] = close - 2 * inside_range

    return df
