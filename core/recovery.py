# ==========================================
# INSTITUTION-GRADE RECOVERY SYSTEM
# ==========================================

from broker.orders import get_positions, get_orderbook, cancel_order, place_sl_order
from strategy.fib_strategy import calculate_sl
from utils.logger import log

def get_latest_buy_trade(fyers, symbol):

    trades = fyers.tradebook().get("tradeBook", [])
    log(f"all orders {trades}")

    # filter only this symbol
    trades = [t for t in trades if t["symbol"] == symbol]
    log(f"{symbol} orders {trades}")


    # sort latest first
    trades.sort(key=lambda x: x["tradeDateTime"], reverse=True)
    log(f"{symbol} sorted by time orders {trades}")

    for t in trades:
        if t["side"] == 1:   # BUY
            return float(t.get("tradedPrice", 0)), t.get("qty", 0)

    return None, None


def sync_engine(engine):

    symbol = engine.symbol
    state = engine.state
    fyers = engine.fyers

    log(f"{symbol} RECOVERY START")

    # --------------------------------------
    # FETCH BROKER STATE
    # --------------------------------------
    positions = get_positions(fyers)
    orders = get_orderbook(fyers)

    # --------------------------------------
    # STEP 1: POSITION RECOVERY
    # --------------------------------------
    active_position = None

    for pos in positions:
        print(pos)
        if pos["symbol"] == symbol and pos["qty"] != 0:
            active_position = pos
            break

    if active_position:
        # qty = abs(active_position["qty"])
        # entry_price = float(active_position.get("avgPrice", 0))
        if active_position["qty"]>0:
            entry_price, qty = get_latest_buy_trade(fyers, symbol)

            log(f"{symbol} POSITION FOUND | Qty={qty} | Entry={entry_price}")

            sl_price = calculate_sl(entry_price)

            state.set_active_trade(entry_price, sl_price, qty)

    else:
        log(f"{symbol} NO ACTIVE POSITION")
        state.reset_trade()

    # --------------------------------------
    # STEP 2: ORDER CLASSIFICATION
    # --------------------------------------
    entry_orders = []
    sl_orders = []

    for o in orders:
        if o["symbol"] != symbol:
            continue

        if o.get("status") != 1:
            continue

        if o["side"] == 1:
            entry_orders.append(o)

        elif o["side"] == -1:
            sl_orders.append(o)

    # --------------------------------------
    # STEP 3: HANDLE ENTRY ORDERS
    # --------------------------------------
    if entry_orders:

        # Keep latest, cancel others
        latest = entry_orders[-1]

        state.entry_order_id = latest["id"]

        log(f"{symbol} ENTRY ORDER RECOVERED")

        for o in entry_orders[:-1]:
            cancel_order(fyers, o["id"])
            log(f"{symbol} CANCELLED STALE ENTRY ORDER")

    else:
        state.entry_order_id = None

    # --------------------------------------
    # STEP 4: HANDLE SL ORDERS
    # --------------------------------------
    if state.active_trade:

        expected_sl = state.sl_price

        if sl_orders:

            latest_sl = sl_orders[-1]
            state.sl_order_id = latest_sl["id"]

            broker_sl = float(latest_sl.get("stopPrice", 0))

            log(f"{symbol} SL ORDER RECOVERED | Broker SL={broker_sl}")

            # 🔥 VALIDATE SL
            if abs(broker_sl - expected_sl) > 1:
                log(f"{symbol} SL MISMATCH -> FIXING")

                cancel_order(fyers, latest_sl["id"])

                res = place_sl_order(fyers, symbol, state.qty, expected_sl)
                state.sl_order_id = res.get("id")

            # cancel duplicates
            for o in sl_orders[:-1]:
                cancel_order(fyers, o["id"])

        else:
            # CRITICAL: Missing SL → recreate
            log(f"{symbol} NO SL FOUND -> RECREATING")

            res = place_sl_order(fyers, symbol, state.qty, expected_sl)

            state.sl_order_id = res.get("id")

            log(f"{symbol} NEW SL PLACED @ {expected_sl}")

    else:
        # no position → cancel all SL
        for o in sl_orders:
            cancel_order(fyers, o["id"])
            log(f"{symbol} CANCELLED ORPHAN SL")

        state.sl_order_id = None

    # --------------------------------------
    # STEP 5: PARTIAL FILL DETECTION
    # --------------------------------------
    for o in orders:

        if o["symbol"] != symbol:
            continue

        filled = o.get("filledQty", 0)
        status = o.get("status")

        if filled > 0 and status != 2:
            log(f"{symbol} PARTIAL FILL DETECTED -> {filled}")

            # SAFE ACTION: clear entry order id
            state.entry_order_id = None

    log(f"{symbol} RECOVERY ENGINE COMPLETE")