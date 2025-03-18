#!/usr/bin/env python3
import argparse
import logging
import os
import signal
import sys
import time
from dotenv import load_dotenv
import pandas as pd

import futu as ft
from connection import FutuConnection
from market_data import MarketData
from trading import Trading
from strategy import SimpleMovingAverageStrategy
from utils import generate_password_hash

# Configure logging - set to DEBUG for more detailed information
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('futu_trader.log')
    ]
)
logger = logging.getLogger("FutuTrader")

# Also set Futu API's logger to DEBUG
futu_logger = logging.getLogger("futu")
futu_logger.setLevel(logging.DEBUG)

def setup_environment():
    """Load environment variables and check configuration"""
    # Load environment variables
    load_dotenv()
    
    # Check if OpenD is configured
    if not os.getenv('FUTU_OPEND_HOST') or not os.getenv('FUTU_OPEND_PORT'):
        logger.warning("OpenD connection not configured in .env file. Using defaults.")
    
    # Check if account credentials are configured
    if not os.getenv('FUTU_ACCOUNT_ID') or not os.getenv('FUTU_ACCOUNT_PWD'):
        logger.warning("Account credentials not configured in .env file")
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            with open('.env.example', 'r') as example:
                f.write(example.read())
        logger.info("Created .env file from .env.example. Please configure your settings.")

def handle_exit(signum, frame):
    """Handle graceful exit on signals"""
    logger.info("Received exit signal. Shutting down...")
    sys.exit(0)

def hash_password_cmd(password):
    """Generate MD5 hash for a password"""
    if not password:
        logger.error("No password provided")
        return False
        
    hashed = generate_password_hash(password)
    print(f"MD5 hash: {hashed}")
    print("Add this hash to your .env file and set IS_PASSWORD_HASHED=True")
    return True

class FutuTrader:
    """Main application class"""
    
    def __init__(self):
        self.conn = FutuConnection()
        self.market_data = None
        self.trading = None
        self.strategy = None
    
    def initialize(self):
        """Initialize connections and services"""
        # Connect to OpenD
        if not self.conn.connect():
            logger.error("Failed to connect to OpenD. Exiting.")
            return False
        
        # Initialize services
        self.market_data = MarketData(self.conn)
        self.trading = Trading(self.conn)
        
        # Try to get account list to verify connection
        try:
            logger.debug("Getting account list to verify connection...")
            accounts = self.trading.get_account_list()
            if accounts is not None and not accounts.empty:
                logger.info(f"Available accounts: {len(accounts)}")
                for i, acc in accounts.iterrows():
                    logger.info(f"  Account {i+1}: {acc.get('acc_id', 'Unknown')} - {acc.get('trd_env_name', 'Unknown')}")
            else:
                logger.warning("No trading accounts found or unable to retrieve account list. "
                              "Make sure OpenD is properly configured with your trading accounts.")
        except Exception as e:
            logger.error(f"Error checking account list: {str(e)}")
        
        return True
    
    def run_strategy(self, strategy_name, stock_code, **kwargs):
        """Run a trading strategy"""
        if strategy_name.lower() == 'sma':
            # Simple Moving Average strategy
            self.strategy = SimpleMovingAverageStrategy(self.market_data, self.trading)
            
            # Get parameters
            short_window = int(kwargs.get('short_window', 10))
            long_window = int(kwargs.get('long_window', 30))
            
            # Setup and start the strategy
            if not self.strategy.setup(stock_code, short_window, long_window):
                logger.error("Failed to setup strategy. Exiting.")
                return False
                
            self.strategy.start()
            return True
        else:
            logger.error(f"Unknown strategy: {strategy_name}")
            return False
    
    def run_quote_demo(self, stock_code):
        """Run a simple quote demonstration"""
        logger.info(f"Running quote demo for {stock_code}")
        
        # Subscribe to stock
        if not self.market_data.subscribe_stock(stock_code):
            logger.error(f"Failed to subscribe to {stock_code}")
            return False
        
        try:
            # Get basic quote
            quote = self.market_data.get_stock_quote(stock_code)
            if quote is not None and not quote.empty:
                logger.info(f"Quote for {stock_code}:")
                # In Futu API, the result is a DataFrame, not a dict
                logger.info(f"  Last Price: {quote['last_price'].iloc[0] if 'last_price' in quote.columns else 'N/A'}")
                logger.info(f"  Open: {quote['open_price'].iloc[0] if 'open_price' in quote.columns else 'N/A'}")
                logger.info(f"  High: {quote['high_price'].iloc[0] if 'high_price' in quote.columns else 'N/A'}")
                logger.info(f"  Low: {quote['low_price'].iloc[0] if 'low_price' in quote.columns else 'N/A'}")
                logger.info(f"  Volume: {quote['volume'].iloc[0] if 'volume' in quote.columns else 'N/A'}")
            else:
                logger.warning(f"No quote data received for {stock_code}")
            
            # Get order book - handle different return types
            order_book = self.market_data.get_order_book(stock_code)
            if order_book is not None:
                logger.info(f"Order Book for {stock_code}:")
                
                # Check if order_book is a dict with 'Bid' and 'Ask' keys
                if isinstance(order_book, dict) and 'Bid' in order_book and 'Ask' in order_book:
                    # Process bids
                    bids = order_book['Bid']
                    if bids and len(bids) > 0:
                        logger.info("  Bid:")
                        for i, bid in enumerate(bids[:min(3, len(bids))]):
                            if isinstance(bid, dict) and 'price' in bid and 'volume' in bid:
                                logger.info(f"    {i+1}: {bid['price']} x {bid['volume']}")
                    else:
                        logger.info("  No bids available")
                        
                    # Process asks
                    asks = order_book['Ask']
                    if asks and len(asks) > 0:
                        logger.info("  Ask:")
                        for i, ask in enumerate(asks[:min(3, len(asks))]):
                            if isinstance(ask, dict) and 'price' in ask and 'volume' in ask:
                                logger.info(f"    {i+1}: {ask['price']} x {ask['volume']}")
                    else:
                        logger.info("  No asks available")
                else:
                    logger.info(f"  Order book data format not as expected: {type(order_book)}")
            else:
                logger.warning(f"No order book data received for {stock_code}")
            
            # Get K-line data
            kline = self.market_data.get_kline(stock_code, ft.KLType.K_DAY, 5)
            if kline is not None and not kline.empty:
                logger.info(f"Recent K-line data for {stock_code}:")
                
                # Check required columns exist
                required_cols = ['time_key', 'open', 'close', 'high', 'low']
                missing_cols = [col for col in required_cols if col not in kline.columns]
                
                if not missing_cols:
                    for i in range(min(5, len(kline))):
                        day = kline.iloc[i]
                        logger.info(f"  {day['time_key']}: Open {day['open']}, Close {day['close']}, High {day['high']}, Low {day['low']}")
                else:
                    logger.warning(f"K-line data missing required columns: {missing_cols}. Available columns: {kline.columns.tolist()}")
                    # Log what we can
                    logger.info(f"K-line data preview: \n{kline.head().to_string()}")
            else:
                logger.warning(f"No K-line data received for {stock_code}")
            
            return True
                
        except Exception as e:
            import traceback
            logger.error(f"Error in quote demo: {str(e)}")
            logger.debug(f"Quote demo exception traceback: {traceback.format_exc()}")
            return False
    
    def run_account_demo(self):
        """Run a simple account demonstration"""
        logger.info("Running account demo")
        
        try:
            # Get account information
            account_info = self.trading.get_account_info()
            if account_info is not None:
                logger.info("Account Information:")
                
                # Handle account_info as either DataFrame or dict
                if isinstance(account_info, pd.DataFrame) and not account_info.empty:
                    # Access using DataFrame syntax
                    cash = account_info['cash'].iloc[0] if 'cash' in account_info.columns else "N/A"
                    total_assets = account_info['total_assets'].iloc[0] if 'total_assets' in account_info.columns else "N/A"
                    market_val = account_info['market_val'].iloc[0] if 'market_val' in account_info.columns else "N/A"
                    power = account_info['power'].iloc[0] if 'power' in account_info.columns else "N/A"
                    
                    logger.info(f"  Cash: {cash}")
                    logger.info(f"  Total Assets: {total_assets}")
                    logger.info(f"  Market Value: {market_val}")
                    logger.info(f"  Buying Power: {power}")
                elif isinstance(account_info, dict):
                    # Access using dict syntax
                    logger.info(f"  Cash: {account_info.get('cash', ['N/A'])[0]}")
                    logger.info(f"  Total Assets: {account_info.get('total_assets', ['N/A'])[0]}")
                    logger.info(f"  Market Value: {account_info.get('market_val', ['N/A'])[0]}")
                    logger.info(f"  Buying Power: {account_info.get('power', ['N/A'])[0]}")
                else:
                    logger.info(f"  Unexpected account info data type: {type(account_info)}")
                    logger.info(f"  Raw account info: {account_info}")
            else:
                logger.warning("No account information received")
            
            # Get positions
            positions = self.trading.get_positions()
            if positions is not None and isinstance(positions, pd.DataFrame) and not positions.empty:
                logger.info("Current Positions:")
                # Check if expected columns exist
                has_required_cols = all(col in positions.columns for col in ['code', 'qty', 'cost_price'])
                
                if has_required_cols:
                    for i in range(len(positions)):
                        pos = positions.iloc[i]
                        logger.info(f"  {pos['code']}: {pos['qty']} shares at {pos['cost_price']}")
                else:
                    logger.info(f"  Positions available columns: {positions.columns.tolist()}")
                    logger.info(f"  Positions data preview: \n{positions.head().to_string()}")
            else:
                logger.info("No current positions")
            
            # Get order list
            orders = self.trading.get_order_list()
            if orders is not None and isinstance(orders, pd.DataFrame) and not orders.empty:
                logger.info("Recent Orders:")
                # Check if expected columns exist
                has_required_cols = all(col in orders.columns for col in ['code', 'qty', 'price', 'status_name'])
                
                if has_required_cols:
                    for i in range(len(orders)):
                        order = orders.iloc[i]
                        logger.info(f"  {order['code']}: {order['qty']} shares at {order['price']}, Status: {order['status_name']}")
                else:
                    logger.info(f"  Orders available columns: {orders.columns.tolist()}")
                    logger.info(f"  Orders data preview: \n{orders.head().to_string()}")
            else:
                logger.info("No recent orders")
                
            return True
                
        except Exception as e:
            import traceback
            logger.error(f"Error in account demo: {str(e)}")
            logger.debug(f"Account demo exception traceback: {traceback.format_exc()}")
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        if self.strategy:
            self.strategy.stop()
        
        if self.conn:
            self.conn.close()
        
        logger.info("Cleanup complete")

def main():
    """Main entry point"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    
    # Setup environment
    setup_environment()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Futu Trading Program')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Quote demo command
    quote_parser = subparsers.add_parser('quote', help='Run quote demo')
    quote_parser.add_argument('stock_code', help='Stock code (e.g., HK.00700)')
    
    # Account demo command
    account_parser = subparsers.add_parser('account', help='Run account demo')
    
    # Strategy command
    strategy_parser = subparsers.add_parser('strategy', help='Run trading strategy')
    strategy_parser.add_argument('strategy_name', choices=['sma'], help='Strategy name')
    strategy_parser.add_argument('stock_code', help='Stock code (e.g., HK.00700)')
    strategy_parser.add_argument('--short-window', type=int, default=10, help='Short moving average window')
    strategy_parser.add_argument('--long-window', type=int, default=30, help='Long moving average window')
    
    # Hash password command
    hash_parser = subparsers.add_parser('hash-pwd', help='Generate MD5 hash for a password')
    hash_parser.add_argument('password', help='Password to hash')
    
    args = parser.parse_args()
    
    # Handle special commands that don't require initialization
    if args.command == 'hash-pwd':
        return 0 if hash_password_cmd(args.password) else 1
    
    # Initialize the trader
    trader = FutuTrader()
    try:
        if not trader.initialize():
            return 1
        
        # Execute the requested command
        if args.command == 'quote':
            trader.run_quote_demo(args.stock_code)
        elif args.command == 'account':
            trader.run_account_demo()
        elif args.command == 'strategy':
            trader.run_strategy(
                args.strategy_name,
                args.stock_code,
                short_window=args.short_window,
                long_window=args.long_window
            )
        else:
            parser.print_help()
            
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        return 1
    finally:
        trader.cleanup()
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 