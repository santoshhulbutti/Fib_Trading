# ==========================================
# ULTRA-FAST EVENT-DRIVEN ENGINE (FINAL)
# ==========================================

from core.state import TradeState
from core.events import (
    get_level_index,
    detect_cross,
    trigger_hit,
    sl_hit,
    calculate_trailing_sl
)

from strategy.fib_strategy import calculate_sl
from config.trading_params import SL_POINTS, TRAILING_RULES

from broker.orders import (
    place_stop_buy,
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
                modify_order(self.fyers, state.sl_order_id, new_sl, new_sl)
                log(f"{self.symbol} TRAIL SL → {new_sl}")

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

                if trigger_hit(price, trigger):

                    res = place_stop_buy(self.fyers, self.symbol, 1, upper)
                    state.entry_order_id = res.get("id")

                    log(f"{self.symbol} FIRST ORDER PLACED @ {upper}")

            # -------- SUBSEQUENT TRADES --------
            else:
                cross = detect_cross(state.prev_price, price, upper)

                if cross == "CROSS_UP":

                    res = place_stop_buy(self.fyers, self.symbol, 1, upper)
                    state.entry_order_id = res.get("id")

                    log(f"{self.symbol} BREAKOUT ORDER @ {upper}")

        # ----------------------------------
        # UPDATE PREVIOUS PRICE
        # ----------------------------------
        state.prev_price = price

    # --------------------------------------
    # 🔥 REAL EXECUTION (FROM TRADE WS)
    # --------------------------------------
    def handle_trade_update(self, msg):

        try:
            if msg.get("symbol") != self.symbol:
                return

            status = msg.get("status")

            # Only process FILLED trades
            if status != 2:
                return

            fill_price = float(msg.get("avgPrice", 0))
            filled_qty = msg.get("filledQty", 0)

            if fill_price == 0 or filled_qty == 0:
                log(f"{self.symbol} INVALID TRADE DATA → {msg}")
                return

            log(f"{self.symbol} TRADE FILLED @ {fill_price}")

            # Activate trade
            sl_price = calculate_sl(fill_price)

            self.state.set_active_trade(fill_price, sl_price, filled_qty)
            self.state.entry_order_id = None
            self.state.first_trade_done = True

            # Place SL immediately
            sl_res = place_sl_order(self.fyers, self.symbol, filled_qty, sl_price)
            self.state.sl_order_id = sl_res.get("id")

            log(f"{self.symbol} SL PLACED @ {sl_price}")

        except Exception as e:
            error_log(f"{self.symbol} TRADE UPDATE ERROR: {e}")

    # --------------------------------------
    # OPTIONAL: ORDER EVENTS (LOGGING)
    # --------------------------------------
    def handle_order_update(self, msg):
        log(f"{self.symbol} ORDER EVENT: {msg}")

    # --------------------------------------
    # EXIT TRADE
    # --------------------------------------
    def exit_trade(self):

        try:
            # Cancel SL first
            if self.state.sl_order_id:
                cancel_order(self.fyers, self.state.sl_order_id)

            # Clean exit via orders layer
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

        if self.state.active_trade:
            log(f"{self.symbol} EOD FORCE EXIT")
            self.exit_trade()
            self.state.reset_trade()