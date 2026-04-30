# ==========================================
# ORDER MANAGEMENT
# ==========================================

import time
from utils.logger import log


# ------------------------------------------
# PLACE STOP BUY ORDER
# ------------------------------------------
def place_stop_buy(fyers, symbol, qty, trigger_price):
    data = {
        "symbol": symbol,
        "qty": qty,
        "type": 3,  # STOP LIMIT
        "side": 1,  # BUY
        "productType": "INTRADAY",
        "limitPrice": trigger_price,
        "stopPrice": trigger_price,
        "validity": "DAY"
    }

    res = fyers.place_order(data)
    log(f"STOP BUY ORDER: {res}")
    return res

####        TEST CODE BLOCK - start
# def place_stop_sell(fyers, symbol, qty, trigger_price):
#     data = {
#         "symbol": symbol,
#         "qty": qty,
#         "type": 3,  # STOP LIMIT
#         "side": -1,  # sell
#         "productType": "INTRADAY",
#         "limitPrice": trigger_price,
#         "stopPrice": trigger_price,
#         "validity": "DAY"
#     }
#
#     res = fyers.place_order(data)
#     log(f"STOP SELL ORDER: {res}")
#     return res
####        TEST CODE BLOCK - end

# ------------------------------------------
# PLACE STOP LOSS ORDER
# ------------------------------------------
def place_sl_order(fyers, symbol, qty, sl_price):
    data = {
        "symbol": symbol,
        "qty": qty,
        "type": 3,
        "side": -1,  # SELL
        "productType": "INTRADAY",
        "limitPrice": sl_price,
        "stopPrice": sl_price,
        "validity": "DAY"
    }

    res = fyers.place_order(data)
    log(f"SL ORDER: {res}")
    return res


####        TEST CODE BLOCK - start
def place_sell_sl_order(fyers, symbol, qty, sl_price):
    data = {
        "symbol": symbol,
        "qty": qty,
        "type": 3,
        "side": 1,  # buy
        "productType": "INTRADAY",
        "limitPrice": sl_price,
        "stopPrice": sl_price,
        "validity": "DAY"
    }

    res = fyers.place_order(data)
    log(f"SL ORDER: {res}")
    return res
####        TEST CODE BLOCK - end

# ------------------------------------------
# MARKET ORDER (EXIT)
# ------------------------------------------
def place_market_order(fyers, symbol, qty, side):
    data = {
        "symbol": symbol,
        "qty": qty,
        "type": 2,  # MARKET
        "side": 1 if side == "BUY" else -1,
        "productType": "INTRADAY",
        "limitPrice": 0,
        "stopPrice": 0,
        "validity": "DAY"
    }

    res = fyers.place_order(data)
    log(f"MARKET ORDER: {res}")
    return res


# ------------------------------------------
# CANCEL ORDER
# ------------------------------------------
def cancel_order(fyers, order_id):
    res = fyers.cancel_order({"id": order_id})
    log(f"CANCEL ORDER: {res}")
    return res


# ------------------------------------------
# MODIFY ORDER (TRAILING SL)
# ------------------------------------------
def modify_order(fyers, order_id, price, trigger):
    data = {
        "id": order_id,
        "type": 3,
        "limitPrice": price,
        "stopPrice": trigger,
        "qty": 0
    }

    res = fyers.modify_order(data)
    log(f"MODIFY ORDER: {res}")
    return res


# ------------------------------------------
# GET ORDER STATUS
# ------------------------------------------
def get_order_status(fyers, order_id):
    res = fyers.orderbook()

    for order in res.get("orderBook", []):
        if order["id"] == order_id:
            return order["status"]

    return None


# ------------------------------------------
# GET ORDER BY ID
# ------------------------------------------
def get_order_by_id(fyers, order_id):

    res = fyers.orderbook()

    if "orderBook" not in res:
        return None

    for order in res["orderBook"]:
        if order["id"] == order_id:
            return order

    return None


# ------------------------------------------
# CHECK IF ORDER FILLED
# ------------------------------------------
def is_order_filled(fyers, order_id):

    order = get_order_by_id(fyers, order_id)

    if not order:
        return False

    return order.get("status") == 2  # 2 = FILLED


# ------------------------------------------
# WAIT FOR EXECUTION (IMPORTANT)
# ------------------------------------------
def wait_for_execution(fyers, order_id, timeout=10):
    start = time.time()

    while time.time() - start < timeout:
        status = get_order_status(fyers, order_id)

        if status == 2:  # FILLED
            log(f"ORDER FILLED: {order_id}")
            return True

        elif status == 5:  # REJECTED
            log(f"ORDER REJECTED: {order_id}")
            return False

        time.sleep(1)

    log(f"ORDER TIMEOUT: {order_id}")
    return False


# ------------------------------------------
# GET POSITIONS
# ------------------------------------------
def get_positions(fyers):
    res = fyers.positions()
    return res.get("netPositions", [])


# ------------------------------------------
# CLOSE POSITION
# ------------------------------------------
def close_position(fyers, symbol):
    positions = get_positions(fyers)

    for pos in positions:
        if pos["symbol"] == symbol and pos["qty"] != 0:

            qty = abs(pos["qty"])
            side = "SELL" if pos["qty"] > 0 else "BUY"

            log(f"CLOSING POSITION: {symbol}")

            place_market_order(fyers, symbol, qty, side)