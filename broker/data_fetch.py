# ==========================================
# HISTORICAL DATA FETCH
# ==========================================

import datetime
from utils.logger import log


# def get_prev_day_ohlc(fyers, symbol="BSE:SENSEX-INDEX"):
#     """
#     Fetch previous day's OHLC
#     """
#
#     today = datetime.date.today()
#
#     from_date = (today - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
#     to_date = today.strftime("%Y-%m-%d")
#
#     data = {
#         "symbol": symbol,
#         "resolution": "D",
#         "date_format": "1",
#         "range_from": from_date,
#         "range_to": to_date,
#         "cont_flag": "1"
#     }
#
#     res = fyers.history(data)
#
#     if "candles" not in res:
#         raise Exception(f"Data Fetch Error: {res}")
#
#     candles = res["candles"]
#
#     if len(candles) < 2:
#         raise Exception("Not enough historical data")
#
#     prev = candles[-2]
#
#     o, h, l, c = prev[1], prev[2], prev[3], prev[4]
#
#     result = {
#         "open": o,
#         "high": h,
#         "low": l,
#         "close": c
#     }
#
#     log(f"PREV DAY OHLC: {result}")
#
#     return result

# ==========================================
# FETCH OHLC FOR ANY SYMBOL (INDEX / OPTION)
# ==========================================

# ------------------------------------------
# GET LAST TRADING DAY
# ------------------------------------------
def get_last_trading_day(today):

    from config.symbols import is_trading_day  # reuse existing logic
    import datetime

    date = today

    while not is_trading_day(date):
        date -= datetime.timedelta(days=1)

    return date


def get_prev_day_ohlc_for_symbol(fyers, symbol):
    from datetime import date, timedelta

    today = date.today()
    to_date = get_last_trading_day(today).strftime("%Y-%m-%d")

    # Previous trading day (for safety buffer)
    from_date = (to_date - timedelta(days=7)).strftime("%Y-%m-%d")

    # from_date = (today - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    # to_date = today.strftime("%Y-%m-%d")

    data = {
        "symbol": symbol,
        "resolution": "D",
        "date_format": "1",
        "range_from": from_date,
        "range_to": to_date,
        "cont_flag": "1"
    }

    res = fyers.history(data)

    if "candles" not in res:
        raise Exception(f"OHLC Fetch Error for {symbol}: {res}")

    candles = res["candles"]

    if len(candles) < 2:
        raise Exception(f"Not enough data for {symbol}")

    prev = candles[-2]

    return {
        "open": prev[1],
        "high": prev[2],
        "low": prev[3],
        "close": prev[4]
    }