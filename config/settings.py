# ==========================================
# SYSTEM & BROKER SETTINGS
# ==========================================

# -------- FYERS API --------
CLIENT_ID = "TIA57SU3G1-200"
SECRET_KEY = "nNUf3zJTDFcquIJb"
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