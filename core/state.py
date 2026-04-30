# ==========================================
# TRADE STATE MANAGEMENT
# ==========================================

class TradeState:
    def __init__(self, symbol):
        self.symbol = symbol

        # Market state
        self.prev_price = None
        self.curr_index = None

        # Trade state
        self.active_trade = False
        self.entry_price = None
        self.sl_price = None

        # Order state
        self.pending_order_id = None
        self.sl_order_id = None

        # Strategy flags
        self.first_trade_done = False

        # Risk tracking
        self.trades_today = 0

    # --------------------------------------
    # RESET TRADE AFTER EXIT
    # --------------------------------------
    def reset_trade(self):
        self.active_trade = False
        self.entry_price = None
        self.sl_price = None
        self.pending_order_id = None
        self.sl_order_id = None

    # --------------------------------------
    # SET ACTIVE TRADE
    # --------------------------------------
    def set_active_trade(self, entry_price, sl_price):
        self.active_trade = True
        self.entry_price = entry_price
        self.sl_price = sl_price
        self.pending_order_id = None
        self.trades_today += 1

    # --------------------------------------
    # UPDATE SL
    # --------------------------------------
    def update_sl(self, new_sl):
        if new_sl and new_sl > self.sl_price:
            self.sl_price = new_sl