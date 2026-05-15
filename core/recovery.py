# ==========================================
# INSTITUTION-GRADE RECOVERY SYSTEM
# ==========================================

from broker.orders import get_positions, get_orderbook, cancel_order, place_sl_order
from strategy.fib_strategy import calculate_sl
from utils.logger import log, error_log
from utils.state_logger import log_state


from datetime import datetime

fmt = "%d-%b-%Y %H:%M:%S"

def get_latest_buy_trade(fyers, symbol):

    trades = fyers.tradebook().get("tradeBook", [])
    log(f"ALL ORDERS: {trades}")

    # filter only this symbol
    trades = [t for t in trades if t.get("symbol") == symbol]
    log(f"{symbol} ORDERS: {trades}")

    # sort latest first
    trades.sort(key=lambda x: datetime.strptime(x.get("orderDateTime"), fmt), reverse=True)
    log(f"{symbol} SORTED BY TIME (LATEST FIRST): {trades}")

    for t in trades:
        if t.get("side") == 1:   # BUY
            return float(t.get("tradePrice", 0)), t.get("tradedQty", 0)

    return None, None


def sync_engine(engine):

    symbol = engine.symbol
    state = engine.state
    fyers = engine.fyers

    log(f"{symbol} RECOVERY START")

    # --------------------------------------
    # FETCH BROKER STATE
    # --------------------------------------
    positions = get_positions(fyers) #list of positions are fetched
    log(f"POSITIONS LIST:{positions}")
    orders = get_orderbook(fyers) #list of orders are fetched
    log(f"ORDER BOOK LIST:{orders}")

    # --------------------------------------
    # STEP 1: POSITION RECOVERY
    # --------------------------------------
    active_position = None

    for pos in positions:
        if pos.get("symbol") == symbol and pos.get("qty") != 0:
            active_position = pos
            break

    if active_position:
        # qty = abs(active_position["qty"])
        # entry_price = float(active_position.get("avgPrice", 0))
        if active_position.get("qty")!=0:
            entry_price, qty = get_latest_buy_trade(fyers, symbol)

            log(f"{symbol} POSITION FOUND | QTY={qty} | ENTRY={entry_price}")

            sl_price = calculate_sl(entry_price)

            state.set_active_trade(entry_price, sl_price, qty)
            # state.first_trade_done = True
            try:
                log_state(state, "RECOVERY - OPEN POSITION STATE")
            except Exception as e:
                error_log(f"RECOVERY - OPEN POSITION STATE: LOGGING FAILED: {e}")

    else:
        log(f"{symbol} NO ACTIVE POSITION")
        state.reset_trade()
        try:
            log_state(state, "RECOVERY - NO ACTIVE POSITION - RESET")
        except Exception as e:
            error_log(f"RECOVERY - NO ACTIVE POSITION RESET: LOGGING FAILED: {e}")

    # --------------------------------------
    # STEP 2: ORDER CLASSIFICATION
    # --------------------------------------
    entry_orders = []
    sl_orders = []

    for o in orders:
        if o.get("symbol") == symbol and (o.get("status") == 6 or o.get("status") == 4):
            if o.get("side") == 1:
                entry_orders.append(o)
            elif o.get("side") == -1:
                sl_orders.append(o)


    # --------------------------------------
    # STEP 3: HANDLE ENTRY ORDERS
    # --------------------------------------
    if entry_orders:

        # Keep latest, cancel others
        latest = entry_orders[-1]

        state.entry_order_id = latest.get("id")
        if state.entry_order_id:
            log(f"{symbol} ✓ ENTRY ORDER RECOVERED")
            try:
                log_state(state, "RECOVERY - ENTRY ORDER FOUND")
            except Exception as e:
                error_log(f"RECOVERY - ENTRY ORDER FOUND: LOGGING FAILED: {e}")

        else:
            log(f"{symbol} X ENTRY ORDER ID FETCHING PROBLEM")

        for o in entry_orders[:-1]:
            cancel_order(fyers, o.get("id"))
            log(f"{symbol} CANCELLED STALE ENTRY ORDER")

    else:
        state.entry_order_id = None
        try:
            log_state(state, "RECOVERY - ENTRY ORDER NOT FOUND")
        except Exception as e:
            error_log(f"RECOVERY - ENTRY ORDER NOT FOUND: LOGGING FAILED: {e}")


    # --------------------------------------
    # STEP 4: HANDLE SL ORDERS
    # --------------------------------------
    if state.active_trade:

        expected_sl = state.sl_price

        if sl_orders:

            latest_sl = sl_orders[-1]
            state.sl_order_id = latest_sl.get("id")

            broker_sl = float(latest_sl.get("stopPrice", 0))

            log(f"{symbol} SL ORDER RECOVERED | Broker SL={broker_sl}")

            # 🔥 VALIDATE SL
            if abs(broker_sl - expected_sl) > 1:
                log(f"{symbol} SL MISMATCH -> FIXING")

                can = cancel_order(fyers, latest_sl.get("id"))

                if can.get("s") == "ok":
                    log(f"{symbol} MISMATCHED SL ORDER CANCELLED")
                    try:
                        log_state(state, "RECOVERY - MISMATCH SL ORDER CANCELLED")
                    except Exception as e:
                        error_log(f"RECOVERY - MISMATCH SL ORDER CANCEL: LOGGING FAILED: {e}")

                res = place_sl_order(fyers, symbol, state.qty, expected_sl)

                if res.get("s") == "ok":
                    state.sl_order_id = res.get("id")
                    log(f"{symbol} SL ORDER PLACED SUCCESSFULLY @ {expected_sl}")
                    try:
                        log_state(state, "RECOVERY - CORRECT SL ORDER PLACED")
                    except Exception as e:
                        error_log(f"RECOVERY - CORRECT SL ORDER PLACED: LOGGING FAILED: {e}")

            # cancel duplicates
            for o in sl_orders[:-1]:
                cancel_order(fyers, o.get("id"))

        else:
            # CRITICAL: Missing SL → recreate
            log(f"{symbol} NO SL FOUND -> RECREATING")

            res = place_sl_order(fyers, symbol, state.qty, expected_sl)

            if res.get("s") == "ok":
                state.sl_order_id = res.get("id")
                log(f"{symbol} RECOVERY SL ORDER PLACED SUCCESSFULLY @ {expected_sl}")
                try:
                    log_state(state, "RECOVERY - SL ORDER PLACED")
                except Exception as e:
                    error_log(f"RECOVERY - SL ORDER PLACED: LOGGING FAILED: {e}")


    else:
        # no position → cancel all SL
        for o in sl_orders:
            cancel_order(fyers, o.get("id"))
            log(f"{symbol} CANCELLED ORPHAN SL")

        state.sl_order_id = None
        try:
            log_state(state, "RECOVERY - NO SL ORDER RESET")
        except Exception as e:
            error_log(f"RECOVERY - NO SL ORDER RESET: LOGGING FAILED: {e}")

    # --------------------------------------
    # STEP 5: PARTIAL FILL DETECTION
    # --------------------------------------
    for o in orders:

        if o.get("symbol") != symbol:
            continue

        filled = o.get("filledQty", 0)
        status = o.get("status")

        if filled > 0 and status != 2:
            log(f"{symbol} PARTIAL FILL DETECTED -> {filled}")

            # SAFE ACTION: clear entry order id
            state.entry_order_id = None

    log(f"{symbol} RECOVERY ENGINE COMPLETE")