# ==========================================
# ORDER + TRADE WEBSOCKET (FINAL)
# ==========================================

from fyers_apiv3.FyersWebsocket import order_ws
from utils.logger import log, error_log
from config.settings import CLIENT_ID, SECRET_KEY, REDIRECT_URI

import time


def start_order_ws(access_token, engine_router, on_reconnect):


    # --------------------------------------
    # INTERNAL STATE (FOR RECONNECT CONTROL)
    # --------------------------------------
    last_resync_time = {"ts": 0}

    RESYNC_COOLDOWN = 3  # seconds (avoid multiple rapid resyncs)

    # --------------------------------------
    # SAFE RESYNC TRIGGER
    # --------------------------------------
    def trigger_resync():

        try:
            now = time.time()

            # Prevent duplicate resync calls
            if now - last_resync_time["ts"] < RESYNC_COOLDOWN:
                log("RESYNC SKIPPED (cooldown)")
                return

            last_resync_time["ts"] = now

            log("WS RECONNECTED -> TRIGGERING FULL RESYNC")

            on_reconnect()

            log("RESYNC COMPLETE")

        except Exception as e:
            error_log(f"RESYNC ERROR: {e}")

    # --------------------------------------
    # TRADE UPDATE (MOST IMPORTANT)
    # --------------------------------------
    def on_trade(msg):
        try:
            log(f"TRADE -> {msg.get('symbol')} | status={msg.get('status')}")

            # Route to engine
            engine_router("TRADE", msg)

        except Exception as e:
            error_log(f"TRADE WS ERROR: {e}")

    # --------------------------------------
    # ORDER UPDATE (SECONDARY)
    # --------------------------------------
    def on_order(msg):
        try:
            log(f"ORDER -> {msg.get('symbol')} | status={msg.get('status')}")

            engine_router("ORDER", msg)

        except Exception as e:
            error_log(f"ORDER WS ERROR: {e}")

    # --------------------------------------
    # POSITION UPDATE (OPTIONAL)
    # --------------------------------------
    def on_position(msg):
        try:
            log(f"POSITION -> {msg.get('symbol')} | qty={msg.get('qty')}")

            engine_router("POSITION", msg)

        except Exception as e:
            error_log(f"POSITION WS ERROR: {e}")

    # --------------------------------------
    # GENERAL EVENTS (OPTIONAL)
    # --------------------------------------
    def on_general(msg):
        log(f"GENERAL UPDATE -> {msg}")

    # --------------------------------------
    # CONNECT CALLBACK
    # --------------------------------------
    def on_connect():
        try:
            log("ORDER WS CONNECTED")

            # Subscribe to all streams
            fyers.subscribe(
                data_type="OnOrders,OnTrades,OnPositions,OnGeneral"
            )

            # CRITICAL: RESYNC STATE
            trigger_resync()

            # Keep socket alive
            fyers.keep_running()

        except Exception as e:
            error_log(f"CONNECT ERROR: {e}")

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
        reconnect=True,
        reconnect_retry=10
    )

    # --------------------------------------
    # CONNECT
    # --------------------------------------
    fyers.connect()