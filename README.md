# 📊 Sensex Options Fibonacci Trading Bot

A **fully event-driven, recovery-safe intraday trading system** built for **BSE Sensex options**, using **pure price-action + Fibonacci levels**.
Designed with **institutional-grade execution flow**, real-time WebSockets, and broker-synced recovery—without relying on databases.

---

# 🚀 Overview

This project implements a **systematic trading engine** that:

* Trades **ATM Sensex Call & Put options**
* Uses **Fibonacci retracement levels** derived from **previous day OHLC**
* Executes trades using **stop-buy breakout logic**
* Maintains **strict one-trade-per-side discipline**
* Automatically manages **SL + trailing SL**
* Ensures **state consistency using broker sync + recovery (no DB required)**

---

# 🧠 Core Philosophy

```text
Broker = Truth
Engine State = Mirror
WebSocket = Trigger
```

* No blind assumptions
* No polling-based execution
* Fully event-driven

---

# 🏗️ Project Structure

```text
Fib_Trading/
│
├── main.py                     # Entry point
│
├── core/
│   ├── engine.py              # Execution engine (brain)
│   ├── state.py               # Trade state management
│   ├── events.py              # Fast price-level logic
│   └── recovery.py            # Institutional-grade recovery system
│
├── broker/
│   ├── auth.py                # Fyers authentication
│   ├── data_ws.py             # Price WebSocket
│   ├── order_ws.py            # Order/Trade/Position WebSocket
│   ├── orders.py              # All broker actions
│   └── data_fetch.py          # Historical OHLC
│
├── strategy/
│   └── fib_strategy.py        # Fibonacci logic + SL calculation
│
├── config/
│   ├── settings.py            # API + system config
│   ├── symbols.py             # Option symbol generation (expiry logic)
│   └── trading_params.py      # Strategy parameters
│
├── utils/
│   ├── logger.py              # Logging
│   ├── helpers.py             # Utility helpers
│   └── time_utils.py          # Market time checks
│
├── data/
│   └── holidays_2026.json     # Trading holidays
│
├── tests/
│   ├── test_engine.py
│   └── test_strategy.py
│
└── requirements.txt
```

---

# ⚙️ Tech Stack

| Component    | Technology                          |
| ------------ | ----------------------------------- |
| Language     | Python 3.11+                        |
| Broker API   | Fyers API v3                        |
| Market Data  | WebSocket (symbolUpdate)            |
| Execution    | WebSocket (orders/trades/positions) |
| Architecture | Event-driven                        |
| Storage      | None (broker-synced recovery)       |

---

# 🔄 System Flow (High-Level)

```text
Start Bot
   ↓
Load Config
   ↓
Fetch Previous Day OHLC
   ↓
Generate Fibonacci Levels
   ↓
Create Engines (CALL + PUT)
   ↓
INITIAL RECOVERY (sync with broker)
   ↓
Start WebSockets
   ↓
Live Trading Loop
```

---

# 🔥 Execution Flow (Detailed)

## 📈 Price Flow

```text
Tick (WebSocket)
   ↓
Engine.on_tick()
   ↓
Level detection (O(1))
   ↓
Entry / SL / Trailing decisions
```

---

## 💰 Trade Flow

```text
Entry condition met
   ↓
Stop-buy order placed
   ↓
Trade WebSocket confirms fill
   ↓
Engine.handle_trade_update()
   ↓
SL order placed immediately
```

---

## 🛡️ Risk Flow

```text
Price hits SL
   ↓
Broker executes SL
   ↓
Position update WebSocket
   ↓
Engine.handle_position_update()
   ↓
State reset
```

---

# 🔁 Recovery System (CRITICAL)

## ✅ Startup Recovery

```text
Bot starts
   ↓
Fetch positions + orders
   ↓
Rebuild:
   - active_trade
   - entry_order_id
   - sl_order_id
```

---

## ✅ Reconnect Recovery

```text
WebSocket reconnects
   ↓
on_connect()
   ↓
Trigger resync_all()
   ↓
sync_engine()
   ↓
State corrected
```

---

## ✅ Position Sync (Real-time)

```text
Broker position changes
   ↓
on_position()
   ↓
Engine.handle_position_update()
   ↓
State updated instantly
```

---

# 📊 Strategy Logic

---

## 🎯 Entry Rules

### First Trade

* Trigger = `level - SL_POINTS`
* If price hits trigger → place stop-buy at level

---

## 🔁 Subsequent Trades

* Only after previous trade exits
* Entry when price crosses level from below

---

## 🚫 Restrictions

* Only **1 active trade per side**
* No re-entry until trade exits

---

## 🛑 Stop Loss

* Fixed: `entry - SL_POINTS`

---

## 📈 Trailing SL

Defined in `trading_params.py`:

```python
TRAILING_RULES = {
    200: 50,
    400: 200,
    ...
}
```

---

## ⏰ EOD Exit

* All positions closed before **3:20 PM**

---

# ⚡ Performance Design

* O(1) level detection (no loops)
* No polling (WebSocket-only)
* Lightweight logging
* Async threads for WS

---

# 🔐 Security

* Uses **environment variables** for API keys
* No credentials stored in code

---

# 🧪 Modes

## 🧪 Test Mode

* Equity trading (e.g., HDFCBANK)
* Small SL
* Fast iteration

## 🚀 Live Mode

* Sensex options
* Full strategy rules

---

# ▶️ How to Run

---

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 2. Set Environment Variables

```bash
set FYERS_CLIENT_ID=your_client_id
set FYERS_SECRET_KEY=your_secret
```

---

## 3. Run the Bot

```bash
python main.py
```

---

# ⚠️ Important Notes

---

## 🚨 Do NOT skip these

* Verify symbol generation (weekly/monthly expiry)
* Test reconnect scenarios
* Run with **1 lot initially**

---

## 🧠 Known Trade-offs

* No database → state derived from broker
* trades_today resets on restart
* first_trade_done resets

---

# 📈 Future Enhancements

---

## 🔹 High Priority

* Max daily loss enforcement
* Trade journal (CSV)
* PnL tracking

---

## 🔹 Advanced

* Multi-strategy engine
* Position scaling (pyramiding)
* Auto-restart watchdog
* Latency monitoring

---

## 🔹 Professional Level

* Dashboard (Streamlit)
* Backtesting engine
* Multi-broker support

---

# 🧠 Final Insight

```text
This is not just a bot.
This is a real-time, event-driven trading system.
```

* Execution is handled by WebSocket
* State is validated by broker
* Recovery ensures consistency

---

# 🚀 Disclaimer

This project is for educational and personal use.
Live trading involves risk. Always test thoroughly before deploying real capital.

---

# 🙌 Contribution

You can extend this system by:

* Adding new strategies
* Improving risk management
* Building UI/dashboard

---

# 📌 Final Status

```text
Execution Engine      ✅
Recovery System       ✅
WebSocket Handling    ✅
Symbol Logic          ✅
Production Ready      ⚠️ (after testing)
```

---
