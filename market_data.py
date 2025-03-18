import logging
import pandas as pd
import futu as ft
from connection import FutuConnection

logger = logging.getLogger("FutuTrader")

class MarketData:
    """Handles market data operations"""
    
    def __init__(self, connection):
        """
        Initialize with a FutuConnection
        
        Args:
            connection: FutuConnection instance
        """
        self.conn = connection
        
    def get_stock_quote(self, stock_code):
        """
        Get real-time quote for a stock
        
        Args:
            stock_code: Stock code with prefix (e.g., 'HK.00700')
        
        Returns:
            pandas.DataFrame with quote data or None if error
        """
        if not self.conn.connected:
            logger.error("Not connected to OpenD")
            return None
            
        ret, data = self.conn.quote_ctx.get_stock_quote([stock_code])
        if ret != ft.RET_OK:
            logger.error(f"Failed to get stock quote: {data}")
            return None
            
        return data
    
    def get_market_snapshot(self, stock_codes):
        """
        Get market snapshot for multiple stocks
        
        Args:
            stock_codes: List of stock codes with prefix
        
        Returns:
            pandas.DataFrame with snapshot data or None if error
        """
        if not self.conn.connected:
            logger.error("Not connected to OpenD")
            return None
            
        ret, data = self.conn.quote_ctx.get_market_snapshot(stock_codes)
        if ret != ft.RET_OK:
            logger.error(f"Failed to get market snapshot: {data}")
            return None
            
        return data
    
    def get_kline(self, stock_code, ktype=ft.KLType.K_DAY, count=100):
        """
        Get K-line data for a stock
        
        Args:
            stock_code: Stock code with prefix (e.g., 'HK.00700')
            ktype: K-line type (e.g., ft.KLType.K_DAY, ft.KLType.K_1M)
            count: Number of K-line points to retrieve
        
        Returns:
            pandas.DataFrame with K-line data or None if error
        """
        if not self.conn.connected:
            logger.error("Not connected to OpenD")
            return None
            
        try:
            logger.debug(f"Getting K-line data for {stock_code}, type={ktype}, count={count}")
            
            # In the latest Futu API, request_history_kline may return different value formats
            try:
                result = self.conn.quote_ctx.request_history_kline(
                    code=stock_code, 
                    ktype=ktype, 
                    autype=ft.AuType.QFQ,  # 使用前复权
                    max_count=count,  # 改用max_count参数
                    extended_time=False
                )
                
                # Handle different return formats
                if isinstance(result, tuple) and len(result) >= 2:
                    ret, data = result[0], result[1]
                else:
                    logger.error(f"Unexpected return format from request_history_kline: {type(result)}")
                    return None
            except ValueError as ve:
                logger.error(f"ValueError in request_history_kline: {ve}")
                # Try alternative approach for older API versions
                logger.info("Trying alternative API call format...")
                ret, data = self.conn.quote_ctx.request_history_kline(
                    code=stock_code, 
                    ktype=ktype, 
                    autype=ft.AuType.QFQ,
                    start=None,  # 不指定开始时间
                    end=None,    # 不指定结束时间
                    max_count=count,
                    extended_time=False
                )
            
            if ret != ft.RET_OK:
                logger.error(f"Failed to get K-line data: {data}")
                return None
                
            # Verify data structure
            if data is None:
                logger.warning(f"K-line data is None for {stock_code}")
                return None
                
            # Check if data is a DataFrame
            if not isinstance(data, pd.DataFrame):
                logger.warning(f"K-line data is not a DataFrame, but {type(data)}")
                # Try to convert to DataFrame if possible
                if isinstance(data, (list, tuple)):
                    try:
                        return pd.DataFrame(data)
                    except Exception as e:
                        logger.error(f"Failed to convert K-line data to DataFrame: {e}")
                        return None
                return None
                
            # Log column info for debugging
            logger.debug(f"K-line columns: {data.columns.tolist()}")
            logger.debug(f"K-line data shape: {data.shape}")
                
            return data
            
        except Exception as e:
            import traceback
            logger.error(f"Error getting K-line data for {stock_code}: {str(e)}")
            logger.debug(f"K-line exception traceback: {traceback.format_exc()}")
            return None
    
    def get_order_book(self, stock_code, num=10):
        """
        Get order book (bid/ask) for a stock
        
        Args:
            stock_code: Stock code with prefix (e.g., 'HK.00700')
            num: Number of levels to retrieve
        
        Returns:
            dict with order book data or None if error
        """
        if not self.conn.connected:
            logger.error("Not connected to OpenD")
            return None
            
        try:
            logger.debug(f"Getting order book for {stock_code} with {num} levels")
            ret, data = self.conn.quote_ctx.get_order_book(stock_code, num)
            if ret != ft.RET_OK:
                logger.error(f"Failed to get order book: {data}")
                return None
                
            # Verify data structure
            logger.debug(f"Order book data type: {type(data)}")
            
            # Handle different data structures returned by Futu API
            if isinstance(data, dict):
                if 'Bid' in data and 'Ask' in data:
                    return {
                        'Bid': data['Bid'],
                        'Ask': data['Ask']
                    }
                else:
                    logger.warning(f"Order book data missing expected keys. Keys: {data.keys()}")
                    return data
            elif isinstance(data, tuple):
                logger.warning(f"Order book returned tuple instead of dict. len={len(data)}")
                # Try to extract meaningful data
                if len(data) >= 2:
                    return {
                        'Bid': data[0],
                        'Ask': data[1]
                    }
                return {'data': data}
            else:
                logger.warning(f"Unexpected order book data type: {type(data)}")
                return {'data': data}
                
        except Exception as e:
            import traceback
            logger.error(f"Error getting order book for {stock_code}: {str(e)}")
            logger.debug(f"Order book exception traceback: {traceback.format_exc()}")
            return None
    
    def subscribe_stock(self, stock_code, data_types=None):
        """
        Subscribe to real-time data for a stock
        
        Args:
            stock_code: Stock code with prefix (e.g., 'HK.00700')
            data_types: List of data types to subscribe to
        
        Returns:
            bool: Success or failure
        """
        if not self.conn.connected:
            logger.error("Not connected to OpenD")
            return False
            
        try:
            if data_types is None:
                data_types = [ft.SubType.QUOTE, ft.SubType.ORDER_BOOK, ft.SubType.TICKER]
            
            logger.debug(f"Subscribing to {stock_code} for data types: {data_types}")
            
            # First check if the stock exists
            ret_check, data_check = self.conn.quote_ctx.get_stock_basicinfo(
                market=ft.Market.HK if stock_code.startswith('HK.') else 
                      ft.Market.US if stock_code.startswith('US.') else
                      ft.Market.SH_SZ if stock_code.startswith(('SH.', 'SZ.')) else
                      ft.Market.HK,
                code_list=[stock_code]
            )
            
            if ret_check != ft.RET_OK:
                logger.warning(f"Stock validation failed for {stock_code}: {data_check}")
                # Continue despite validation error - the stock might still be valid
            elif len(data_check) == 0:
                logger.warning(f"Stock {stock_code} not found in basic info")
                # Continue despite warning
                
            # Try to subscribe
            ret, data = self.conn.quote_ctx.subscribe([stock_code], data_types)
            if ret != ft.RET_OK:
                error_msg = str(data)
                
                # Special handling for common errors
                if "subscribe count exceeds limit" in error_msg:
                    logger.error(f"Subscription limit exceeded. Try reducing the number of subscriptions.")
                elif "stock not found" in error_msg:
                    logger.error(f"Stock {stock_code} not found. Check the stock code format (e.g., HK.00700).")
                else:
                    logger.error(f"Failed to subscribe: {error_msg}")
                    
                return False
                
            logger.info(f"Subscribed to {stock_code} for {data_types}")
            return True
            
        except Exception as e:
            import traceback
            logger.error(f"Error subscribing to {stock_code}: {str(e)}")
            logger.debug(f"Subscription exception: {traceback.format_exc()}")
            return False
    
    def search_stocks(self, market, keyword):
        """
        Search for stocks by keyword
        
        Args:
            market: Market code (e.g., 'HK', 'US')
            keyword: Search keyword
        
        Returns:
            pandas.DataFrame with search results or None if error
        """
        if not self.conn.connected:
            logger.error("Not connected to OpenD")
            return None
            
        ret, data = self.conn.quote_ctx.search_stocks(keyword, ft.StockSearchType.STOCK_SEARCH_KEY_WORD, market)
        if ret != ft.RET_OK:
            logger.error(f"Failed to search stocks: {data}")
            return None
            
        return data 