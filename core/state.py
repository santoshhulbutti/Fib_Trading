# ==========================================
# TRADE STATE MANAGEMENT (FINAL - EVENT DRIVEN)
# ==========================================

class TradeState:
    def __init__(self, symbol):
        self.symbol = symbol

        # --------------------------------------
        # MARKET STATE
        # --------------------------------------
        self.prev_price = None
        self.curr_index = None

        # --------------------------------------
        # TRADE STATE
        # --------------------------------------
        self.active_trade = False
        self.entry_price = None
        self.sl_price = None

        # --------------------------------------
        # ORDER TRACKING
        # --------------------------------------
        self.entry_order_id = None   # Pending entry order
        self.sl_order_id = None      # SL order after fill

        # --------------------------------------
        # STRATEGY FLAGS
        # --------------------------------------
        self.first_trade_done = False

        # --------------------------------------
        # RISK TRACKING
        # --------------------------------------
        self.trades_today = 0

    # --------------------------------------
    # RESET TRADE AFTER EXIT
    # --------------------------------------
    def reset_trade(self):
        self.active_trade = False
        self.entry_price = None
        self.sl_price = None

        self.entry_order_id = None
        self.sl_order_id = None

    # --------------------------------------
    # SET ACTIVE TRADE (AFTER FILL)
    # --------------------------------------
    def set_active_trade(self, entry_price, sl_price):
        self.active_trade = True
        self.entry_price = entry_price
        self.sl_price = sl_price

        # Clear entry order (now filled)
        self.entry_order_id = None

        self.trades_today += 1

    # --------------------------------------
    # UPDATE SL (TRAILING)
    # --------------------------------------
    def update_sl(self, new_sl):
        if new_sl and new_sl > self.sl_price:
            self.sl_price = new_sl