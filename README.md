# Binance Futures Testnet Trading Bot

A Python CLI trading bot for placing **Market** and **Limit** orders on the **Binance Futures Testnet (USDT-M)**.

Built as a clean, modular command-line tool that validates inputs locally, communicates with the Binance Futures Testnet API, and provides structured logging for every operation.

---

## Table of Contents

- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Design Decisions](#design-decisions)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Usage](#usage)
- [Sample Output](#sample-output)
- [Logging](#logging)
- [Error Handling](#error-handling)
- [Assumptions & Limitations](#assumptions--limitations)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Layer                            │
│  cli.py — argparse, user-facing input/output                │
└──────────────────────────┬──────────────────────────────────┘
                           │ calls execute_order()
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Orchestration Layer                        │
│  bot/orders.py — validates → calls API → formats output     │
└─────────┬───────────────────────────────────┬───────────────┘
          │                                   │
          ▼                                   ▼
┌──────────────────────┐        ┌──────────────────────────┐
│   Validation Layer   │        │       API Layer           │
│  bot/validators.py   │        │  bot/client.py            │
│  Pure input checks,  │        │  Binance API wrapper,     │
│  no I/O or network   │        │  credentials, HTTP calls  │
└──────────────────────┘        └──────────────────────────┘
                                           │
                                           ▼
                                ┌──────────────────────┐
                                │  Binance Futures      │
                                │  Testnet API          │
                                │  (USDT-M)             │
                                └──────────────────────┘

Cross-cutting: bot/logging_config.py → logs/trading_bot.log
```

**Data flows one direction:** CLI → Orchestration → Validation + API → Binance. Each layer has a single responsibility and no knowledge of the layers above it.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # Package marker
│   ├── client.py            # Binance API wrapper — credentials, connection, order execution
│   ├── orders.py            # Orchestration — validation, API call, formatting, logging
│   ├── validators.py        # Pure input validation — symbol, side, type, quantity, price
│   └── logging_config.py    # Shared logger factory → logs/trading_bot.log
├── cli.py                   # CLI entry point — argparse argument parsing
├── .env                     # API credentials (git-ignored, never committed)
├── .env.example             # Credential template with placeholder values
├── .gitignore               # Excludes venv/, .env, __pycache__/, *.pyc, logs/*.log
├── requirements.txt         # Python dependencies
├── README.md
└── logs/                    # Log output directory (log files are git-ignored)
```

---

## Design Decisions

### Separation of Concerns

The codebase is split into four distinct layers to keep responsibilities clean:

| Layer | File | Knows About | Does NOT Know About |
|-------|------|-------------|---------------------|
| **CLI** | `cli.py` | argparse, `orders.execute_order()` | Binance API, validation rules |
| **Orchestration** | `bot/orders.py` | validators, client, formatting | argparse, CLI arguments |
| **Validation** | `bot/validators.py` | Input rules only | API, CLI, network |
| **API** | `bot/client.py` | Binance SDK, credentials | CLI arguments, validation logic |

This means:
- **`validators.py`** can be unit-tested with no network or mocks needed
- **`client.py`** can be swapped for a different exchange without touching the CLI
- **`orders.py`** orchestrates everything without being coupled to either end

### Error Handling Strategy

Three categories of errors, each with distinct handling:

1. **Validation errors** — caught *before* any API call is made. Saves a network round-trip and gives instant feedback.
2. **Binance API errors** — specific error codes from the exchange (e.g., insufficient balance, invalid precision). Displayed with the Binance error code for easy debugging.
3. **Network errors** — connection failures, timeouts. Displayed with guidance to check connectivity.

All errors produce human-readable messages. No raw stack traces reach the user.

### Security

- API keys are loaded from `.env` via `python-dotenv` at runtime — never hardcoded
- `.env` is in `.gitignore` — cannot be accidentally committed
- Log messages include order metadata (symbol, qty, orderId) but never dump raw API payloads that could contain keys or signatures
- All operations use the **testnet** endpoint — no real funds at risk

---

## Prerequisites

- **Python 3.10+**
- A **[Binance Futures Testnet](https://testnet.binancefuture.com/)** account
- A Testnet **API Key** and **API Secret** (generated from the testnet dashboard)

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Dhruvil-Patel-28/Trading_Bot.git
cd Trading_Bot
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

This installs:
- **`python-binance`** — Binance API SDK (supports Futures Testnet)
- **`python-dotenv`** — Loads environment variables from `.env`

### 4. Configure API credentials

```bash
cp .env.example .env
```

Edit `.env` and replace the placeholders with your real testnet keys:

```
BINANCE_API_KEY=your_actual_testnet_api_key
BINANCE_API_SECRET=your_actual_testnet_api_secret
```

> ⚠️ **Never commit `.env`** — it is git-ignored by default.

---

## Usage

**Always activate the virtual environment first:**

```bash
source venv/bin/activate
```

### Place a Market Order

Executes immediately at the current market price:

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Place a Limit Order

Places an order at a specific price (fills when the market reaches that price):

```bash
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 3500
```

### CLI Arguments

| Argument     | Required | Type   | Description                                                  |
|--------------|----------|--------|--------------------------------------------------------------|
| `--symbol`   | Yes      | string | Trading pair symbol (e.g., `BTCUSDT`, `ETHUSDT`)             |
| `--side`     | Yes      | string | Order side: `BUY` or `SELL`                                  |
| `--type`     | Yes      | string | Order type: `MARKET` or `LIMIT`                              |
| `--quantity` | Yes      | float  | Order quantity (must be > 0)                                 |
| `--price`    | No       | float  | Order price — **required** for `LIMIT`, ignored for `MARKET` |

### View Help

```bash
python cli.py --help
```

---

## Sample Output

### Successful Market Order

```
🤖 Binance Futures Testnet Trading Bot
────────────────────────────────────────

══════════════════════════════════════════════════
  ORDER REQUEST SUMMARY
══════════════════════════════════════════════════
  Symbol:     BTCUSDT
  Side:       BUY
  Type:       MARKET
  Quantity:   0.001
══════════════════════════════════════════════════

══════════════════════════════════════════════════
  ORDER RESPONSE
══════════════════════════════════════════════════
  Order ID:       123456789
  Status:         NEW
  Symbol:         BTCUSDT
  Side:           BUY
  Type:           MARKET
  Orig Qty:       0.001
  Executed Qty:   0.001
  Avg Price:      98250.00
══════════════════════════════════════════════════

✅ Order placed successfully! (ID: 123456789, Status: NEW)
```

### Validation Error (Missing Price for LIMIT)

```
❌ Validation Error: Price is required for LIMIT orders.
```

### API Error (Invalid Quantity)

```
❌ Order Failed: Binance API error (-1111): Quantity precision is over the maximum defined for this asset.
```

---

## Logging

All API interactions are logged to **`logs/trading_bot.log`** with structured formatting:

```
2026-07-15 12:30:00 | INFO     | trading_bot.client  | Binance Futures Testnet client initialized successfully.
2026-07-15 12:30:00 | INFO     | trading_bot.client  | Placing BUY MARKET order: symbol=BTCUSDT, qty=0.001
2026-07-15 12:30:01 | INFO     | trading_bot.client  | Order placed successfully: orderId=123456, status=NEW
2026-07-15 12:30:05 | WARNING  | trading_bot.orders  | Validation failed: Price is required for LIMIT orders.
2026-07-15 12:30:10 | ERROR    | trading_bot.client  | Binance API error [-1111]: Quantity precision is over the maximum.
```

### Log Levels

| Level   | What's Logged                               | Destination        |
|---------|---------------------------------------------|--------------------|
| `DEBUG` | Detailed internal state (if added)          | File only          |
| `INFO`  | API requests, successful responses          | File only          |
| `WARNING` | Validation failures, unexpected statuses  | File + Console     |
| `ERROR` | API errors, network failures                | File + Console     |

- **File handler:** Captures `DEBUG` and above — full audit trail
- **Console handler:** Only `WARNING` and above — keeps CLI output clean

### Log Format

```
<timestamp> | <level> | <module> | <message>
```

Logs are structured for easy grep/search but never dump raw API payloads that could leak API keys or signatures.

---

## Error Handling

The bot uses a layered error handling strategy — each error type produces a distinct, readable message:

### 1. Input Validation Errors

Caught **before** any API call. No network request is made.

| Invalid Input | Error Message |
|---|---|
| Empty symbol | `Symbol is required and must be a non-empty string.` |
| Bad side (e.g., `HOLD`) | `Invalid side 'HOLD'. Must be 'BUY' or 'SELL'.` |
| Bad type (e.g., `STOP`) | `Invalid order type 'STOP'. Must be 'MARKET' or 'LIMIT'.` |
| Negative quantity | `Invalid quantity '-5.0'. Must be greater than 0.` |
| LIMIT without price | `Price is required for LIMIT orders.` |

### 2. Binance API Errors

Returned by the exchange with specific error codes:

| Scenario | Example Message |
|---|---|
| Invalid symbol | `Binance API error (-1121): Invalid symbol.` |
| Precision too high | `Binance API error (-1111): Quantity precision is over the maximum.` |
| Insufficient balance | `Binance API error (-2019): Margin is insufficient.` |

### 3. Network Errors

Connection or timeout issues:

| Scenario | Example Message |
|---|---|
| No internet | `Network error: Could not connect to Binance. Check your internet connection.` |
| Timeout | `Binance request failed: <timeout details>` |

---

## Assumptions & Limitations

1. **Testnet only** — Configured exclusively for `https://testnet.binancefuture.com`. Does **not** connect to the live Binance API. No real money is involved.

2. **USDT-M Futures** — Only USDT-margined futures contracts are supported.

3. **Order types** — Only `MARKET` and `LIMIT` orders. Advanced types (STOP_MARKET, TAKE_PROFIT, TRAILING_STOP, etc.) are not implemented.

4. **Time in Force** — LIMIT orders default to `GTC` (Good Till Cancelled).

5. **No position management** — The bot places individual orders but does not manage open positions, stop-losses, or take-profit chains.

6. **Symbol existence** — The bot validates the *format* of the symbol (alphanumeric, uppercase) but does not verify the symbol exists on Binance. Invalid symbols are caught by the API and surfaced as a clear error.

7. **Quantity precision** — The bot does not auto-adjust quantity to match Binance's step size rules for each symbol. If precision is incorrect, the API returns a descriptive error.

8. **Single order per invocation** — Each CLI execution places one order. There is no batch mode or interactive REPL.

9. **No auto-retry** — Failed API calls are not retried automatically. The user is shown the error and can retry manually.

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `python-binance` | Latest | Binance API SDK with Futures Testnet support |
| `python-dotenv` | Latest | Load `.env` environment variables at runtime |

All other imports (`argparse`, `logging`, `os`, `sys`, `re`) are from the Python standard library.
