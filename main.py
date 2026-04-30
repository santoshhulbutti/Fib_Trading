# ==========================================
# MAIN ENTRY POINT (ORCHESTRATOR)
# ==========================================

from fyers_apiv3 import fyersModel

from broker.auth import get_access_token
from broker.data_ws import start_ws
from broker.data_fetch import get_prev_day_ohlc_for_symbol

from config.settings import CLIENT_ID
from config.trading_params import FIB_RATIOS, SL_POINTS
from config.symbols import get_atm_strike, build_option_symbol, get_option_symbols

from strategy.fib_strategy import generate_fib_levels

from core.engine import Engine
from utils.logger import log, error_log
from utils.time_utils import is_eod_exit_time

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
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S.%f")[:-3]   # trim to milliseconds
    print(f"SYSTEM STARTING... Current Time = {current_time}")

    # AUTH
    access_token = get_access_token()

    fyers = fyersModel.FyersModel(
        client_id=CLIENT_ID,
        token=access_token,
        log_path=""
    )

    log("AUTH SUCCESS")
    current_time = now.strftime("%H:%M:%S.%f")[:-3]  # trim to milliseconds
    print(f"AUTH SUCCESS... Current Time = {current_time}")

    # --------------------------------------
    # GET ATM OPTION SYMBOLS
    # --------------------------------------
    # First get index close (for ATM calculation)
    index_ohlc = get_prev_day_ohlc_for_symbol(fyers, "BSE:SENSEX-INDEX")
    prev_close = index_ohlc["close"]

    symbols = get_option_symbols(prev_close)

    call_symbol = symbols["call"]
    put_symbol = symbols["put"]

    log(f"CALL SYMBOL: {call_symbol}")
    log(f"PUT SYMBOL: {put_symbol}")

    # --------------------------------------
    # FETCH OPTION OHLC (CRITICAL FIX)
    # --------------------------------------
    call_ohlc = get_prev_day_ohlc_for_symbol(fyers, call_symbol)
    put_ohlc = get_prev_day_ohlc_for_symbol(fyers, put_symbol)

    log(f"CALL OHLC: {call_ohlc}")
    log(f"PUT OHLC: {put_ohlc}")

    # --------------------------------------
    # GENERATE FIB LEVELS (SEPARATE)
    # --------------------------------------
    call_levels = generate_fib_levels(call_ohlc["high"], call_ohlc["low"])
    put_levels = generate_fib_levels(put_ohlc["high"], put_ohlc["low"])

    log(f"CALL LEVELS: {call_levels}")
    log(f"PUT LEVELS: {put_levels}")

    # --------------------------------------
    # INIT ENGINES
    # --------------------------------------
    call_engine = Engine(fyers, call_symbol, call_levels)
    put_engine = Engine(fyers, put_symbol, put_levels)

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

    def on_message(msg):

        try:
            if "ltp" not in msg:
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
            if is_eod_exit_time():
                log("EOD EXIT TRIGGERED")
                call_engine.force_exit()
                put_engine.force_exit()

        except Exception as e:
            error_log(f"MAIN ERROR: {e}")

    # START WS
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