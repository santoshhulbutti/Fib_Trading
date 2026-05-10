# ==========================================
# MAIN ENTRY POINT (ORCHESTRATOR)
# ==========================================

from fyers_apiv3 import fyersModel

import pandas as pd

from broker.auth import get_access_token
from broker.data_ws import start_ws
from broker.order_ws import start_order_ws
from broker.data_fetch import get_prev_day_ohlc_for_symbol

from config.settings import CLIENT_ID
from config.symbols import get_option_symbols

from strategy.fib_strategy import generate_fib_levels

from core.engine import Engine
from core.recovery import sync_engine

from utils.logger import log, error_log
from utils.state_logger import log_state
from utils.time_utils import is_eod_exit_time

import datetime
import threading
import time

order_ws_initialized = False

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

    log("FYERS MODEL CREATED...")

    # ======================================
    # 🔴 SWITCH MODE HERE
    # ======================================

    test_mode = True   # ✅ Change to False for options

    # ======================================
    # TEST MODE (EQUITY)
    # ======================================
    if test_mode:

        eq_symbol = "NSE:ADANIPORTS-EQ"

        # for sym in eq_symbol: # Need to check for list of eq symbols & how to create multiple Engine instances.
        eq_ohlc = get_prev_day_ohlc_for_symbol(fyers, eq_symbol)
        eq_levels = generate_fib_levels(eq_ohlc["high"], eq_ohlc["low"])
        log(f"Yesterday's OHLC for {eq_symbol} : {eq_ohlc}")
        log(f"Fib levels for {eq_symbol} : {eq_levels}")

        eq_engine = Engine(fyers, eq_symbol, eq_levels)

        try:
            log_state(eq_engine.state,"MAIN INITIAL STATE")
        except Exception as e:
            error_log(f"MAIN INITIAL STATE LOGGING FAILED: {e}")

        return fyers, [eq_engine], [eq_symbol]

    # ======================================
    # LIVE MODE (OPTIONS)
    # ======================================
    else:

        index_ohlc = get_prev_day_ohlc_for_symbol(fyers, "BSE:SENSEX-INDEX")
        log(f"Yesterday's OHLC for BSE:SENSEX-INDEX : {index_ohlc}")
        prev_close = index_ohlc["close"]

        symbols = get_option_symbols(prev_close)

        call_symbol = symbols["call"]
        put_symbol = symbols["put"]

        # Fetch OHLC for options safely
        call_ohlc = get_prev_day_ohlc_for_symbol(fyers, call_symbol)
        put_ohlc = get_prev_day_ohlc_for_symbol(fyers, put_symbol)

        call_levels = generate_fib_levels(call_ohlc["high"], call_ohlc["low"])
        put_levels = generate_fib_levels(put_ohlc["high"], put_ohlc["low"])

        log(f"Fib levels for {call_symbol} : {call_levels}")
        log(f"Fib levels for {put_symbol} : {put_levels}")

        call_engine = Engine(fyers, call_symbol, call_levels)
        put_engine = Engine(fyers, put_symbol, put_levels)

        try:
            log_state(call_engine.state, "MAIN CALL INITIAL STATE")
            log_state(put_engine.state, "MAIN PUT INITIAL STATE")
        except Exception as e:
            error_log(f"INITIAL STATE LOGGING FAILED: {e}")

        return fyers, [call_engine, put_engine], [call_symbol, put_symbol]


# ------------------------------------------
# MAIN EXECUTION
# ------------------------------------------
def run():

    fyers, engines, symbols = initialize_system()

    log("ENGINE INSTANCE CREATION COMPLETE...")

    # --------------------------------------
    # RECOVERY SYNC
    # --------------------------------------
    for engine in engines:
        try:
            sync_engine(engine)
        except Exception as e:
            error_log(f"{engine.symbol} RECOVERY FAILED: {e}")

    log("INITIAL RECOVERY ENGINE COMPLETED")

    # --------------------------------------
    # 🔥 RECONNECT RESYNC
    # --------------------------------------

    def resync_all():

        global order_ws_initialized

        # ----------------------------------
        # SKIP FIRST CONNECT
        # ----------------------------------
        if not order_ws_initialized:
            order_ws_initialized = True

            log("INITIAL ORDER WS CONNECT -> SKIPPING RESYNC")

            return

        # ----------------------------------
        # REAL RECONNECT RESYNC
        # ----------------------------------

        log("RECONNECT RESYNC START")

        for engine in engines:
            try:
                sync_engine(engine)
            except Exception as e:
                error_log(f"{engine.symbol} RESYNC FAILED: {e}")

        log("RECONNECT RESYNC ENGINE COMPLETE")

    # --------------------------------------
    # PRICE CALLBACK
    # --------------------------------------
    def on_message(msg):

        # print("Response:", msg)
        # df = pd.DataFrame([msg])
        # print(df[['ltp', 'symbol']])

        try:
            if "ltp" not in msg:
                return

            symbol = msg.get("symbol")
            price = msg.get("ltp")

            # print(f"LTP {symbol} -> {price}")

            # ROUTE TO ENGINE
            for engine in engines:
                if engine.symbol == symbol:
                    engine.on_tick(price)

            # ----------------------------------
            # EOD EXIT
            # ----------------------------------
            if is_eod_exit_time():
                log("EOD EXIT TRIGGERED")

                for engine in engines:
                    # res = engine.force_exit()
                    try:
                        res = engine.force_exit()
                        log(f"EOD EXIT FOR {engine.symbol} : {res.get("message")}")
                    except Exception as e:
                        log(f"EOD EXIT ERROR: {e}")


        except Exception as ex:
            error_log(f"MAIN ERROR: {ex}")

    # --------------------------------------
    # ORDER/TRADES CALLBACK
    # --------------------------------------
    def engine_router(event_type, msg):
        try:
            symbol = msg.get("symbol")

            for engine in engines:
                if engine.symbol == symbol:

                    if event_type == "TRADE":
                        engine.handle_trade_update(msg)

                    elif event_type == "ORDER":
                        engine.handle_order_update(msg)

                    elif event_type == "POSITION":
                        engine.handle_position_update(msg)

        except Exception as exp:
            error_log(f"ROUTER ERROR: {exp}")

    log("STARTING WEBSOCKETS...")
    # --------------------------------------
    # START DATA WS (THREAD)
    # --------------------------------------
    threading.Thread(
        target=start_ws,
        args=(fyers.token, symbols, on_message),
        daemon=True
    ).start()

    # --------------------------------------
    # START ORDER WS (THREAD)
    # --------------------------------------
    order_token = CLIENT_ID+":"+fyers.token
    threading.Thread(
        target=start_order_ws,
        args=(order_token, engine_router, resync_all),
        daemon=True
    ).start()

    # --------------------------------------
    # KEEP MAIN ALIVE
    # --------------------------------------
    while True:
        time.sleep(1)


# ------------------------------------------
# ENTRY POINT
# ------------------------------------------
if __name__ == "__main__":
    run()