# ==========================================
# MAIN ENTRY POINT (ORCHESTRATOR)
# ==========================================

from fyers_apiv3 import fyersModel

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
from utils.time_utils import is_eod_exit_time

import datetime
import threading
import time


# ------------------------------------------
# SYSTEM INIT
# ------------------------------------------
def initialize_system():

    log("SYSTEM STARTING...")
    now = datetime.datetime.now()
    print(f"SYSTEM STARTING... {now}")

    # AUTH
    access_token = get_access_token()

    fyers = fyersModel.FyersModel(
        client_id=CLIENT_ID,
        token=access_token,
        log_path=""
    )

    log("AUTH SUCCESS")

    # ======================================
    # 🔴 SWITCH MODE HERE
    # ======================================

    test_mode = True   # ✅ Change to False for options

    # ======================================
    # TEST MODE (EQUITY)
    # ======================================
    if test_mode:

        eq_symbol = "NSE:HDFCBANK-EQ"

        eq_ohlc = get_prev_day_ohlc_for_symbol(fyers, eq_symbol)
        eq_levels = generate_fib_levels(eq_ohlc["high"], eq_ohlc["low"])

        eq_engine = Engine(fyers, eq_symbol, eq_levels)

        return fyers, [eq_engine], [eq_symbol]

    # ======================================
    # LIVE MODE (OPTIONS)
    # ======================================
    else:

        index_ohlc = get_prev_day_ohlc_for_symbol(fyers, "BSE:SENSEX-INDEX")
        prev_close = index_ohlc["close"]

        symbols = get_option_symbols(prev_close)

        call_symbol = symbols["call"]
        put_symbol = symbols["put"]

        # Fetch OHLC for options safely
        call_ohlc = get_prev_day_ohlc_for_symbol(fyers, call_symbol)
        put_ohlc = get_prev_day_ohlc_for_symbol(fyers, put_symbol)

        call_levels = generate_fib_levels(call_ohlc["high"], call_ohlc["low"])
        put_levels = generate_fib_levels(put_ohlc["high"], put_ohlc["low"])

        call_engine = Engine(fyers, call_symbol, call_levels)
        put_engine = Engine(fyers, put_symbol, put_levels)

        return fyers, [call_engine, put_engine], [call_symbol, put_symbol]


# ------------------------------------------
# MAIN EXECUTION
# ------------------------------------------
def run():

    fyers, engines, symbols = initialize_system()

    log("STARTING WEBSOCKETS...")

    # --------------------------------------
    # RECOVERY SYNC
    # --------------------------------------
    for engine in engines:
        try:
            sync_engine(engine)
        except Exception as e:
            error_log(f"{engine.symbol} RECOVERY FAILED: {e}")

    log("INITIAL RECOVERY COMPLETE")

    # --------------------------------------
    # 🔥 RECONNECT RESYNC
    # --------------------------------------
    def resync_all():

        log("🔄 RECONNECT RESYNC START")

        for engine in engines:
            try:
                sync_engine(engine)
            except Exception as e:
                error_log(f"{engine.symbol} RESYNC FAILED: {e}")

        log("✅ RECONNECT RESYNC COMPLETE")

    # --------------------------------------
    # PRICE CALLBACK
    # --------------------------------------
    def on_message(msg):

        try:
            if "ltp" not in msg:
                return

            symbol = msg.get("symbol")
            price = msg.get("ltp")

            print(f"LTP {symbol} → {price}")

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
                    engine.force_exit()

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
    threading.Thread(
        target=start_order_ws,
        args=(fyers.token, engine_router, resync_all),
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