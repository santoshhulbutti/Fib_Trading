# ==========================================
# WEBSOCKET DATA FEED (FINAL CORRECT VERSION)
# ==========================================

from fyers_apiv3.FyersWebsocket import data_ws
from fyers_apiv3.FyersWebsocket import order_ws
from utils.logger import log


def start_ws(access_token, symbols, on_message):

    # --------------------------------------
    # CALLBACKS
    # --------------------------------------
    def on_connect():
        log("WebSocket Connected")

        # Subscribe to symbols
        fyers.subscribe(
            symbols=symbols,
            data_type="symbolUpdate"
        )
        # fyers.keep_running()

    def on_close(message):
        log(f"WebSocket Closed: {message}")

    def on_error(message):
        log(f"WebSocket Error: {message}")

    def onmessage(msg):
        on_message(msg)

    # --------------------------------------
    # SOCKET INIT (IMPORTANT)
    # --------------------------------------
    fyers = data_ws.FyersDataSocket(
        access_token=access_token,
        log_path="",
        litemode=False,
        write_to_file=False,
        reconnect=True,
        on_connect=on_connect,
        on_close=on_close,
        on_error=on_error,
        on_message=onmessage,
        reconnect_retry=20
    )

    # --------------------------------------
    # CONNECT
    # --------------------------------------
    fyers.connect()