# Integration & Deployment: System Operations

## 🚀 System Setup & Configuration

### Prerequisites

1. **Fyers Trading Account**
   - Live funds account or paper trading
   - API access enabled
   - OAuth credentials obtained

2. **Python Environment**
   - Python 3.11 or higher
   - pip package manager
   - Virtual environment (recommended)

3. **System Requirements**
   - Windows 10+, Linux, or macOS
   - 500MB disk space (logs)
   - Stable internet (broadband recommended for trading)
   - Timezone: IST (05:30 UTC)

---

## 📦 Installation

### Step 1: Clone/Download Repository

```bash
cd D:\Trade Automation\Fib_Trading
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies Breakdown:**
```
fyers-apiv3==3.0.9              # Broker API
websocket-client==1.8.0         # WebSocket support
pandas==2.2.2                   # Data handling
numpy==1.26.4                   # Numerical operations
python-dateutil==2.9.0.post0    # Date utilities
loguru==0.7.2                   # Advanced logging (optional)
pytest==8.2.2                   # Testing (optional)
```

### Step 4: Verify Installation

```bash
python -m pytest tests/ -v
```

Expected output:
```
tests/test_strategy.py::test_fib_levels PASSED
tests/test_engine.py::test_on_tick PASSED
...
```

---

## 🔐 Configuration: Environment Variables

### Setting API Credentials

**Windows (PowerShell):**
```powershell
$env:FYERS_CLIENT_ID = "your_client_id_here"
$env:FYERS_SECRET_KEY = "your_secret_key_here"

# Verify
echo $env:FYERS_CLIENT_ID
```

**Windows (Permanent - System Variables):**
```
Control Panel → System → Advanced System Settings
→ Environment Variables → New
FYERS_CLIENT_ID = your_client_id
FYERS_SECRET_KEY = your_secret_key
```

**Linux/macOS:**
```bash
export FYERS_CLIENT_ID="your_client_id_here"
export FYERS_SECRET_KEY="your_secret_key_here"

# Verify
echo $FYERS_CLIENT_ID

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export FYERS_CLIENT_ID="your_client_id"' >> ~/.bashrc
source ~/.bashrc
```

**Alternative: Environment File (Python)**
```python
# Create .env file in project root
FYERS_CLIENT_ID=your_client_id
FYERS_SECRET_KEY=your_secret_key

# Then in Python code
from dotenv import load_dotenv
load_dotenv()
```

### Configuration Files

**`config/settings.py`:**
- Reads credentials from environment
- Sets log paths
- Configures market settings
- Raise error if credentials missing

**`config/trading_params.py`:**
- Mode switch: test_mode = True/False
- Strategy parameters (SL, trailing, limits)
- Risk controls

**`config/symbols.py`:**
- Option symbol generation
- Expiry calculation logic

---

## 🎯 Mode Switching: Test vs Live

### Test Mode (Safest for Learning)

**Configuration:**
```python
# main.py line 54
test_mode = True

# config/trading_params.py line 8
test_mode = True
```

**What Changes:**
```
Symbol: NSE:ADANIPORTS-EQ (equity, not options)
SL_POINTS: 10 (small)
Trailing SL: Fast ramps {5: 2, 6: 3, ...}
Max daily trades: 50
Max daily loss: ₹1000
```

**Use Case:**
- Learning the system
- Testing strategy logic
- Debugging issues
- Fast iteration (ticks are faster)

**Risk:**
- Low (equity testing, small SL)

**Steps:**
```python
1. Set test_mode = True in both locations
2. Run: python main.py
3. Monitor: logs/system.log, logs/trades.log
```

---

### Live Mode (Production Trading)

**Configuration:**
```python
# main.py line 54
test_mode = False

# config/trading_params.py line 8
test_mode = False
```

**What Changes:**
```
Symbol: BSE:SENSEX options (calls & puts)
SL_POINTS: 25 (realistic)
Trailing SL: Gradual {100: 30, 200: 50, ...}
Max daily trades: 10
Max daily loss: ₹6000
```

**Use Case:**
- Live trading with real capital
- Institutional-grade strategy
- Small account management

**Risk:**
- Medium (options trading, real money)

**Pre-Flight Checklist:**
```
[ ] Tested in paper trading first
[ ] Verified symbol generation (expiry dates)
[ ] Confirmed SL execution works
[ ] Tested reconnection scenarios
[ ] Prepared logs directory
[ ] Set alert thresholds
[ ] Reviewed daily loss limits
[ ] Started with 1 lot only
```

**Steps:**
```python
1. ✅ Complete pre-flight checklist
2. Set test_mode = False in both locations
3. Run: python main.py
4. Monitor closely for 2-3 days
5. Scale if performance is consistent
```

---

## ▶️ Running the System

### Method 1: Direct Execution

```bash
python main.py
```

**Output (First 30 seconds):**
```
[INFO] 2026-05-10 09:14:30:123456 | SYSTEM STARTING...
[INFO] 2026-05-10 09:14:31:234567 | AUTHENTICATION STARTED...

LOGIN URL:
https://api.fyers.in/validate-token?token=...

ENTER AUTHENTICATION CODE: [PASTE AUTH CODE HERE]

[INFO] 2026-05-10 09:14:45:345678 | AUTHENTICATION SUCCESSFUL...
[INFO] 2026-05-10 09:14:46:456789 | FYERS MODEL CREATED...
[INFO] 2026-05-10 09:14:47:567890 | Fetching OHLC...
[INFO] 2026-05-10 09:14:50:678901 | Levels generated: [2700.00, 2776.40, ...]
[INFO] 2026-05-10 09:14:51:789012 | ENGINE INSTANCE CREATION COMPLETE...
[INFO] 2026-05-10 09:14:52:890123 | INITIAL RECOVERY ENGINE COMPLETED
[INFO] 2026-05-10 09:14:53:901234 | STARTING WEBSOCKETS...
[INFO] 2026-05-10 09:15:00:012345 | DATA WEB SOCKET CONNECTED
[INFO] 2026-05-10 09:15:01:123456 | ORDER WEB SOCKET CONNECTED
```

**Alive Indicators:**
- No error logs
- WebSocket connected messages
- Continuous price feeds in logs

### Method 2: Background Process (Advanced)

**Windows (PowerShell):**
```powershell
$job = Start-Job -ScriptBlock { cd D:\Trade Automation\Fib_Trading; python main.py }
Get-Job -Id $job.Id  # Check status
Stop-Job -Id $job.Id # Stop when done
```

**Linux/macOS:**
```bash
nohup python main.py > fib_trading.log 2>&1 &
# Check: ps aux | grep main.py
# Stop: kill <PID>
```

### Method 3: Scheduled Start (Daily Auto-Run)

**Windows Task Scheduler:**
```
1. Task Scheduler → Create Basic Task
2. Name: Fib Trading Bot
3. Trigger: Daily at 09:14 AM
4. Action: Start Python
   Program: C:\Users\YourUser\AppData\Local\Programs\Python\Python311\python.exe
   Arguments: D:\Trade Automation\Fib_Trading\main.py
5. Conditions: Wake computer if asleep
6. Settings: Allow task to be queued
```

**Linux Cron:**
```bash
# Edit crontab
crontab -e

# Add line (9:14 AM IST = UTC 03:44)
14 09 * * 1-5 cd /path/to/Fib_Trading && python main.py >> trading.log 2>&1

# (Adjust based on your timezone)
```

---

## 🔌 Broker Integration Details

### Fyers API Integration

**Authentication Flow:**

```
1. OAuth2 Authorization
   - User runs: python main.py
   - Prints: Login URL
   - User visits URL, gets auth code
   - Pastes auth code when prompted
   
2. Token Exchange
   - System exchanges code for access token
   - Access token stored in memory (session)
   - Token typically valid for 1 year
   
3. API Calls
   - All subsequent calls use this token
   - Example: fyers.positions() uses token
```

**Token Lifecycle:**
```
Token Lifetime: ~1 year (or until logout)
Stored: In-memory only (FyersModel object)
On Restart: New token required (manual re-entry)
Refresh: Future enhancement (implement token refresh)
```

### WebSocket Subscriptions

**Data WebSocket (Price Feed):**
```python
# Subscribes to: SymbolUpdate
# Data Type: Real-time LTP, bid/ask, volume
# Update Frequency: Every 1-5 seconds (depends on volume)
# Symbols: All trading symbols

# Callback: on_message(tick)
# Format: {symbol, ltp, bid, ask, volume, oi, ...}
```

**Order WebSocket (Execution Feed):**
```python
# Subscribes to: Orders, Trades, Positions
# Events:
#   - Order update: Status change (pending → executed → rejected)
#   - Trade event: Execution details (price, qty, time)
#   - Position update: Quantity change

# Callbacks: on_order(), on_trade(), on_position()
# Format: {orderId, symbol, status, qty, price, ...}

# Reconnect Handling:
#   - Auto-reconnects on disconnect
#   - Triggers sync_engine() after reconnect
```

### Order Types & Execution

**Entry Order (Stop-Buy):**
```python
place_stop_buy(
    fyers,
    symbol="NSE:ADANIPORTS-EQ",
    qty=1,
    trigger_price=2800.00,
    limit_price=2800.05
)

# Execution:
# - Broker holds order until price touches 2800
# - Once triggered, executes at limit_price (or better)
# - Called "stop-buy" (buy order with trigger)
```

**SL Order (Stop-Loss):**
```python
place_sl_order(
    fyers,
    symbol="NSE:ADANIPORTS-EQ",
    qty=1,
    sl_price=2775.50
)

# Execution:
# - Broker executes when price <= sl_price (sell)
# - Called "stop-loss sell" (sell when price drops)
# - Automatically cancels when position closes
```

**Exit Order (Market):**
```python
close_position(
    fyers,
    symbol="NSE:ADANIPORTS-EQ",
    qty=1
)

# Execution:
# - Immediate market sell at best available price
# - Used for emergency exits or EOD
# - No waiting, executes in ~100-500ms
```

---

## 📊 Monitoring & Observability

### Log Files Location

```
logs/
├── system.log      # All system events
├── trades.log      # Trade-specific events
├── errors.log      # Errors and exceptions
│
└── Broker Logs:
    ├── fyersApi.log
    ├── fyersDataSocket.log
    ├── fyersOrderSocket.log
    └── fyersRequests.log
```

### Monitoring checklist

**Before Market Open (09:00 AM):**
```
[ ] System started without errors
[ ] Authentication successful
[ ] OHLC fetched and levels calculated
[ ] Engines initialized
[ ] Recovery completed (if position open)
[ ] WebSockets connected (both data and order)
[ ] Ready for first price tick
```

**During Trading (09:15 AM - 3:20 PM):**
```
[ ] Price ticks arriving every 1-5 seconds
[ ] Level transitions logged
[ ] No WebSocket errors
[ ] Orders executing successfully
[ ] Trades confirming immediately after entry
[ ] SL orders placed correctly
[ ] Trailing SL updates (if profit made)
```

**After Market Close (3:20 PM+):**
```
[ ] EOD exit triggered on all positions
[ ] All orders closed
[ ] Logs saved for review
[ ] No error messages
[ ] Ready for next day
```

### Key Log Patterns to Watch

**Healthy System:**
```
[INFO] 09:15:02 | Price tick: NSE:ADANIPORTS-EQ @ 2850.50
[INFO] 09:15:03 | ENGINE - LEVEL DETECT STATE
[INFO] 09:15:30 | Trigger detected, placing entry order
[INFO] 09:15:35 | TRADE UPDATE: Order filled @ 2800.50
[INFO] 09:15:36 | SL order placed @ 2775.50
[INFO] 10:30:00 | SL hit, closing position @ 2774.80
[INFO] 10:30:01 | RECOVERY - RESET STATE
```

**Problem Indicators:**
```
[ERROR] Connection lost, retrying...        # WS disconnect
[ERROR] Order rejected: Insufficient margin # Margin issue
[ERROR] SL order failed to place            # ⚠️ Critical!
[ERROR] MAIN ERROR: ...                    # Unhandled exception
```

### Real-Time Monitoring Dashboard (Future)

Recommended tools:
- **Streamlit** — Web-based dashboard
- **Grafana** — Historical metrics
- **Custom alerts** — Email/SMS on events

Current status: Manual log monitoring

---

## 🔄 Recovery Scenarios

### Scenario 1: WebSocket Disconnects (Network Issue)

**Timeline:**
```
09:15 - Trading normally
09:20 - Internet hiccup, WebSocket drops
  └─ No price ticks for 10 seconds
  └─ System logs: "WebSocket closed"
  └─ Auto-reconnect triggered (retry_count=20)

09:21 - Reconnection successful
  └─ on_connect() fires
  └─ resync_all() checks engine state
  └─ Broker state verified
  └─ Position still open? YES → Continue trading
  └─ Position closed? YES → Reset state
  └─ Log: "RECONNECT RESYNC COMPLETE"

09:22 - Price ticks resume
  └─ Trading continues normally
```

**User Action:** None (automatic recovery)

---

### Scenario 2: Bot Crashes (Process Kill)

**Timeline:**
```
10:00 - Bot running with active position
10:05 - Python process crashes (Windows close, kill -9, power fail)
  └─ Broker still has:
     ├─ Open position (qty=1 @ entry_price)
     └─ SL order pending (qty=1 @ sl_price)

[Manual restart]
10:10 - User restarts: python main.py
  └─ Authentication (new token)
  └─ OHLC fetched, levels calculated
  └─ sync_engine() called immediately
     └─ Fetch positions: Found position open
     └─ Extract entry_price from trade history
     └─ Calculate sl_price
     └─ Fetch orders: Found SL order pending
     └─ Restore state: active_trade=True, sl_order_id="1046"
  └─ SL protection intact, no loss of exposure

10:15 - Trading resumes
  └─ Monitoring price for SL hit
  └─ If price to 2774, SL executes (broker closes)
  └─ Position syncs on next tick
```

**User Action:** Restart bot, recovery handles state

---

### Scenario 3: Broker API Timeout (Fyers Server Issue)

**Timeline:**
```
10:30 - Try to enter trade
  └─ place_stop_buy() called
  └─ Fyers API timeout (no response for 5 sec)
  └─ Exception raised
  └─ Caught in engine
  └─ Logged: "ORDER FAILED: Timeout"

10:35 - Retry logic (built-in)
  └─ Next price tick triggers entry checks again
  └─ If condition still met, retry
  └─ If Fyers still down, manual intervention needed

[Manual Recovery]
10:40 - Wait for broker to recover
  └─ Fyers website back up
  └─ Restart bot: python main.py
  └─ Recovery sync will restore state
```

**User Action:** Monitor broker status, restart if needed

---

### Scenario 4: Missing Stop Loss Order (Critical Issue)

**Timeline:**
```
10:00 - Trade fills @ 2800.50
  └─ handle_trade_update() called
  └─ Try to place SL @ 2775.50
  └─ place_sl_order() returns: {s: "error", msg: "..."}
  └─ Log: "SL order failed to place"
  └─ Position OPEN WITHOUT SL! ⚠️

[User alerts triggered]
  └─ Email/SMS: "SL order failed"

[Manual Recovery]
10:05 - User manually places SL on Fyers web console
  └─ Sets SL order @ 2775.50

OR

10:05 - User runs force_exit()
  └─ Market sells position immediately
  └─ Mitigates risk

Preferred: Always monitor critically, add alerts
```

**User Action:** Manual SL placement or force exit

---

## ⚙️ Configuration Tuning

### Adjusting SL Points

**Test Mode - Conservative → Aggressive:**
```python
# config/trading_params.py, test_mode=True
# Conservative (larger buffer)
SL_POINTS = 15    # Allow 15-point swings

# Default (balance)
SL_POINTS = 10    # Closer stop, less noise

# Aggressive (tight stop)
SL_POINTS = 5     # Tight stop, more frequent hits
```

**Impact:**
```
Larger SL → Fewer false exits, but more loss per hit
Smaller SL → More frequent exits, smaller average loss
```

### Adjusting Trailing SL Aggressiveness

**Test Mode - Conservative:**
```python
TRAILING_RULES = {
    5: 1,      # Start protecting early
    6: 2,
    7: 3,
    ...
}
```

**Test Mode - Aggressive:**
```python
TRAILING_RULES = {
    10: 2,     # Let profit run more
    15: 5,
    20: 10,
    ...
}
```

**Impact:**
```
Aggressive → Fewer but larger wins
Conservative → More frequent exits, smaller wins
```

### Daily Loss Limits

**Test Mode - Learning:**
```python
MAX_DAILY_LOSS = 5000     # Generous for learning
MAX_TRADES_PER_DAY = 100  # Lots of opportunities
```

**Test Mode - Pre-Live:**
```python
MAX_DAILY_LOSS = 1000     # Realistic cap
MAX_TRADES_PER_DAY = 50   # Moderate frequency
```

**Live Mode - Safe:**
```python
MAX_DAILY_LOSS = 6000     # Capital-based limit
MAX_TRADES_PER_DAY = 10   # Conservative
```

---

## 🚨 Production Readiness Checklist

### System Setup
```
[ ] Python 3.11+ installed
[ ] All dependencies installed (pip install -r requirements.txt)
[ ] Fyers account created with API access
[ ] API credentials stored as environment variables
[ ] logs/ directory created (should be auto-created)
[ ] Network: Stable internet connection
```

### Initial Testing (Paper Trading or Small Account)
```
[ ] Run in TEST MODE for 2-3 days
  [ ] Verify entry logic (ticks, triggers)
  [ ] Verify exit logic (SL hits)
  [ ] Verify SL placement
  [ ] Monitor logs for errors
  
[ ] Test RECOVERY scenarios
  [ ] Kill process, restart, verify recovery
  [ ] Disconnect internet, reconnect, verify recovery
  [ ] Verify SL is protected after recovery
  
[ ] Validate SYMBOL GENERATION
  [ ] For live: Check option symbols generated correctly
  [ ] Verify expiry dates
  [ ] Check strikes are ATM
```

### Before LIVE Trading
```
[ ] Trailing SL rules are correct
[ ] Daily loss limits set appropriately
[ ] Max trades per day is reasonable
[ ] Margin check: Account has ≥ ₹50,000
[ ] Market hours: IST 09:15 AM - 3:30 PM (Mon-Fri)
[ ] Holidays: Check holidays_2026.json
[ ] EOD exit time verified (3:20 PM)
[ ] Email/SMS alerts configured (if using)
[ ] Backup power plan (UPS/WiFi hotspot)
```

### Daily Operations
```
[ ] Start bot 5 minutes before market open (09:10)
[ ] Monitor first 5 trades (verify entries/exits)
[ ] Check logs every 30 minutes
[ ] Monitor P&L progress
[ ] Verify SL orders are active
[ ] Confirm EOD exit at 3:20 PM
[ ] Archive logs for review (daily)
```

### Monthly Maintenance
```
[ ] Review trading logs
[ ] Analyze P&L by day/strategy
[ ] Adjust parameters if needed (based on results)
[ ] Check for code updates
[ ] Backup logs and configuration
```

---

## 🔧 Troubleshooting Guide

### Problem: "Missing environment variable: FYERS_CLIENT_ID"

**Cause:** API credentials not set

**Fix:**
```bash
# Windows
set FYERS_CLIENT_ID=your_id
set FYERS_SECRET_KEY=your_key

# Linux
export FYERS_CLIENT_ID=your_id
export FYERS_SECRET_KEY=your_key

# Verify
echo $FYERS_CLIENT_ID
```

---

### Problem: "WebSocket connection failed"

**Cause:** Network issue or authentication failure

**Fix:**
```bash
1. Check internet connection
2. Restart bot
3. Check logs for specific error message
4. If persistent: Check Fyers status page
```

---

### Problem: "No price ticks received (bot hanging)"

**Cause:** Symbol not subscribed, or data stream frozen

**Fix:**
```bash
1. Check symbol name in config/symbols.py
2. Verify symbol is valid (NSE:ADANIPORTS-EQ, not ADANIPORTS)
3. Restart bot and check initial recovery
4. Force exit any existing position first
```

---

### Problem: "Order rejected: Insufficient margin"

**Cause:** Account balance < order value

**Fix:**
```bash
1. Check account balance on Fyers
2. Reduce QTY in config (if possible)
3. Add funds to broker account
4. Or switch to smaller position
```

---

### Problem: "SL order not placed (critical!)"

**Cause:** Broker API error or SL price validation failure

**Fix:**
```bash
1. Check SL price is below entry (should be always)
2. Manual place SL on Fyers console
3. Or force_exit() immediately
4. Review logs for exact error
5. Contact Fyers support if persistent
```

---

## 📞 Support & Debugging

### Asking for Help

**Provide:**
1. Exact error message from logs
2. Timestamp when error occurred
3. System info (OS, Python version)
4. Recent relevant logs (5-10 lines)
5. What you were trying to do

**Example:**
```
Error: "ORDER REJECTED: GTC order rejected"

Timestamp: 2026-05-10 10:30:45
OS: Windows 10
Python: 3.11.2

Recent logs:
[ERROR] 2026-05-10 10:30:45 | place_sl_order() failed: GTC order rejected
[INFO] 2026-05-10 10:30:45 | Entry price: 2800.50, SL price: 2775.50

Action taken: Restarted bot, problem persists
```

### Debug Mode

**Enable verbose logging:**
```python
# In main.py or engine.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Output:** More detailed logs for diagnosis

---

## 📋 Deployment Checklist (Final)

```
PRE-MARKET (09:00 AM):
  [ ] Bot started
  [ ] Auth successful
  [ ] OHLC loaded
  [ ] Levels calculated
  [ ] Engines created
  [ ] WebSockets connected
  [ ] First price tick received
  
MARKET OPEN (09:15 AM):
  [ ] Monitoring price ticks
  [ ] No errors in logs
  [ ] Ready for first signal
  
IF TRADE OPENS:
  [ ] Entry order placed
  [ ] Trade fills
  [ ] SL order placed
  [ ] Position protected
  
ON SL HIT:
  [ ] Position closes
  [ ] State resets
  [ ] System ready for next
  
EOD (3:20 PM):
  [ ] All positions closed
  [ ] Any SL orders cancelled
  [ ] Daily logs archived
  [ ] Ready for next day
```

---

## Next Steps

- See `STRATEGY.md` for strategy tuning
- See `ARCHITECTURE.md` for system design
- See `COMPONENTS.md` for code details


