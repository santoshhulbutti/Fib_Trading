# ==========================================
# ORDER + TRADE WEBSOCKET (FINAL)
# ==========================================

from fyers_apiv3.FyersWebsocket import order_ws
from utils.logger import log, error_log


def start_order_ws(access_token, engine_router):

    # --------------------------------------
    # TRADE UPDATE (MOST IMPORTANT)
    # --------------------------------------
    def on_trade(msg):
        try:
            log(f"TRADE UPDATE → {msg}")

            # Route to engine
            engine_router("TRADE", msg)

        except Exception as e:
            error_log(f"TRADE WS ERROR: {e}")

    # --------------------------------------
    # ORDER UPDATE (SECONDARY)
    # --------------------------------------
    def on_order(msg):
        try:
            log(f"ORDER UPDATE → {msg}")

            engine_router("ORDER", msg)

        except Exception as e:
            error_log(f"ORDER WS ERROR: {e}")

    # --------------------------------------
    # POSITION UPDATE (OPTIONAL)
    # --------------------------------------
    def on_position(msg):
        log(f"POSITION UPDATE → {msg}")

    # --------------------------------------
    # GENERAL EVENTS (OPTIONAL)
    # --------------------------------------
    def on_general(msg):
        log(f"GENERAL UPDATE → {msg}")

    # --------------------------------------
    # CONNECT CALLBACK
    # --------------------------------------
    def on_connect():
        log("ORDER WS CONNECTED")

        # Subscribe to all relevant streams
        fyers.subscribe(
            data_type="OnOrders,OnTrades,OnPositions,OnGeneral"
        )

        # Keep connection alive
        fyers.keep_running()

    # --------------------------------------
    # ERROR HANDLING
    # --------------------------------------
    def on_error(msg):
        error_log(f"ORDER WS ERROR: {msg}")

    def on_close(msg):
        log(f"ORDER WS CLOSED: {msg}")

    # --------------------------------------
    # SOCKET INIT
    # --------------------------------------
    fyers = order_ws.FyersOrderSocket(
        access_token=access_token,
        write_to_file=False,
        log_path="",
        on_connect=on_connect,
        on_close=on_close,
        on_error=on_error,
        on_general=on_general,
        on_orders=on_order,
        on_positions=on_position,
        on_trades=on_trade,
        reconnect=True
    )

    # --------------------------------------
    # CONNECT
    # --------------------------------------
    fyers.connect()