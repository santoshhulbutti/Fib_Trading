# ==========================================
# MAIN ENTRY POINT (ORCHESTRATOR)
# ==========================================

from fyers_apiv3 import fyersModel
from auth import get_access_token
from broker.data_ws import start_ws
from broker.data_fetch import get_prev_day_ohlc
from config.settings import CLIENT_ID
from config.trading_params import FIB_RATIOS, SL_POINTS

from instrument import get_atm_strike, build_option_symbol
from core.engine import Engine
from utils.logger import log

import datetime

# ------------------------------------------
# FIB LEVEL CALCULATION
# ------------------------------------------

def calculate_fib_levels(high, low):
    diff = high - low
    levels = [round(high - diff * r, 2) for r in FIB_RATIOS]
    levels.sort()
    return levels


# ------------------------------------------
# SYSTEM INIT
# ------------------------------------------

def initialize_system():

    log("SYSTEM STARTING...")

    # AUTH
    access_token = get_access_token()

    fyers = fyersModel.FyersModel(
        client_id=CLIENT_ID,
        token=access_token,
        log_path=""
    )

    log("AUTH SUCCESS")

    # --------------------------------------
    # FETCH PREVIOUS DAY DATA
    # --------------------------------------
    ohlc = get_prev_day_ohlc(fyers)

    prev_high = ohlc["high"]
    prev_low = ohlc["low"]
    prev_close = ohlc["close"]

    log(f"PREV DAY DATA: {ohlc}")

    # --------------------------------------
    # ATM STRIKE
    # --------------------------------------
    atm_strike = get_atm_strike(prev_close)

    log(f"ATM STRIKE: {atm_strike}")

    # --------------------------------------
    # SYMBOLS
    # --------------------------------------
    call_symbol = build_option_symbol(atm_strike, "CE")
    put_symbol = build_option_symbol(atm_strike, "PE")

    log(f"CALL SYMBOL: {call_symbol}")
    log(f"PUT SYMBOL: {put_symbol}")

    # --------------------------------------
    # LEVELS
    # --------------------------------------
    levels = calculate_fib_levels(prev_high, prev_low)

    log(f"FIB LEVELS: {levels}")

    # --------------------------------------
    # ENGINE INIT
    # --------------------------------------
    call_engine = Engine(fyers, call_symbol, levels)
    put_engine = Engine(fyers, put_symbol, levels)

    log("ENGINES INITIALIZED")

    return fyers, call_engine, put_engine, call_symbol, put_symbol


# ------------------------------------------
# EOD CHECK
# ------------------------------------------

def is_eod():
    now = datetime.datetime.now()
    return now.hour == 15 and now.minute >= 20


# ------------------------------------------
# MAIN EXECUTION
# ------------------------------------------

def run():

    fyers, call_engine, put_engine, call_symbol, put_symbol = initialize_system()

    log("STARTING WEBSOCKET...")

    # --------------------------------------
    # WEBSOCKET CALLBACK
    # --------------------------------------
    def on_message(msg):

        try:
            if 'ltp' not in msg:
                return

            symbol = msg.get("symbol")
            price = msg.get("ltp")

            # ROUTE TO ENGINE
            if symbol == call_symbol:
                call_engine.on_tick(price)

            elif symbol == put_symbol:
                put_engine.on_tick(price)

            # ----------------------------------
            # EOD EXIT
            # ----------------------------------
            if is_eod():
                log("EOD EXIT TRIGGERED")

                call_engine.force_exit()
                put_engine.force_exit()

        except Exception as e:
            log(f"ERROR: {e}")

    # --------------------------------------
    # START LIVE DATA
    # --------------------------------------
    start_ws(
        access_token=fyers.token,
        symbols=[call_symbol, put_symbol],
        on_message=on_message
    )


# ------------------------------------------
# ENTRY POINT
# ------------------------------------------

if __name__ == "__main__":
    run()