# ==========================================
# ORDER MANAGEMENT (FINAL - EVENT DRIVEN)
# ==========================================

from utils.logger import log, error_log


# ------------------------------------------
# PLACE STOP BUY ORDER
# ------------------------------------------
def place_stop_buy(fyers, symbol, qty, trigger_price):
    from config.trading_params import SL_POINTS
    try:
        data = {
            "symbol": symbol,
            "qty": qty,
            "type": 4,  # Stop Limit - Limit Order / SL-L ORDER
            "side": 1,  # BUY
            "productType": "INTRADAY",
            "limitPrice": trigger_price+0.1,
            "stopPrice": trigger_price,
            "validity": "DAY"
        }

        res = fyers.place_order(data)

        if res.get("s") =="ok":
            log(f"BUY ORDER SUBMIT SUCCESSFULLY: {res}")
            log(f"{symbol} STOP BUY ORDER: {res}")
            return res
        elif res.get("s") =="error":
            error_log(f"BUY ORDER SUBMIT ERROR: {res}")
            return res


        # NEED TO VERIFY ORDER SUCCESS OR NOT THEN LOG THE RESPONSE
        return res

    except Exception as e:
        error_log(f"{symbol} STOP BUY ERROR: {e}")
        return {}


# ------------------------------------------
# PLACE STOP SELL ORDER
# ------------------------------------------
# def place_stop_sell(fyers, symbol, qty, trigger_price):
#
#     try:
#         data = {
#             "symbol": symbol,
#             "qty": qty,
#             "type": 3,  # STOP LIMIT
#             "side": -1,  # SELL
#             "productType": "INTRADAY",
#             "limitPrice": trigger_price,
#             "stopPrice": trigger_price,
#             "validity": "DAY"
#         }
#
#         res = fyers.place_order(data)
#         log(f"{symbol} STOP BUY ORDER -> {res}")
#         return res
#
#     except Exception as e:
#         error_log(f"{symbol} STOP BUY ERROR: {e}")
#         return {}



# ------------------------------------------
# PLACE STOP LOSS ORDER (FOR LONG POSITION)
# ------------------------------------------
def place_sl_order(fyers, symbol, qty, sl_price):
    from config.trading_params import SL_POINTS

    try:
        data = {
            "symbol": symbol,
            "qty": qty,
            "type": 3,  # STOP LIMIT
            "side": -1,  # SELL
            "productType": "INTRADAY",
            "limitPrice": 0,#sl_price,
            "stopPrice": sl_price,
            "validity": "DAY"
        }

        res = fyers.place_order(data)
        log(f"{symbol} SL ORDER: {res}")
        return res

    except Exception as e:
        error_log(f"{symbol} SL ORDER ERROR: {e}")
        return {}


# ------------------------------------------
# MARKET ORDER (EXIT)
# ------------------------------------------
def place_market_order(fyers, symbol, qty, side):

    try:
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

        if res.get("s") =="ok":
            log(f"MARKET ORDER SUBMIT SUCCESSFULLY: {res}")
            log(f"{symbol} MARKET ORDER ({side}): {res}")
            return res
        elif res.get("s") =="error":
            error_log(f"MARKET ORDER SUBMIT ERROR: {res}")
            return res
        # log(f"{symbol} MARKET ORDER ({side}): {res}")
        return res

    except Exception as e:
        error_log(f"{symbol} MARKET ORDER ERROR: {e}")
        return {}


# ------------------------------------------
# CANCEL ORDER
# ------------------------------------------
def cancel_order(fyers, order_id):

    try:
        res = fyers.cancel_order({"id": order_id})
        log(f"CANCEL ORDER: {res}")
        return res

    except Exception as e:
        error_log(f"CANCEL ORDER ERROR: {e}")
        return {}


# ------------------------------------------
# MODIFY ORDER (TRAILING SL)
# ------------------------------------------
def modify_order(fyers, order_id, price, trigger, qty):

    try:
        data = {
            "id": order_id,
            "type": 3,
            "limitPrice": 0,
            "stopPrice": trigger,
            "qty": qty  # unchanged
        }

        res = fyers.modify_order(data)
        if res.get("s") =="ok":
            log(f"MODIFY ORDER: {res}")
            return res
        elif res.get("s") =="error":
            error_log(f"MODIFY ORDER ERROR: {res}")
            return res


    except Exception as e:
        error_log(f"MODIFY ORDER ERROR: {e}")
        return {}


# ------------------------------------------
# MODIFY ENTRY ORDER
# ------------------------------------------
def modify_entry_order(fyers, order_id, price, trigger, qty):

    try:
        data = {
            "id": order_id,
            "type": 4,
            "limitPrice": price,
            "stopPrice": trigger,
            "qty": qty  # unchanged
        }

        res = fyers.modify_order(data)
        if res.get("s") =="ok":
            log(f"MODIFY ENTRY ORDER: {res}")
            return res
        elif res.get("s") =="error":
            error_log(f"MODIFY ENTRY ORDER ERROR: {res}")
            return res


    except Exception as e:
        error_log(f"MODIFY ENTRY ORDER ERROR: {e}")
        return {}


# ------------------------------------------
# GET POSITIONS
# ------------------------------------------
def get_positions(fyers):

    try:
        res = fyers.positions()
        return res.get("netPositions", [])

    except Exception as e:
        error_log(f"GET POSITIONS ERROR: {e}")
        return []


# ------------------------------------------
# CLOSE POSITION (UTILITY)
# ------------------------------------------
def close_position(fyers, symbol):

    try:
        positions = get_positions(fyers)

        for pos in positions:
            if pos.get("symbol") == symbol and pos.get("qty") != 0:

                qty = abs(pos.get("qty"))
                side = "SELL" if pos.get("qty") > 0 else "BUY"

                log(f"{symbol} CLOSING POSITION | Qty={qty} | Side={side}")

                res = place_market_order(fyers, symbol, qty, side)
                if res.get("s") == "ok":
                    log(f"POSITION CLOSE ORDER SUBMIT SUCCESSFULLY: {res}")
                    log(f"{symbol} POSITION CLOSE ORDER ({side}): {res}")
                    return res
                elif res.get("s") == "error":
                    error_log(f"POSITION CLOSE ORDER SUBMIT ERROR: {res}")
                    return res
                return res

        log(f"{symbol} NO POSITION FOUND TO CLOSE")

    except Exception as e:
        error_log(f"{symbol} CLOSE POSITION ERROR: {e}")

# ------------------------------------------
# GET ORDERBOOK
# ------------------------------------------
def get_orderbook(fyers):

    try:
        res = fyers.orderbook()
        return res.get("orderBook", [])

    except Exception as e:
        error_log(f"ORDERBOOK ERROR: {e}")
        return []