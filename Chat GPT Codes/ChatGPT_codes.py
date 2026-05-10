# core/engine.py

```python
# ==========================================
# EVENT-DRIVEN TRADING ENGINE
# ==========================================

from core.events import (
    detect_cross,
    get_level_index,
    trigger_hit
)

from strategy.fib_strategy import (
    calculate_sl,
    calculate_trailing_sl
)

from broker.orders import (
    place_stop_buy,
    place_sl_order,
    modify_sl_order,
    cancel_order,
    close_position
)

from utils.logger import log, error_log
from utils.time_utils import is_market_open, is_eod_exit_time
from utils.state_logger import log_state


# ==========================================
# ENGINE
# ==========================================
class TradingEngine:

    # --------------------------------------
    # INIT
    # --------------------------------------
    def __init__(self, fyers, symbol, levels, state):

        self.fyers = fyers
        self.symbol = symbol
        self.levels = levels
        self.state = state

        log(f"{symbol} ENGINE INITIALIZED")

    # ======================================
    # MAIN TICK HANDLER
    # ======================================
    def on_tick(self, price):

        try:

            # ----------------------------------
            # MARKET HOURS CHECK
            # ----------------------------------
            if not is_market_open():
                return

            # ----------------------------------
            # EOD EXIT
            # ----------------------------------
            if is_eod_exit_time():

                if self.state.active_trade:
                    self.force_exit()

                return

            # ----------------------------------
            # PREVIOUS PRICE INIT
            # ----------------------------------
            if self.state.prev_price is None:
                self.state.prev_price = price
                return

            # ----------------------------------
            # FIND CURRENT LEVEL ZONE
            # ----------------------------------
            idx = get_level_index(price, self.levels)

            self.state.curr_index = idx

            lower = self.levels[idx]
            upper = self.levels[idx + 1]

            # ----------------------------------
            # ACTIVE TRADE MANAGEMENT
            # ----------------------------------
            if self.state.active_trade:

                self.manage_active_trade(price)

                self.state.prev_price = price
                return

            # ----------------------------------
            # ENTRY LOCK
            # ----------------------------------
            if self.state.entry_order_id:

                self.state.prev_price = price
                return

            # ==================================
            # FIRST TRADE LOGIC
            # ==================================
            if not self.state.first_trade_done:

                trigger = upper - self.state.sl_points

                if trigger_hit(price, trigger):

                    log(
                        f"{self.symbol} FIRST TRADE TRIGGER HIT | "
                        f"Trigger={trigger} | Upper={upper}"
                    )

                    self.place_entry_order(upper)

                    self.state.prev_price = price
                    return

            # ==================================
            # CONTINUATION BREAKOUT LOGIC
            # ==================================
            crossed = detect_cross(
                self.state.prev_price,
                price,
                upper
            )

            if crossed:

                log(
                    f"{self.symbol} BREAKOUT DETECTED | "
                    f"Upper={upper}"
                )

                self.place_entry_order(upper)

            # ----------------------------------
            # UPDATE PREVIOUS PRICE
            # ----------------------------------
            self.state.prev_price = price

        except Exception as e:
            error_log(f"{self.symbol} ON_TICK ERROR: {e}")

    # ======================================
    # PLACE ENTRY ORDER
    # ======================================
    def place_entry_order(self, trigger_price):

        try:

            res = place_stop_buy(
                self.fyers,
                self.symbol,
                self.state.default_qty,
                trigger_price
            )

            order_id = res.get("id")

            if not order_id:
                error_log(f"{self.symbol} ENTRY ORDER FAILED")
                return

            self.state.entry_order_id = order_id

            log(
                f"{self.symbol} ENTRY ORDER PLACED | "
                f"ID={order_id}"
            )

            log_state(self.state, "ENTRY_ORDER_PLACED")

        except Exception as e:
            error_log(f"{self.symbol} ENTRY ORDER ERROR: {e}")

    # ======================================
    # ORDER EVENT HANDLER
    # ======================================
    def handle_order_update(self, msg):

        try:

            if msg.get("symbol") != self.symbol:
                return

            status = msg.get("status")

            log(
                f"ORDER -> {self.symbol} | status={status}"
            )

            # ----------------------------------
            # REJECTED
            # ----------------------------------
            if status == 5:

                log(f"{self.symbol} ORDER REJECTED")

                self.state.entry_order_id = None

                log_state(self.state, "ORDER_REJECTED")

            # ----------------------------------
            # CANCELLED
            # ----------------------------------
            elif status == 1:

                log(f"{self.symbol} ORDER CANCELLED")

                self.state.entry_order_id = None

                log_state(self.state, "ORDER_CANCELLED")

            # ----------------------------------
            # OPEN / TRIGGER PENDING
            # ----------------------------------
            elif status in [4, 6]:

                log(
                    f"{self.symbol} ORDER ACTIVE | "
                    f"Status={status}"
                )

        except Exception as e:
            error_log(f"{self.symbol} ORDER EVENT ERROR: {e}")

    # ======================================
    # TRADE EVENT HANDLER
    # ======================================
    def handle_trade_update(self, msg):

        try:

            if msg.get("symbol") != self.symbol:
                return

            status = msg.get("status")
            side = msg.get("side")

            # ----------------------------------
            # ONLY FILLED TRADES
            # ----------------------------------
            if status != 2:
                return

            fill_price = float(
                msg.get("tradedPrice")
                or msg.get("avgPrice")
                or 0
            )

            qty = int(
                msg.get("filledQty")
                or msg.get("qty")
                or 0
            )

            if fill_price <= 0 or qty <= 0:

                error_log(
                    f"{self.symbol} INVALID TRADE DATA"
                )

                return

            # ==================================
            # BUY EXECUTION
            # ==================================
            if side == 1:

                # duplicate protection
                if self.state.active_trade:
                    return

                log(
                    f"{self.symbol} BUY EXECUTED @ {fill_price}"
                )

                # ------------------------------
                # ACTIVATE TRADE
                # ------------------------------
                sl_price = calculate_sl(
                    fill_price,
                    self.state.sl_points
                )

                self.state.set_active_trade(
                    fill_price,
                    sl_price,
                    qty
                )

                self.state.entry_order_id = None
                self.state.first_trade_done = True

                log_state(self.state, "TRADE_ACTIVATED")

                # ------------------------------
                # PLACE SL
                # ------------------------------
                sl_res = place_sl_order(
                    self.fyers,
                    self.symbol,
                    qty,
                    sl_price
                )

                sl_order_id = sl_res.get("id")

                if sl_order_id:

                    self.state.sl_order_id = sl_order_id

                    log(
                        f"{self.symbol} SL PLACED @ {sl_price}"
                    )

                    log_state(self.state, "SL_PLACED")

                else:

                    error_log(
                        f"{self.symbol} SL PLACEMENT FAILED"
                    )

            # ==================================
            # SELL EXECUTION (SL / EXIT)
            # ==================================
            elif side == -1:

                log(
                    f"{self.symbol} SELL EXECUTED @ {fill_price}"
                )

                # ----------------------------------
                # RESET TRADE
                # ----------------------------------
                self.state.reset_trade()

                log_state(self.state, "TRADE_EXITED")

        except Exception as e:
            error_log(f"{self.symbol} TRADE EVENT ERROR: {e}")

    # ======================================
    # POSITION EVENT HANDLER
    # ======================================
    def handle_position_update(self, msg):

        try:

            if msg.get("symbol") != self.symbol:
                return

            qty = msg.get("qty")

            log(
                f"POSITION -> {self.symbol} | qty={qty}"
            )

            # ----------------------------------
            # ONLY SYNCHRONIZATION
            # ----------------------------------
            # NO ORDER PLACEMENT HERE
            # NO SL PLACEMENT HERE
            # NO TRADE ACTIVATION HERE

            if qty == 0 and self.state.active_trade:

                log(
                    f"{self.symbol} POSITION CLOSED AT BROKER"
                )

                self.state.reset_trade()

                log_state(self.state, "BROKER_POSITION_CLOSED")

        except Exception as e:
            error_log(f"{self.symbol} POSITION EVENT ERROR: {e}")

    # ======================================
    # ACTIVE TRADE MANAGEMENT
    # ======================================
    def manage_active_trade(self, price):

        try:

            # ----------------------------------
            # SL HIT CHECK
            # ----------------------------------
            if price <= self.state.sl_price:

                log(
                    f"{self.symbol} SL HIT @ {price}"
                )

                self.force_exit()

                return

            # ----------------------------------
            # TRAILING SL
            # ----------------------------------
            new_sl = calculate_trailing_sl(
                self.state.entry_price,
                price,
                self.state.sl_price
            )

            if not new_sl:
                return

            if new_sl <= self.state.sl_price:
                return

            # ----------------------------------
            # MODIFY SL ORDER
            # ----------------------------------
            res = modify_sl_order(
                self.fyers,
                self.state.sl_order_id,
                new_sl
            )

            status = res.get("s")

            if status == "ok":

                self.state.update_sl(new_sl)

                log(
                    f"{self.symbol} TRAIL SL UPDATED -> {new_sl}"
                )

                log_state(self.state, "TRAIL_SL_UPDATED")

        except Exception as e:
            error_log(f"{self.symbol} TRADE MANAGEMENT ERROR: {e}")

    # ======================================
    # FORCE EXIT
    # ======================================
    def force_exit(self):

        try:

            log(f"{self.symbol} FORCE EXIT INITIATED")

            # ----------------------------------
            # CANCEL SL ORDER
            # ----------------------------------
            if self.state.sl_order_id:

                cancel_order(
                    self.fyers,
                    self.state.sl_order_id
                )

            # ----------------------------------
            # CLOSE POSITION
            # ----------------------------------
            close_position(
                self.fyers,
                self.symbol
            )

            # ----------------------------------
            # RESET STATE
            # ----------------------------------
            self.state.reset_trade()

            log_state(self.state, "FORCE_EXIT")

        except Exception as e:
            error_log(f"{self.symbol} FORCE EXIT ERROR: {e}")

```
