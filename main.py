# ==========================================
# MAIN ENTRY POINT (ORCHESTRATOR)
# ==========================================

from fyers_apiv3 import fyersModel

from broker.auth import get_access_token
from broker.data_ws import start_ws
from broker.order_ws import start_order_ws   # ✅ NEW
from broker.data_fetch import get_prev_day_ohlc_for_symbol

from config.settings import CLIENT_ID
from config.trading_params import FIB_RATIOS
from config.symbols import get_option_symbols

from strategy.fib_strategy import generate_fib_levels

from core.engine import Engine
from utils.logger import log, error_log
from utils.time_utils import is_eod_exit_time

import datetime
import threading


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

    TEST_MODE = True   # ✅ Change to False for options

    # ======================================
    # TEST MODE (EQUITY)
    # ======================================
    if TEST_MODE:

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

        except Exception as e:
            error_log(f"MAIN ERROR: {e}")

    # --------------------------------------
    # ORDER/TRADES CALLBACK
    # --------------------------------------
    def engine_router(event_type, msg):

        symbol = msg.get("symbol")

        for engine in engines:
            if engine.symbol == symbol:

                if event_type == "TRADE":
                    engine.handle_trade_update(msg)

                elif event_type == "ORDER":
                    engine.handle_order_update(msg)

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
        args=(fyers.token, engine_router),
        daemon=True
    ).start()

    # --------------------------------------
    # KEEP MAIN ALIVE
    # --------------------------------------
    while True:
        pass


# ------------------------------------------
# ENTRY POINT
# ------------------------------------------
if __name__ == "__main__":
    run()