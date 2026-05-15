# =========================================================
# stock_screen_intra.py
# =========================================================
# Screens NSE Nifty 500 stocks using FYERS historical API
#
# CONDITIONS:
# 1. Price > 10 EMA > 20 EMA > 50 EMA > 100 EMA
# 2. Last candle low < lowest low of previous 3 candles
# 3. Last candle high > highest high of previous 2 candles
# 4. Last candle volume > 2x previous candle volume
#
# OUTPUT:
# Saves all matching stocks in to a csv file.
#
# REQUIREMENTS:
# pip install fyers-apiv3 pandas ta
#
# =========================================================

from fyers_apiv3 import fyersModel
import pandas as pd
from ta.trend import EMAIndicator
from datetime import datetime, timedelta
from pathlib import Path
import time
import os


BASE_DIR = Path(__file__).resolve().parent.parent
SYMBOL_FILE = BASE_DIR / "data/stock_list/nifty500_symbols.csv"
FILTERED_FILE = BASE_DIR / "data/filtered_stocks/filtered_stocks.csv"

# =========================================================
# CONFIG
# =========================================================
#
# CLIENT_ID = "YOUR_CLIENT_ID"
# ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
#
# # =========================================================
# # FYERS CONNECTION
# # =========================================================
#
# fyers = fyersModel.FyersModel(
#     client_id=CLIENT_ID,
#     token=ACCESS_TOKEN,
#     is_async=False,
#     log_path=""
# )

# =========================================================
# DOWNLOAD NIFTY500 STOCKS
# =========================================================

def download_nifty500_symbols():

    print("Downloading Nifty 500 stock list...")

    url = "https://nsearchives.nseindia.com/content/indices/ind_nifty500list.csv"

    df = pd.read_csv(url)

    # Convert to FYERS format
    df["fyers_symbol"] = "NSE:" + df["Symbol"] + "-EQ"

    # Save locally
    df[["fyers_symbol"]].to_csv(
        SYMBOL_FILE,
        index=False
    )

    print(f"Saved symbols to {SYMBOL_FILE}")


# =========================================================
# LOAD SYMBOLS FROM LOCAL FILE
# =========================================================

def load_symbols():

    if not os.path.exists(SYMBOL_FILE):

        print("Symbol file not found.")
        download_nifty500_symbols()

    df = pd.read_csv(SYMBOL_FILE)

    return df["fyers_symbol"].tolist()


# =========================================================
# FETCH HISTORICAL DATA
# =========================================================

def get_historical_data(symbol, fyers):

    range_from = (
        datetime.now() - timedelta(days=250)
    ).strftime("%Y-%m-%d")

    range_to = datetime.now().strftime("%Y-%m-%d")

    data = {
        "symbol": symbol,
        "resolution": "D",
        "date_format": "1",
        "range_from": range_from,
        "range_to": range_to,
        "cont_flag": "1"
    }

    response = fyers.history(data=data)
    print(response)

    if response.get("s") != "ok":

        print(f"Failed: {symbol}")
        return None

    candles = response["candles"]

    df = pd.DataFrame(
        candles,
        columns=[
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]
    )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        unit="s"
    )

    return df


# =========================================================
# EMA CALCULATION
# =========================================================

def calculate_ema(df):

    df["EMA10"] = EMAIndicator(
        close=df["close"],
        window=10
    ).ema_indicator()

    df["EMA20"] = EMAIndicator(
        close=df["close"],
        window=20
    ).ema_indicator()

    df["EMA50"] = EMAIndicator(
        close=df["close"],
        window=50
    ).ema_indicator()

    df["EMA100"] = EMAIndicator(
        close=df["close"],
        window=100
    ).ema_indicator()

    return df


# =========================================================
# SCREENING CONDITIONS
# =========================================================

def check_conditions(df):

    if len(df) < 120:
        return False

    last = df.iloc[-1]

    prev1 = df.iloc[-2]
    prev2 = df.iloc[-3]
    prev3 = df.iloc[-4]

    # ---------------------------------------------
    # Condition 1
    # ---------------------------------------------

    cond1 = (
        last["close"] > last["EMA10"] >
        last["EMA20"] >
        last["EMA50"] >
        last["EMA100"]
    )

    # ---------------------------------------------
    # Condition 2
    # Last low below previous 3 lows
    # ---------------------------------------------

    prev_3_low = min(
        prev1["low"],
        prev2["low"],
        prev3["low"]
    )

    cond2 = last["low"] < prev_3_low

    # ---------------------------------------------
    # Condition 3
    # Last high above previous 2 highs
    # ---------------------------------------------

    prev_2_high = max(
        prev1["high"],
        prev2["high"]
    )

    cond3 = last["high"] > prev_2_high

    # ---------------------------------------------
    # Condition 4
    # Volume expansion
    # ---------------------------------------------

    cond4 = (
        last["volume"] >
        2 * prev1["volume"]
    )

    return cond1 and cond2 and cond3 and cond4


# =========================================================
# SAVE FILTERED STOCKS
# =========================================================

def save_filtered_stocks(stock_list):

    df = pd.DataFrame({
        "symbol": stock_list
    })

    df.to_csv(
        FILTERED_FILE,
        index=False
    )

    print(f"\nSaved filtered stocks to {FILTERED_FILE}")


# =========================================================
# LOAD FILTERED STOCKS
# =========================================================

def load_filtered_stocks():

    if not os.path.exists(FILTERED_FILE):

        print("Filtered stock file not found.")
        return []

    df = pd.read_csv(FILTERED_FILE)

    return df["symbol"].tolist()


# =========================================================
# MAIN SCREENER
# =========================================================

def run_screener(access_token):
    from config.settings import CLIENT_ID
    fyers = fyersModel.FyersModel(
        client_id=CLIENT_ID,
        token=access_token,
        is_async=False,
        log_path=""
    )

    symbols = load_symbols()

    print(f"\nLoaded {len(symbols)} stocks\n")

    matched_stocks = []

    for symbol in symbols:

        try:

            df = get_historical_data(symbol, fyers)

            if df is None:
                continue

            df = calculate_ema(df)

            if check_conditions(df):

                matched_stocks.append(symbol)

                print(f"MATCHED: {symbol}")

            time.sleep(0.25)

        except Exception as e:

            print(f"Error: {symbol} -> {e}")

    # Save filtered stocks
    save_filtered_stocks(matched_stocks)

    return #matched_stocks


# =========================================================
# ENTRY
# =========================================================
#
# if __name__ == "__main__":
#
#     # Run screener
#     filtered_list = run_screener()
#
#     print("\n==============================")
#     print("FILTERED STOCKS")
#     print("==============================")
#
#     for stock in filtered_list:
#         print(stock)
#
#     # Example:
#     # Load filtered stocks later
#     live_trade_list = load_filtered_stocks()
#
#     print("\nLoaded for strategy:")
#     print(live_trade_list)