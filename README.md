# 📈 FYERS Algo Trading Bot (Sensex Options)

A fully automated, event-driven algorithmic trading system for **BSE Sensex Options (ATM CE/PE)** using the FYERS API.
This bot implements a **Fibonacci-based breakout strategy** with advanced order handling, trailing stop-loss, and real-time execution.

---

# 🚀 Overview

This project is designed to:

* Trade **ATM CALL & PUT options automatically**
* Use **previous day OHLC** to compute Fibonacci levels
* Execute trades using **event-driven architecture (low latency)**
* Manage risk via **fixed SL + dynamic trailing SL**
* Operate fully automated with **no manual inputs**

---

# 🧠 Strategy Summary

### Core Logic

1. Fetch previous day **High, Low, Close**
2. Calculate **ATM strike**
3. Generate **Fibonacci levels**
4. Monitor real-time price using WebSocket
5. Execute trades based on:

   * First trade trigger logic
   * Subsequent breakout logic
6. Manage trades using:

   * Fixed SL (25 points)
   * Trailing SL ladder
7. Exit all positions before **3:20 PM**

---

# 🏗️ Project Structure

```
fyers_algo_bot/
│
├── main.py                    # Entry point (orchestrator)
│
├── config/
│   ├── settings.py           # API keys, system config
│   ├── symbols.py            # ATM + expiry + symbol logic
│   └── trading_params.py     # Strategy parameters
│
├── core/
│   ├── engine.py             # Ultra-fast event-driven engine
│   ├── state.py              # Trade state tracking
│   └── events.py             # Cross/trigger detection
│
├── strategy/
│   └── fib_strategy.py       # Strategy rules (pluggable)
│
├── broker/
│   ├── auth.py               # FYERS authentication
│   ├── orders.py             # Order placement/modification
│   ├── data_ws.py            # WebSocket handling
│   └── data_fetch.py         # Historical OHLC fetch
│
├── utils/
│   ├── logger.py             # Logging system
│   ├── helpers.py            # Utility functions
│   └── time_utils.py         # Time checks (EOD)
│
├── data/
│   ├── cache/                # Daily cached values
│   └── instruments/          # Instrument dumps (optional)
│
├── logs/
│   ├── trades.log
│   ├── errors.log
│   └── system.log
│
├── tests/
│   ├── test_engine.py
│   └── test_strategy.py
│
├── requirements.txt
└── README.md
```

---

# ⚙️ Tech Stack

| Component       | Technology            |
| --------------- | --------------------- |
| Language        | Python 3.10+          |
| Broker API      | FYERS API v3          |
| Data Feed       | WebSocket (real-time) |
| Architecture    | Event-driven          |
| Deployment      | AWS EC2 (recommended) |
| Logging         | File-based logging    |
| Version Control | Git                   |

---

# ⚡ Key Features

### ✅ Fully Automated

* No manual inputs (ATM, OHLC auto-calculated)

### ✅ Event-Driven Engine

* Executes logic only on meaningful price changes
* Ultra-low latency (O(1) per tick)

### ✅ Smart Order Management

* Stop-buy entry orders
* Cancel & replace logic
* SL + Trailing SL updates

### ✅ Risk Management

* Fixed SL (25 points)
* Trailing SL ladder
* One active trade per side

### ✅ Independent Engines

* Separate logic for:

  * CALL side
  * PUT side

### ✅ End-of-Day Safety

* Auto square-off at 3:20 PM

---

# 🔄 Execution Flow

## 1. System Start

* Authenticate with FYERS
* Initialize logging

## 2. Pre-Market Setup

* Fetch previous day OHLC
* Calculate ATM strike
* Generate option symbols
* Compute Fibonacci levels

## 3. Live Execution

* Start WebSocket
* For each tick:

  * Detect level crossing
  * Apply entry logic
  * Manage trades

## 4. Trade Management

* Place entry orders
* Confirm execution
* Place SL order
* Update trailing SL

## 5. End-of-Day

* Close all open positions
* Cancel pending orders

---

# 📦 Installation

## 1. Clone Repository

```bash
git clone https://github.com/your-repo/fyers-algo-bot.git
cd fyers-algo-bot
```

---

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Configure Settings

Edit:

```
config/settings.py
```

Add:

```python
CLIENT_ID = "your_client_id"
SECRET_KEY = "your_secret_key"
REDIRECT_URI = "your_redirect_url"
```

---

# ▶️ Running the Bot

```bash
python main.py
```

---

# 🔐 Authentication Flow

1. Script generates login URL
2. Login via browser
3. Copy auth code
4. Paste in terminal

---

# 📊 Logs

Logs are stored in `/logs`:

| File       | Description         |
| ---------- | ------------------- |
| trades.log | Trade entries/exits |
| errors.log | Errors & failures   |
| system.log | System events       |

---

# ⚠️ Important Notes

* Ensure **stable internet connection**
* Use **static IP** for FYERS API
* Start bot before market opens
* Always test with **small capital first**

---

# 🧪 Testing

Run unit tests:

```bash
pytest tests/
```

---

# ☁️ Deployment (AWS EC2)

### Steps:

1. Launch Ubuntu EC2 instance
2. Install Python
3. Upload project
4. Run using:

```bash
screen -S algo
python main.py
```

---

# 🔮 Future Enhancements

* ✅ Order execution via WebSocket (real-time fills)
* ✅ Position reconciliation system
* ✅ Multi-strategy support
* ✅ Dashboard (PnL + metrics)
* ✅ Telegram alerts
* ✅ Database logging (PostgreSQL)
* ✅ Auto-restart on crash
* ✅ Backtesting engine
* ✅ Multi-broker support

---

# 🛑 Risk Disclaimer

This software is for educational purposes only.
Trading involves financial risk. Use at your own discretion.

---

# 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first.

---

# 📌 Final Thought

This is not just a script—it’s a **trading system**.
Execution quality, discipline, and risk control matter more than strategy.

---
