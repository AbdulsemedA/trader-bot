# 🤖 Binance Futures Testnet Trading Bot

A Python CLI application for placing **Market**, **Limit**, and **Stop-Limit** orders on the Binance Futures Testnet (USDT-M). Built with clean architecture, structured logging, and a polished terminal experience.

## Features

- ✅ **Market & Limit orders** on Binance Futures Testnet
- ✅ **Stop-Limit orders** (bonus)
- ✅ **BUY & SELL** support
- ✅ Rich CLI output with colored tables and panels
- ✅ Confirmation prompt before order execution
- ✅ Structured logging to file + console
- ✅ Comprehensive input validation
- ✅ HMAC-SHA256 request signing (direct REST — no wrapper libraries)

## Project Structure

```
trading_bot/
  bot/
    __init__.py
    client.py            # Binance API client (HMAC-SHA256 signing, requests)
    orders.py            # Order placement logic (market, limit, stop-limit)
    validators.py        # Input validation
    logging_config.py    # Logging setup (file + console handlers)
  cli.py                 # CLI entry point (Typer + Rich)
  .env.example           # Template for API credentials
  requirements.txt
  README.md
```

## Setup

### 1. Prerequisites

- Python 3.10+
- A [Binance Futures Testnet](https://testnet.binancefuture.com) account with API credentials

### 2. Install Dependencies

```bash
# Clone the repository
git clone <repo-url>
cd trading_bot

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Credentials

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your testnet API key and secret
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

> ⚠️ Never commit your `.env` file. It is excluded via `.gitignore`.

## Usage

### View Help

```bash
python cli.py --help
```

### Market Order

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Limit Order

```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 50000
```

### Stop-Limit Order (Bonus)

```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP_LIMIT --quantity 0.001 --price 60000 --stop-price 59000
```

### Short-form Options

```bash
python cli.py -s ETHUSDT -d SELL -t MARKET -q 0.01
```

## Example Output

```
╭──────────── 📋 Order Request ─────────────╮
│  Symbol      BTCUSDT                       │
│  Side        BUY                           │
│  Type        MARKET                        │
│  Quantity    0.001                          │
╰────────────────────────────────────────────╯
Do you want to proceed with this order? [y/n]: y

       📊 Order Response
┌────────────────┬───────────┐
│ Field          │ Value     │
├────────────────┼───────────┤
│ Order ID       │ 123456    │
│ Symbol         │ BTCUSDT   │
│ Side           │ BUY       │
│ Type           │ MARKET    │
│ Status         │ FILLED    │
│ Original Qty   │ 0.001     │
│ Executed Qty   │ 0.001     │
│ Avg Price      │ 67543.20  │
└────────────────┴───────────┘
✅ Order placed successfully!
```

## Logging

All API requests, responses, and errors are logged to `trading_bot.log` with the format:

```
2025-01-15 10:30:45 | INFO     | trading_bot.orders | Preparing MARKET BUY order: BTCUSDT qty=0.001
2025-01-15 10:30:45 | DEBUG    | trading_bot.client | REQUEST  POST https://testnet.binancefuture.com/fapi/v1/order | params={...}
2025-01-15 10:30:46 | DEBUG    | trading_bot.client | RESPONSE ... | status=200 | body={...}
2025-01-15 10:30:46 | INFO     | trading_bot.client | Order placed successfully: orderId=123456
```

## Assumptions

- The bot targets **Binance Futures Testnet** only (`https://testnet.binancefuture.com`)
- API credentials are loaded from a `.env` file in the project root
- Direct REST calls with HMAC-SHA256 signing are used instead of the `python-binance` library
- Stop-Limit orders use the `STOP` type as defined in the Binance Futures API
- The `timeInForce` is set to `GTC` (Good Till Cancelled) for Limit and Stop-Limit orders
- Quantity precision and price tick size validation are delegated to the Binance API server
# trader-bot
