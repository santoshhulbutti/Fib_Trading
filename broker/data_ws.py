# ==========================================
# WEBSOCKET DATA FEED
# ==========================================

from fyers_apiv3.FyersWebsocket import data_ws
from utils.logger import log


def start_ws(access_token, symbols, on_message):

    def on_open():
        log("WebSocket Connected")
        ws.subscribe(symbols=symbols, data_type="symbolData")

    def on_error(msg):
        log(f"WS ERROR: {msg}")

    def on_close(msg):
        log("WebSocket Closed")

    ws = data_ws.FyersDataSocket(
        access_token=access_token,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        reconnect=True
    )

    ws.connect()