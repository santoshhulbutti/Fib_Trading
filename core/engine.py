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

from strategy.fib_strategy import calculate_sl
from config.trading_params import SL_POINTS, TRAILING_RULES

from broker.orders import (
    place_stop_buy,
    # place_stop_sell,
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
                    # state.pending_order_id = res.get("id")
                    state.entry_order_id = res.get("id")
                    state.entry_order_filled = False

                    log(f"{self.symbol} FIRST TRADE ORDER @ {upper}")

            # -------- SUBSEQUENT TRADES --------
            else:
                cross = detect_cross(state.prev_price, price, upper)

                if cross == "CROSS_UP":
                    res = place_stop_buy(self.fyers, self.symbol, 1, upper)
                    # state.pending_order_id = res.get("id")
                    state.entry_order_id = res.get("id")
                    state.entry_order_filled = False

                    log(f"{self.symbol} BREAKOUT ORDER @ {upper}")

                ####        TEST CODE BLOCK - start
                # if cross == "CROSS_DOWN":
                #     res = place_stop_sell(self.fyers, self.symbol, 1, lower)
                #     state.pending_order_id = res.get("id")
                #
                #     log(f"{self.symbol} BREAKDOWN ORDER @ {upper}")
                ####        TEST CODE BLOCK - end

        # ----------------------------------
        # ORDER EXECUTION (SIMPLIFIED)
        # ----------------------------------
        # NOTE: Replace with real order status check later

        # if state.pending_order_id and price >= upper:
        #
        #     log(f"{self.symbol} EXECUTED @ {upper}")
        #
        #     sl_price = calculate_sl(upper)
        #
        #     state.set_active_trade(upper, sl_price)
        #     state.first_trade_done = True
        #
        #     sl_res = place_sl_order(self.fyers, self.symbol, 1, sl_price)
        #     state.sl_order_id = sl_res.get("id")

        # ----------------------------------
        # CHECK ENTRY ORDER EXECUTION
        # ----------------------------------
        if state.entry_order_id and not state.entry_order_filled:

            from broker.orders import get_order_by_id

            order = get_order_by_id(self.fyers, state.entry_order_id)

            if not order:
                # Order not found yet (API delay / transient)
                return

            # if order:

            status = order.get("status")
            # avg_price = order.get("avgPrice")

            # 2 = FILLED
            if status == 2:

                avg_price = order.get("avgPrice")
                filled_qty = order.get("filledQty", 0)

                # 🔴 Safety check (VERY IMPORTANT)
                if avg_price is None or filled_qty == 0:
                    log(f"{self.symbol} ERROR: Filled order but avgPrice/filledQty missing → {order}")
                    return

                fill_price = float(avg_price)
                log(f"{self.symbol} ORDER FILLED @ {fill_price} | Qty: {filled_qty}")

                # log(f"{self.symbol} ORDER FILLED @ {fill_price}")

                # Activate trade
                sl_price = calculate_sl(fill_price)

                state.set_active_trade(fill_price, sl_price)
                state.entry_order_filled = True
                state.first_trade_done = True
                state.entry_order_id = None  # clear pending order

                # ----------------------------------
                # PLACE SL ORDER AFTER CONFIRMATION
                # ----------------------------------
                sl_res = place_sl_order(self.fyers, self.symbol, filled_qty, sl_price)

                state.sl_order_id = sl_res.get("id")

                log(f"{self.symbol} SL PLACED @ {sl_price}")

                # ----------------------------------
                # CASE 2: ORDER REJECTED
                # ----------------------------------
            elif status == 5:  # REJECTED

                log(f"{self.symbol} ORDER REJECTED → {order}")

                state.entry_order_id = None
                state.entry_order_filled = False

                # ----------------------------------
                # CASE 3: ORDER CANCELLED
                # ----------------------------------
            elif status == 6:  # CANCELLED

                log(f"{self.symbol} ORDER CANCELLED")

                state.entry_order_id = None
                state.entry_order_filled = False

                # ----------------------------------
                # CASE 4: STILL PENDING
                # ----------------------------------
            else:
                # status = 1 (PLACED) or others
                # Do nothing → keep waiting
                pass

        # ----------------------------------
        # UPDATE PREVIOUS PRICE
        # ----------------------------------
        state.prev_price = price

    # --------------------------------------
    # EXIT TRADE
    # --------------------------------------
    def exit_trade(self):

        try:
            # Cancel SL first
            if self.state.sl_order_id:
                cancel_order(self.fyers, self.state.sl_order_id)

            positions = get_positions(self.fyers)

            for pos in positions:
                if pos["symbol"] == self.symbol and pos["qty"] != 0:
                    qty = abs(pos["qty"])
                    side = "SELL" if pos["qty"] > 0 else "BUY"

                    log(f"{self.symbol} EXIT | Qty: {qty} | Side: {side}")

                    place_market_order(self.fyers, self.symbol, qty, side)
                    return

            log(f"{self.symbol} NO POSITION FOUND")

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