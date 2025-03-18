# Futu API Trading Program

A Python-based trading program that uses the Futu OpenAPI to access market data and execute trades.

## Prerequisites

1. Install [Futu OpenD](https://openapi.futunn.com/futu-api-doc/intro/intro.html) and start it with your Futu/Moomoo account
2. Python 3.7 or higher
3. Futu API Python SDK

## Installation

1. Clone the repository:
```
git clone <repository-url>
cd futu-trader
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

3. Configure your environment variables:
```
cp .env.example .env
```

Then edit the `.env` file with your connection details and account credentials.

## Configuration

The `.env` file contains the following configuration options:

```
# Futu OpenD Connection Settings
FUTU_OPEND_HOST=127.0.0.1
FUTU_OPEND_PORT=11111

# Password Hashing Settings
USE_MD5_HASH=True
IS_PASSWORD_HASHED=False

# Trading Account Credentials
FUTU_ACCOUNT_ID=YOUR_ACCOUNT_ID
FUTU_ACCOUNT_PWD=YOUR_ACCOUNT_PASSWORD
FUTU_TRADE_PWD=YOUR_TRADE_PASSWORD
FUTU_UNLOCK_TRADE_PWD=YOUR_UNLOCK_TRADE_PASSWORD

# Market Data Settings
DEFAULT_MARKET=HK  # Options: HK, US, CN, SG
QUOTE_PUSH_INTERVAL_S=3  # In seconds
```

### Password Security

To improve security and avoid storing plaintext passwords in your .env file, the application supports MD5 password hashing:

1. **Default Mode** - The application can automatically hash your passwords using MD5 before sending them to the Futu API:
   - Set `USE_MD5_HASH=True` and `IS_PASSWORD_HASHED=False`
   - Enter your actual passwords in plaintext in the .env file
   - The application will hash them before sending to the API

2. **Pre-hashed Mode** - You can pre-hash your passwords and store only the hashes:
   - Set `USE_MD5_HASH=True` and `IS_PASSWORD_HASHED=True`
   - Generate MD5 hashes of your passwords using the built-in command:
     ```
     python main.py hash-pwd "your_password"
     ```
   - Enter the resulting hash values (32 hex characters) in the .env file

This approach prevents plaintext passwords from being stored in your configuration files.

## Usage

The program provides several commands:

### Get Stock Quotes

```
python main.py quote HK.00700
```

This command will display the current quote, order book, and recent K-line data for the specified stock.

### Check Account Information

```
python main.py account
```

This command will display your account information, current positions, and recent orders.

### Run a Trading Strategy

```
python main.py strategy sma HK.00700 --short-window 10 --long-window 30
```

This will run a Simple Moving Average crossover strategy on the specified stock. The strategy will buy when the short moving average crosses above the long moving average, and sell when it crosses below.

### Generate Password Hash

```
python main.py hash-pwd "your_password"
```

This command generates an MD5 hash of your password that you can store in the .env file when using pre-hashed mode (`IS_PASSWORD_HASHED=True`).

## Available Strategies

### Simple Moving Average (SMA)

A trend-following strategy that uses two moving averages to generate buy and sell signals:

- Buy when the short-term moving average crosses above the long-term moving average
- Sell when the short-term moving average crosses below the long-term moving average

Parameters:
- `--short-window`: Period for the short-term moving average (default: 10)
- `--long-window`: Period for the long-term moving average (default: 30)

## Architecture

The program is organized into several components:

- `connection.py`: Manages the connection to Futu OpenD
- `market_data.py`: Handles market data operations (quotes, K-lines, etc.)
- `trading.py`: Handles trading operations (placing orders, positions, etc.)
- `strategy.py`: Implements trading strategies
- `main.py`: Command-line interface and main entry point
- `utils.py`: Utility functions including password hashing

## Warning

This software is for educational purposes only. Use at your own risk. Always test with a paper trading account before using real money.

## License

MIT 