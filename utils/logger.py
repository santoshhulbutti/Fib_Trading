# ==========================================
# LOGGER (SYSTEM + TRADE + ERROR)
# ==========================================

import os
from datetime import datetime
from config.settings import LOG_PATH, ENABLE_LOGGING

# Ensure log directory exists
os.makedirs(LOG_PATH, exist_ok=True)


def _write(file_name, message):
    """
    Internal file writer
    """
    if not ENABLE_LOGGING:
        return

    file_path = os.path.join(LOG_PATH, file_name)

    with open(file_path, "a") as f:
        f.write(message + "\n")


def log(message):
    """
    General system log
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
    msg = f"[INFO] {timestamp} | {message}"

    print(msg)
    _write("system.log", msg)


def trade_log(message):
    """
    Trade-specific log
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
    msg = f"[TRADE] {timestamp} | {message}"

    print(msg)
    _write("trades.log", msg)


def error_log(message):
    """
    Error logging
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
    msg = f"[ERROR] {timestamp} | {message}"

    print(msg)
    _write("errors.log", msg)