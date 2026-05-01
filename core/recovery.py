# ==========================================
# INSTITUTION-GRADE RECOVERY SYSTEM
# ==========================================

from broker.orders import get_positions, get_orderbook, cancel_order, place_sl_order
from utils.logger import log


def sync_engine(engine):

    symbol = engine.symbol
    state = engine.state
    fyers = engine.fyers

    log(f"{symbol} 🔄 RECOVERY START")

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
        if pos["symbol"] == symbol and pos["qty"] != 0:
            active_position = pos
            break

    if active_position:
        qty = abs(active_position["qty"])
        entry_price = float(active_position.get("avgPrice", 0))

        log(f"{symbol} ✅ POSITION FOUND | Qty={qty} | Entry={entry_price}")

        state.set_active_trade(entry_price, None, qty)

    else:
        log(f"{symbol} ❌ NO ACTIVE POSITION")

    # --------------------------------------
    # STEP 2: ORDER CLASSIFICATION
    # --------------------------------------
    entry_orders = []
    sl_orders = []

    for o in orders:
        if o["symbol"] != symbol:
            continue

        status = o.get("status")

        if status != 1:  # only open orders
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

        log(f"{symbol} 🔁 ENTRY ORDER RECOVERED")

        for o in entry_orders[:-1]:
            cancel_order(fyers, o["id"])
            log(f"{symbol} ❌ CANCELLED STALE ENTRY ORDER")

    else:
        state.entry_order_id = None

    # --------------------------------------
    # STEP 4: HANDLE SL ORDERS
    # --------------------------------------
    if state.active_trade:

        if sl_orders:

            latest_sl = sl_orders[-1]
            state.sl_order_id = latest_sl["id"]

            log(f"{symbol} 🛡️ SL ORDER RECOVERED")

            # cancel duplicates
            for o in sl_orders[:-1]:
                cancel_order(fyers, o["id"])

        else:
            # 🚨 CRITICAL: Missing SL → recreate
            log(f"{symbol} ⚠ NO SL FOUND → RECREATING")

            sl_price = state.entry_price - 25  # or your SL logic

            res = place_sl_order(fyers, symbol, state.qty, sl_price)

            state.sl_order_id = res.get("id")

            log(f"{symbol} 🛡️ NEW SL PLACED @ {sl_price}")

    else:
        # no position → cancel all SL
        for o in sl_orders:
            cancel_order(fyers, o["id"])
            log(f"{symbol} ❌ CANCELLED ORPHAN SL")

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
            log(f"{symbol} ⚠ PARTIAL FILL DETECTED → {filled}")

    log(f"{symbol} ✅ RECOVERY COMPLETE")