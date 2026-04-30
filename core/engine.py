# ==========================================
# ULTRA-FAST EVENT-DRIVEN ENGINE
# ==========================================

from core.state import TradeState
from core.events import (
    get_level_index,
    detect_cross,
    trigger_hit,
    sl_hit,
    calculate_trailing_sl
)

from config.trading_params import SL_POINTS, TRAILING_RULES
from broker.orders import (
    place_stop_buy,
    cancel_order,
    place_sl_order,
    modify_order,
    get_positions,
    place_market_order
)

from utils.logger import log, error_log


class Engine:

    def __init__(self, fyers, symbol, levels):
        self.fyers = fyers
        self.symbol = symbol
        self.levels = levels

        self.state = TradeState(symbol)

    # --------------------------------------
    # MAIN TICK HANDLER
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
        # ENTRY LOGIC
        # ----------------------------------
        if not state.active_trade:

            # -------- FIRST TRADE --------
            if not state.first_trade_done:

                trigger = upper - SL_POINTS

                if trigger_hit(price, trigger):

                    if state.pending_order_id:
                        cancel_order(self.fyers, state.pending_order_id)

                    res = place_stop_buy(self.fyers, self.symbol, 1, upper)
                    state.pending_order_id = res.get("id")

                    log(f"{self.symbol} NEW STOP BUY @ {upper}")

            # -------- SUBSEQUENT TRADES --------
            else:
                cross = detect_cross(state.prev_price, price, upper)

                if cross == "CROSS_UP":
                    res = place_stop_buy(self.fyers, self.symbol, 1, upper)
                    state.pending_order_id = res.get("id")

                    log(f"{self.symbol} BREAKOUT BUY @ {upper}")

        # ----------------------------------
        # ORDER EXECUTION (SIMPLIFIED)
        # ----------------------------------
        # NOTE: Replace with real order status check later

        if state.pending_order_id and price >= upper:

            log(f"{self.symbol} EXECUTED @ {upper}")

            sl_price = upper - SL_POINTS

            state.set_active_trade(upper, sl_price)
            state.first_trade_done = True

            sl_res = place_sl_order(self.fyers, self.symbol, 1, sl_price)
            state.sl_order_id = sl_res.get("id")

        # ----------------------------------
        # UPDATE PREVIOUS PRICE
        # ----------------------------------
        state.prev_price = price

    # --------------------------------------
    # EXIT TRADE
    # --------------------------------------
    def exit_trade(self):
        try:
            positions = get_positions(self.fyers)

            for pos in positions:
                if pos["symbol"] == self.symbol and pos["qty"] != 0:

                    qty = abs(pos["qty"])

                    # Determine exit side
                    if pos["qty"] > 0:
                        exit_side = "SELL"
                    else:
                        exit_side = "BUY"

                    log(f"{self.symbol} EXITING POSITION | Qty: {qty} | Side: {exit_side}")

                    # Place market exit
                    res = place_market_order(self.fyers, self.symbol, qty, exit_side)

                    log(f"{self.symbol} EXIT ORDER RESPONSE: {res}")

                    return

            log(f"{self.symbol} NO OPEN POSITION FOUND")

        except Exception as e:
            error_log(f"{self.symbol} EXIT ERROR: {e}")

    # --------------------------------------
    # FORCE EXIT (EOD)
    # --------------------------------------
    def force_exit(self):

        if self.state.active_trade:
            log(f"{self.symbol} EOD EXIT")
            self.exit_trade()
            self.state.reset_trade()