# ==========================================
# SYSTEM & BROKER SETTINGS (FINAL CLEAN)
# ==========================================

import os
from datetime import time


# ==========================================
# ENV HELPER (SAFE ACCESS)
# ==========================================
def get_env(key, required=True, default=None):
    value = os.getenv(key, default)

    if required and not value:
        raise ValueError(f"❌ Missing environment variable: {key}")

    return value


# ==========================================
# FYERS API CONFIG
# ==========================================
CLIENT_ID = get_env("FYERS_CLIENT_ID")
SECRET_KEY = get_env("FYERS_SECRET_KEY")
REDIRECT_URI = "https://www.google.com"


# ==========================================
# TRADING CONFIG
# ==========================================
CAPITAL = 100000
DEFAULT_QTY = 1


# ==========================================
# MARKET CONFIG
# ==========================================
UNDERLYING = "BSE:SENSEX-INDEX"


# ==========================================
# TIME SETTINGS (USE datetime.time)
# ==========================================
MARKET_START = time(9, 10)
MARKET_END = time(15, 30)
EOD_EXIT_TIME = time(15, 20)


# ==========================================
# SYSTEM CONFIG
# ==========================================
LOG_PATH = "logs/"
ENABLE_LOGGING = True


# ==========================================
# NETWORK / DEPLOYMENT
# ==========================================
STATIC_IP_REQUIRED = True