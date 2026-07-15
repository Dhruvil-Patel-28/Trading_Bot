# Binance Futures Testnet Trading Bot

A Python CLI trading bot for placing **Market** and **Limit** orders on the **Binance Futures Testnet (USDT-M)**.

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance API wrapper (testnet mode)
│   ├── orders.py          # Order placement logic & output formatting
│   ├── validators.py      # Input validation (symbol, side, type, qty, price)
│   └── logging_config.py  # Shared logger → logs/trading_bot.log
├── cli.py                 # CLI entry point (argparse)
├── .env                   # API credentials (not committed)
├── .env.example           # Credential template
├── .gitignore
├── requirements.txt
├── README.md
└── logs/                  # Log output directory
```

## Prerequisites

- Python 3.10+
- A [Binance Futures Testnet](https://testnet.binancefuture.com/) account with API key and secret

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd trading_bot
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API credentials:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Binance Futures Testnet API key and secret.

## Usage

**Always activate the virtual environment first:**
```bash
source venv/bin/activate
```

### Place a Market Order
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Place a Limit Order
```bash
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 3500
```

### CLI Arguments

| Argument     | Required | Description                                      |
|--------------|----------|--------------------------------------------------|
| `--symbol`   | Yes      | Trading pair (e.g., `BTCUSDT`, `ETHUSDT`)        |
| `--side`     | Yes      | `BUY` or `SELL`                                  |
| `--type`     | Yes      | `MARKET` or `LIMIT`                              |
| `--quantity` | Yes      | Order quantity (must be > 0)                     |
| `--price`    | No       | Order price (required for `LIMIT`, ignored for `MARKET`) |

### Help
```bash
python cli.py --help
```

## Logging

All API requests, responses, and errors are logged to `logs/trading_bot.log` with structured formatting:

```
2026-07-15 12:30:00 | INFO     | trading_bot.client | Placing BUY MARKET order: symbol=BTCUSDT, qty=0.001
2026-07-15 12:30:01 | INFO     | trading_bot.client | Order placed successfully: orderId=123456, status=NEW
```

- **File log:** `DEBUG` level and above (full detail)
- **Console:** `WARNING` level and above (keeps output clean)

## Error Handling

The bot handles errors gracefully with distinct, readable messages:

- **Validation errors:** Invalid symbol, side, type, quantity, or missing price for LIMIT orders
- **API errors:** Binance-specific error codes and messages (e.g., insufficient balance, invalid quantity precision)
- **Network errors:** Connection failures with retry guidance

No raw stack traces are shown to the user.

## Assumptions

1. **Testnet only:** This bot is configured exclusively for the Binance Futures Testnet (`https://testnet.binancefuture.com`). It does **not** connect to the live/production Binance API.
2. **USDT-M Futures:** Only USDT-margined futures contracts are supported.
3. **Order types:** Only `MARKET` and `LIMIT` orders are supported. Other types (STOP, TAKE_PROFIT, etc.) are not implemented.
4. **Time in Force:** LIMIT orders default to `GTC` (Good Till Cancelled).
5. **No position management:** The bot places individual orders but does not manage open positions, stop-losses, or take-profits.
6. **Symbol validation:** The bot validates the format of the symbol string but does not check if the symbol actually exists on Binance. Invalid symbols will be caught by the API and returned as a clear error.
7. **Quantity precision:** The bot does not automatically adjust quantity to match Binance's step size rules. If the quantity precision is incorrect, the API will return an error.
