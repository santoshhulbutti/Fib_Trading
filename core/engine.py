# ==========================================
# ULTRA-FAST EVENT-DRIVEN ENGINE (FINAL)
# ==========================================

from core.state import TradeState
from core.events import (
    get_level_index,
    detect_cross,
    trigger_hit,
    # trigger_short_hit,
    sl_hit,
    calculate_trailing_sl
)

from strategy.fib_strategy import calculate_sl
from config.trading_params import SL_POINTS, TRAILING_RULES

from broker.orders import (
    place_stop_buy,
    # place_stop_sell,
    cancel_order,
    place_sl_order,
    modify_order,
    close_position
)

from utils.logger import log, error_log


class Engine:

    def __init__(self, fyers, symbol, levels):
        self.fyers = fyers
        self.symbol = symbol
        self.levels = levels
        self.state = TradeState(symbol)

    # --------------------------------------
    # MAIN TICK HANDLER (PRICE LOGIC ONLY)
    # --------------------------------------
    def on_tick(self, price):

        state = self.state

        # ----------------------------------
        # FIRST TICK INIT
        # ----------------------------------
        if state.prev_price is None:
            state.prev_price = price
            state.curr_index = get_level_index(price, self.levels)
            return

        # ----------------------------------
        # LEVEL DETECTION
        # ----------------------------------
        idx = get_level_index(price, self.levels, state.curr_index)
        state.curr_index = idx

        lower = self.levels[idx]
        upper = self.levels[idx + 1]

        # print (upper, lower)

        # ----------------------------------
        # SL HIT
        # ----------------------------------
        if state.active_trade and sl_hit(price, state.sl_price):
            log(f"{self.symbol} SL HIT")

            self.exit_trade()
            state.reset_trade()
            state.prev_price = price
            return

        # ----------------------------------
        # TRAILING SL
        # ----------------------------------
        if state.active_trade:
            new_sl = calculate_trailing_sl(
                state.entry_price,
                price,
                TRAILING_RULES
            )

            if new_sl and new_sl > state.sl_price:
                state.update_sl(new_sl)
                if state.sl_order_id:
                    modify_order(self.fyers, state.sl_order_id, new_sl, new_sl)
                    log(f"{self.symbol} TRAIL SL -> {new_sl}")

        # ----------------------------------
        # 🚨 ENTRY LOCK (RECOVERY SAFE)
        # ----------------------------------
        if state.active_trade or state.entry_order_id:
            state.prev_price = price
            return

        # ----------------------------------
        # ENTRY LOGIC (NO EXECUTION HERE)
        # ----------------------------------
        if not state.active_trade and not state.entry_order_id:

            # -------- FIRST TRADE --------
            if not state.first_trade_done:

                trigger = upper - SL_POINTS
                # trigger_s = lower + SL_POINTS

                if trigger_hit(price, trigger):

                    res = place_stop_buy(self.fyers, self.symbol, 1, upper)
                    if res.get('s')=='ok':
                        state.entry_order_id = res.get("id")
                        log(f"{self.symbol} FIRST LONG ORDER PLACED @ {upper}")
                    if res.get('s') =='error':
                        log(f"{self.symbol} FIRST LONG ORDER error {res.get('message')}")

                # if trigger_short_hit(price, trigger_s):
                #
                #     res = place_stop_sell(self.fyers, self.symbol, 1, upper)
                #     state.entry_order_id = res.get("id")
                #
                #     log(f"{self.symbol} FIRST SHORT ORDER PLACED @ {upper}")

            # -------- SUBSEQUENT TRADES --------
            else:
                cross = detect_cross(state.prev_price, price, upper)

                if cross == "CROSS_UP":

                    res = place_stop_buy(self.fyers, self.symbol, 1, upper)
                    state.entry_order_id = res.get("id")

                    log(f"{self.symbol} BREAKOUT ORDER @ {upper}")

                # if cross == "CROSS_DOWN":
                #
                #     res = place_stop_sell(self.fyers, self.symbol, 1, lower)
                #     state.entry_order_id = res.get("id")
                #
                #     log(f"{self.symbol} BREAKDOWN ORDER @ {lower}")

        # ----------------------------------
        # UPDATE PREVIOUS PRICE
        # ----------------------------------
        state.prev_price = price

    # --------------------------------------
    # REAL EXECUTION (FROM TRADE WS)
    # --------------------------------------
    def handle_trade_update(self, msg):

        log(f"{self.symbol} HANDLE TRADE EVENT: {msg}")

        try:
            if msg.get('trades').get("symbol") != self.symbol:
                log("handle_trade_update - Symbol mismatch")
                return

            filled_qty = msg.get('trades').get("tradedQty", 0)
            status = msg.get("s")

            # Partial fill (status != 2)
            if filled_qty > 0 and status != "ok":
                log(f"{self.symbol} PARTIAL FILL -> {filled_qty} OR TRADE ERROR. CHECK LOG.")
                return

            # Only process FILLED trades
            if status != "ok":
                return

            # fill_price = float(msg.get("avgPrice", 0))
            fill_price = float(msg.get('trades').get("tradePrice") or 0)
            filled_qty = msg.get('trades').get("tradedQty", 0)

            if fill_price == 0 or filled_qty == 0:
                log(f"{self.symbol} INVALID TRADE DATA -> {msg}")
                return

            log(f"{self.symbol} TRADE FILLED @ {fill_price} FOR QTY: {filled_qty}")

            # Activate trade
            sl_price = calculate_sl(fill_price)

            self.state.set_active_trade(fill_price, sl_price, filled_qty)
            self.state.entry_order_id = None
            self.state.first_trade_done = True

            # Place SL immediately
            sl_res = place_sl_order(self.fyers, self.symbol, filled_qty, sl_price)
            log(f"SL ORDER RESPONSE : {sl_res}")
            self.state.sl_order_id = sl_res.get("id")

            log(f"{self.symbol} SL PLACED @ {sl_price}")

        except Exception as e:
            error_log(f"{self.symbol} TRADE UPDATE ERROR: {e}")

    # --------------------------------------
    # OPTIONAL: ORDER EVENTS (LOGGING)
    # --------------------------------------
    def handle_order_update(self, msg):
        log(f"{self.symbol} HANDLE ORDER EVENT: {msg}")

        # ----------------------------------
        # FILLED ORDER
        # ----------------------------------
        # if msg.get("status") == 2:
        #
        #     # Avoid duplicate processing
        #     if self.state.active_trade:
        #         return
        #
        #     fill_price = float(
        #         msg.get("tradedPrice")
        #         # or msg.get("avgPrice")
        #         or 0
        #     )
        #
        #     qty = int(
        #         msg.get("filledQty") or
        #         msg.get("qty") or 0
        #     )
        #
        #     if fill_price <= 0 or qty <= 0:
        #         log(f"{self.symbol} INVALID FILL DATA")
        #         return
        #
        #     log(f"{self.symbol} ORDER FILLED @ {fill_price}")
        #
        #     # ----------------------------------
        #     # ACTIVATE TRADE
        #     # ----------------------------------
        #     sl_price = calculate_sl(fill_price)
        #
        #     self.state.set_active_trade(fill_price, sl_price, qty)
        #
        #     self.state.entry_order_id = None
        #     self.state.first_trade_done = True
        #
        #     # ----------------------------------
        #     # PLACE SL
        #     # ----------------------------------
        #     sl_res = place_sl_order(
        #         self.fyers,
        #         self.symbol,
        #         qty,
        #         sl_price
        #     )
        #
        #     log(f"SL ORDER PLACED, ORDER RAW DATA: {sl_res}")
        #
        #     self.state.sl_order_id = sl_res.get("orders").get("id")
        #
        #     log(f"{self.symbol} SL PLACED @ {sl_price} WITH ORDER ID :{self.state.sl_order_id}")


    # --------------------------------------
    # POSITION UPDATE (CRITICAL FOR SYNC)
    # --------------------------------------
    def handle_position_update(self, msg):
        log(f"{self.symbol} HANDLE POSITION EVENT: {msg}")

        try:
            if msg.get("symbol") != self.symbol:
                return

            qty = msg.get("qty", 0)

            # ----------------------------------
            # POSITION CLOSED
            # ----------------------------------
            if qty == 0:

                if self.state.active_trade:
                    log(f"{self.symbol} POSITION CLOSED (BROKER)")

                    self.state.reset_trade()

                return

            # ----------------------------------
            # POSITION EXISTS
            # ----------------------------------
            entry_price = float(msg.get("avgPrice", 0))

            if entry_price == 0:
                return

            # If engine missed trade (reconnect case)
            if not self.state.active_trade:
                log(f"{self.symbol} POSITION RECOVERED FROM WS @ {entry_price}")

                sl_price = calculate_sl(entry_price)

                self.state.set_active_trade(entry_price, sl_price, abs(qty))

        except Exception as e:
            error_log(f"{self.symbol} POSITION UPDATE ERROR: {e}")

    # --------------------------------------
    # EXIT TRADE
    # --------------------------------------
    def exit_trade(self):
        log(f"{self.symbol} EXIT TRADE EVENT")

        try:
            # Cancel SL first
            if self.state.sl_order_id:
                cancel_order(self.fyers, self.state.sl_order_id)

            # Clean exit via orders layer
            log(f"{self.symbol} EXIT INITIATED")
            close_position(self.fyers, self.symbol)

            # positions = get_positions(self.fyers)
            #
            # for pos in positions:
            #     if pos["symbol"] == self.symbol and pos["qty"] != 0:
            #         qty = abs(pos["qty"])
            #         side = "SELL" if pos["qty"] > 0 else "BUY"
            #
            #         log(f"{self.symbol} EXIT | Qty: {qty} | Side: {side}")
            #
            #         place_market_order(self.fyers, self.symbol, qty, side)
            #         return
            #
            # log(f"{self.symbol} NO POSITION FOUND")

        except Exception as e:
            error_log(f"{self.symbol} EXIT ERROR: {e}")

    # --------------------------------------
    # FORCE EXIT (EOD)
    # --------------------------------------
    def force_exit(self):
        log(f"{self.symbol} FORCED EXIT EVENT")

        if self.state.active_trade:
            log(f"{self.symbol} EOD FORCE EXIT")
            self.exit_trade()
            self.state.reset_trade()