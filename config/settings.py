# ==========================================
# SYSTEM & BROKER SETTINGS
# ==========================================
import os

# -------- FYERS API --------
# def get_env(key):
#     value = os.getenv(key)
#     if not value:
#         raise ValueError(f"Missing environment variable: {key}")
#     else:
#         print("\n🔐 KEY ",key," -", value)
#     return value

CLIENT_ID = os.getenv("FYERS_CLIENT_ID")
SECRET_KEY = os.getenv("FYERS_SECRET_KEY")
REDIRECT_URI = "https://www.google.com"

# -------- TRADING --------
CAPITAL = 100000          # total capital
DEFAULT_QTY = 1           # start small (change later)

# -------- MARKET --------
UNDERLYING = "BSE:SENSEX-INDEX"

# -------- TIME SETTINGS --------
MARKET_START = "09:15"
MARKET_END = "15:30"
EOD_EXIT_TIME = "15:20"

# -------- SYSTEM --------
LOG_PATH = "logs/"
ENABLE_LOGGING = True

# -------- AWS / NETWORK --------
STATIC_IP_REQUIRED = True   # FYERS API compliance