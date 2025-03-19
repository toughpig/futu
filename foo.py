#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FUTU OpenAPI Test Script
"""

import logging
import time
from futu import *
import os
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FutuAPITest")

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables
HOST = os.getenv('FUTU_OPEND_HOST', '127.0.0.1')
PORT = int(os.getenv('FUTU_OPEND_PORT', '11111'))
TRADE_PWD = os.getenv('FUTU_UNLOCK_TRADE_PWD', '')
TRADING_ENV = os.getenv('TRADING_ENV', 'SIMULATE')
USE_MD5_HASH = os.getenv('USE_MD5_HASH', 'False').lower() in ('true', '1', 't', 'yes')
IS_PASSWORD_HASHED = os.getenv('IS_PASSWORD_HASHED', 'False').lower() in ('true', '1', 't', 'yes')

# Define common constants
TEST_STOCK = 'HK.00700'  # Tencent stock for testing

def print_divider(title):
    """Print a divider with title for better output formatting"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

class TestOrderBookHandler(OrderBookHandlerBase):
    """Handler for order book updates"""
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(TestOrderBookHandler, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            logger.error(f"OrderBookHandler error: {data}")
            return RET_ERROR, data
        
        logger.info(f"Received order book: {data['code']}")
        logger.debug(f"Order book detail: {data}")
        return RET_OK, data

class TestTickerHandler(TickerHandlerBase):
    """Handler for ticker updates"""
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(TestTickerHandler, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            logger.error(f"TickerHandler error: {data}")
            return RET_ERROR, data
        
        logger.info(f"Received ticker: {len(data)} transactions")
        logger.debug(f"Ticker detail: {data}")
        return RET_OK, data

class TestQuoteHandler(StockQuoteHandlerBase):
    """Handler for stock quote updates"""
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(TestQuoteHandler, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            logger.error(f"QuoteHandler error: {data}")
            return RET_ERROR, data
        
        logger.info(f"Received quotes for {len(data)} stocks")
        logger.debug(f"Quote detail: {data}")
        return RET_OK, data

def test_unlock_trade(trd_ctx):
    """Test unlocking trade account"""
    print_divider("Testing Trade Account Unlock")
    
    # Get the password - handle MD5 if needed
    password = TRADE_PWD
    
    try:
        logger.info(f"Attempting to unlock trade account...")
        
        if USE_MD5_HASH and not IS_PASSWORD_HASHED:
            # Add code to hash password if needed
            import hashlib
            password = hashlib.md5(password.encode('utf-8')).hexdigest()
            logger.debug("Password hashed with MD5")
        
        # Different API versions have different parameter sets
        try:
            # First try the newer API version without is_password_md5
            ret, data = trd_ctx.unlock_trade(password=password)
        except Exception as e:
            # If that fails, try the older version with is_password_md5
            logger.debug(f"Newer API unlock failed, trying legacy API: {e}")
            ret, data = trd_ctx.unlock_trade(password=password, is_password_md5=IS_PASSWORD_HASHED)
            
        if ret == RET_OK:
            logger.info("✓ Trade account unlocked successfully")
            return True
        else:
            logger.error(f"✗ Failed to unlock trade account: {data}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Exception when unlocking trade: {e}")
        return False

def test_account_info(trd_ctx):
    """Test getting account information"""
    print_divider("Testing Account Information")
    
    # Define the trading environment
    trd_env = TrdEnv.REAL if TRADING_ENV == 'REAL' else TrdEnv.SIMULATE
    logger.info(f"Using {trd_env} trading environment")
    
    try:
        # 1. Get account information
        logger.info("Fetching account information...")
        ret, data = trd_ctx.accinfo_query(trd_env=trd_env)
        if ret == RET_OK:
            logger.info("✓ Account information retrieved:")
            logger.info(f"  Power: {data['power'][0] if 'power' in data.columns else 'N/A'}")
            logger.info(f"  Total Assets: {data['total_assets'][0] if 'total_assets' in data.columns else 'N/A'}")
            logger.info(f"  Cash: {data['cash'][0] if 'cash' in data.columns else 'N/A'}")
            logger.info(f"  Market Value: {data['market_val'][0] if 'market_val' in data.columns else 'N/A'}")
        else:
            logger.error(f"✗ Failed to get account information: {data}")
        
        # 2. Get positions
        logger.info("Fetching positions...")
        ret, data = trd_ctx.position_list_query(trd_env=trd_env)
        if ret == RET_OK:
            if len(data) > 0:
                logger.info(f"✓ Found {len(data)} positions:")
                for i, row in data.iterrows():
                    logger.info(f"  Position {i+1}: {row['code']} - Qty: {row['qty']} - Market Value: {row['market_val']}")
            else:
                logger.info("✓ No positions found in account")
        else:
            logger.error(f"✗ Failed to get positions: {data}")
        
        # 3. Get orders
        logger.info("Fetching orders...")
        ret, data = trd_ctx.order_list_query(trd_env=trd_env)
        if ret == RET_OK:
            if len(data) > 0:
                logger.info(f"✓ Found {len(data)} orders:")
                for i, row in data.iterrows():
                    logger.info(f"  Order {i+1}: {row['code']} - Status: {row['order_status']} - Qty: {row['qty']}")
            else:
                logger.info("✓ No orders found")
        else:
            logger.error(f"✗ Failed to get orders: {data}")
            
        # 4. Get today's trades
        logger.info("Fetching today's trades...")
        ret, data = trd_ctx.deal_list_query(trd_env=trd_env)
        if ret == RET_OK:
            if len(data) > 0:
                logger.info(f"✓ Found {len(data)} trades today:")
                for i, row in data.iterrows():
                    logger.info(f"  Trade {i+1}: {row['code']} - "
                               f"Side: {row['trd_side']} - "
                               f"Price: {row['price']} - "
                               f"Qty: {row['qty']}")
            else:
                logger.info("✓ No trades found today")
        else:
            logger.error(f"✗ Failed to get today's trades: {data}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Exception when getting account info: {e}")
        return False

def test_real_time_data(quote_ctx):
    """Test subscribing to and retrieving real-time market data"""
    print_divider("Testing Real-time Market Data")
    
    try:
        # 1. Set up handlers for real-time data
        order_book_handler = TestOrderBookHandler()
        ticker_handler = TestTickerHandler()
        quote_handler = TestQuoteHandler()
        
        # Set the handlers on the context
        quote_ctx.set_handler(order_book_handler)
        quote_ctx.set_handler(ticker_handler)
        quote_ctx.set_handler(quote_handler)
        
        # 2. Subscribe to different data types
        logger.info(f"Subscribing to {TEST_STOCK}...")
        ret, data = quote_ctx.subscribe(
            [TEST_STOCK], 
            [SubType.QUOTE, SubType.ORDER_BOOK, SubType.TICKER]
        )
        
        if ret != RET_OK:
            logger.error(f"✗ Failed to subscribe: {data}")
            return False
            
        logger.info(f"✓ Successfully subscribed to {TEST_STOCK}")
        
        # 3. Get basic quotes
        logger.info("Fetching real-time quote...")
        ret, data = quote_ctx.get_stock_quote([TEST_STOCK])
        if ret == RET_OK:
            logger.info(f"✓ Real-time quote for {TEST_STOCK}:")
            if len(data) > 0:
                logger.info(f"  Last Price: {data['last_price'][0] if 'last_price' in data.columns else 'N/A'}")
                logger.info(f"  Open: {data['open_price'][0] if 'open_price' in data.columns else 'N/A'}")
                logger.info(f"  High: {data['high_price'][0] if 'high_price' in data.columns else 'N/A'}")
                logger.info(f"  Low: {data['low_price'][0] if 'low_price' in data.columns else 'N/A'}")
                logger.info(f"  Volume: {data['volume'][0] if 'volume' in data.columns else 'N/A'}")
        else:
            logger.error(f"✗ Failed to get real-time quote: {data}")
        
        # 4. Get order book (maker/taker)
        logger.info("Fetching order book (bid/ask)...")
        ret, data = quote_ctx.get_order_book(TEST_STOCK, num=5)  # Get 5 levels
        if ret == RET_OK:
            logger.info(f"✓ Order book for {TEST_STOCK}:")
            
            # Bids (Buyers)
            bids = data['Bid'] if 'Bid' in data else []
            if bids and len(bids) > 0:
                logger.info("  Bid (Buyers):")
                for i, bid in enumerate(bids):
                    if isinstance(bid, tuple) and len(bid) >= 2:
                        logger.info(f"    {i+1}: Price: {bid[0]}, Volume: {bid[1]}, Orders: {bid[2] if len(bid) > 2 else 'N/A'}")
            else:
                logger.info("  No bids available")
                
            # Asks (Sellers)
            asks = data['Ask'] if 'Ask' in data else []
            if asks and len(asks) > 0:
                logger.info("  Ask (Sellers):")
                for i, ask in enumerate(asks):
                    if isinstance(ask, tuple) and len(ask) >= 2:
                        logger.info(f"    {i+1}: Price: {ask[0]}, Volume: {ask[1]}, Orders: {ask[2] if len(ask) > 2 else 'N/A'}")
            else:
                logger.info("  No asks available")
        else:
            logger.error(f"✗ Failed to get order book: {data}")
        
        # 5. Get recent transactions
        logger.info("Fetching recent transactions...")
        ret, data = quote_ctx.get_rt_ticker(TEST_STOCK, num=10)  # Get last 10 tickers
        if ret == RET_OK:
            if len(data) > 0:
                logger.info(f"✓ Recent transactions for {TEST_STOCK}:")
                for i, row in data.iterrows():
                    logger.info(f"  {i+1}: Time: {row['time'] if 'time' in data.columns else 'N/A'}, "
                              f"Price: {row['price'] if 'price' in data.columns else 'N/A'}, "
                              f"Volume: {row['volume'] if 'volume' in data.columns else 'N/A'}, "
                              f"Type: {row['type'] if 'type' in data.columns else 'N/A'}")
            else:
                logger.info("  No recent transactions found")
        else:
            logger.error(f"✗ Failed to get recent transactions: {data}")
                
        # Wait for a few seconds to receive real-time updates via handlers
        logger.info("Waiting for 5 seconds to receive real-time updates...")
        time.sleep(5)
        
        # 6. Unsubscribe
        logger.info("Unsubscribing...")
        ret, data = quote_ctx.unsubscribe_all()
        if ret == RET_OK:
            logger.info("✓ Successfully unsubscribed from all feeds")
        else:
            logger.error(f"✗ Failed to unsubscribe: {data}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Exception when testing real-time data: {e}")
        return False

def run_tests():
    """Run all tests"""
    print_divider("FUTU OpenAPI Test Script")
    logger.info(f"Connecting to FUTU OpenD at {HOST}:{PORT}")
    
    # Initialize contexts
    quote_ctx = None
    trd_ctx = None
    
    try:
        # Initialize quote context
        quote_ctx = OpenQuoteContext(host=HOST, port=PORT)
        logger.info("✓ Quote context initialized")
        
        # Initialize trade context
        trd_ctx = OpenSecTradeContext(host=HOST, port=PORT)
        logger.info("✓ Trade context initialized")
        
        # Test 1: Unlock trade account
        unlock_success = test_unlock_trade(trd_ctx)
        
        # Test 2: Get account information (only if unlock was successful)
        if unlock_success:
            test_account_info(trd_ctx)
        else:
            logger.warning("⚠ Skipping account info test because trade unlock failed")
        
        # Test 3: Subscribe to and retrieve real-time data
        test_real_time_data(quote_ctx)
        
        logger.info("All tests completed")
        return True
        
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        return False
        
    finally:
        # Clean up
        if quote_ctx:
            quote_ctx.close()
            logger.info("Quote context closed")
            
        if trd_ctx:
            trd_ctx.close()
            logger.info("Trade context closed")

if __name__ == "__main__":
    run_tests()
