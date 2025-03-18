import logging
import time
import abc
import pandas as pd
import futu as ft
from market_data import MarketData
from trading import Trading

logger = logging.getLogger("FutuTrader")

class Strategy(abc.ABC):
    """
    Abstract base class for trading strategies
    """
    
    def __init__(self, market_data, trading):
        """
        Initialize with market data and trading services
        
        Args:
            market_data: MarketData instance
            trading: Trading instance
        """
        self.market_data = market_data
        self.trading = trading
        self.running = False
        self.name = self.__class__.__name__
    
    @abc.abstractmethod
    def setup(self):
        """
        Initialize strategy-specific settings
        Returns:
            bool: Success or failure
        """
        pass
    
    @abc.abstractmethod
    def process_data(self):
        """
        Process market data and generate signals
        Returns:
            dict: Signal information or None
        """
        pass
    
    @abc.abstractmethod
    def execute_signal(self, signal):
        """
        Execute a trading signal
        
        Args:
            signal: Signal information
        
        Returns:
            bool: Success or failure
        """
        pass
    
    def start(self):
        """Start strategy execution"""
        if self.running:
            logger.warning(f"Strategy {self.name} already running")
            return
            
        logger.info(f"Starting strategy: {self.name}")
        self.running = True
        
        # Execute strategy setup
        if not self.setup():
            logger.error(f"Failed to setup strategy: {self.name}")
            self.running = False
            return
            
        # Main strategy loop
        try:
            while self.running:
                # Process data and generate signals
                signal = self.process_data()
                
                # Execute signals if any
                if signal:
                    self.execute_signal(signal)
                    
                # Sleep to avoid high CPU usage
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Strategy execution interrupted")
        except Exception as e:
            logger.error(f"Error in strategy execution: {str(e)}")
        finally:
            self.running = False
            logger.info(f"Strategy stopped: {self.name}")
    
    def stop(self):
        """Stop strategy execution"""
        if not self.running:
            logger.warning(f"Strategy {self.name} not running")
            return
            
        logger.info(f"Stopping strategy: {self.name}")
        self.running = False


class SimpleMovingAverageStrategy(Strategy):
    """
    Simple Moving Average crossover strategy
    
    Buy when short MA crosses above long MA
    Sell when short MA crosses below long MA
    """
    
    def __init__(self, market_data, trading):
        super().__init__(market_data, trading)
        self.stock_code = None
        self.short_window = 10
        self.long_window = 30
        self.last_position = 0  # 0: no position, 1: long position
        
    def setup(self, stock_code, short_window=10, long_window=30):
        """
        Initialize strategy parameters
        
        Args:
            stock_code: Stock code to trade (e.g., 'HK.00700')
            short_window: Short moving average period
            long_window: Long moving average period
            
        Returns:
            bool: Success or failure
        """
        self.stock_code = stock_code
        self.short_window = short_window
        self.long_window = long_window
        
        # Subscribe to market data
        success = self.market_data.subscribe_stock(self.stock_code)
        if not success:
            logger.error(f"Failed to subscribe to {self.stock_code}")
            return False
            
        logger.info(f"Strategy setup complete: {self.name} for {self.stock_code}")
        logger.info(f"Parameters: short_window={self.short_window}, long_window={self.long_window}")
        return True
        
    def process_data(self):
        """
        Process market data and generate trading signals
        
        Returns:
            dict: Signal information or None
        """
        # Get historical data for moving averages
        kline_data = self.market_data.get_kline(
            self.stock_code, 
            ktype=ft.KLType.K_DAY, 
            count=self.long_window + 10
        )
        
        if kline_data is None or len(kline_data) < self.long_window:
            logger.warning(f"Insufficient data for {self.stock_code}")
            return None
            
        # Calculate moving averages
        kline_data['short_ma'] = kline_data['close'].rolling(window=self.short_window).mean()
        kline_data['long_ma'] = kline_data['close'].rolling(window=self.long_window).mean()
        
        # Get the most recent values
        current = kline_data.iloc[-1]
        previous = kline_data.iloc[-2]
        
        # Check for crossover
        current_crossover = current['short_ma'] > current['long_ma']
        previous_crossover = previous['short_ma'] > previous['long_ma']
        
        # Generate signals
        signal = None
        if current_crossover and not previous_crossover:
            # Bullish crossover (short MA crosses above long MA)
            if self.last_position != 1:  # Not already in a long position
                signal = {
                    'action': 'BUY',
                    'price': current['close'],
                    'reason': 'Bullish MA crossover'
                }
        elif not current_crossover and previous_crossover:
            # Bearish crossover (short MA crosses below long MA)
            if self.last_position == 1:  # Currently in a long position
                signal = {
                    'action': 'SELL',
                    'price': current['close'],
                    'reason': 'Bearish MA crossover'
                }
                
        return signal
        
    def execute_signal(self, signal):
        """
        Execute a trading signal
        
        Args:
            signal: Signal information
            
        Returns:
            bool: Success or failure
        """
        if not signal or 'action' not in signal:
            return False
            
        # Get account information
        account_info = self.trading.get_account_info()
        if account_info is None:
            logger.error("Failed to get account information")
            return False
            
        # Get current positions
        positions = self.trading.get_positions()
        if positions is None:
            logger.error("Failed to get positions")
            return False
            
        # Check if we already have a position in this stock
        has_position = False
        position_qty = 0
        if not positions.empty:
            stock_positions = positions[positions['code'] == self.stock_code]
            if not stock_positions.empty:
                has_position = True
                position_qty = stock_positions['qty'].iloc[0]
        
        if signal['action'] == 'BUY':
            # Only buy if we don't already have a position
            if has_position:
                logger.info(f"Already have position in {self.stock_code}, skipping buy")
                return False
                
            # Calculate quantity based on available cash
            cash = float(account_info['power'][0])  # Available cash for trading
            price = signal['price']
            max_qty = int(cash / price / 100) * 100  # Round to nearest lot size
            
            if max_qty < 100:
                logger.warning(f"Insufficient funds to buy {self.stock_code}")
                return False
                
            # Place buy order
            result = self.trading.place_order(
                stock_code=self.stock_code,
                price=price,
                qty=max_qty,
                order_type=ft.OrderType.NORMAL,
                direction=ft.TrdSide.BUY
            )
            
            if result is not None:
                logger.info(f"Buy order placed for {self.stock_code}: {max_qty} shares at {price}")
                self.last_position = 1
                return True
            else:
                logger.error(f"Failed to place buy order for {self.stock_code}")
                return False
                
        elif signal['action'] == 'SELL':
            # Only sell if we have a position
            if not has_position or position_qty <= 0:
                logger.info(f"No position in {self.stock_code}, skipping sell")
                return False
                
            # Place sell order for all shares
            result = self.trading.place_order(
                stock_code=self.stock_code,
                price=signal['price'],
                qty=position_qty,
                order_type=ft.OrderType.NORMAL,
                direction=ft.TrdSide.SELL
            )
            
            if result is not None:
                logger.info(f"Sell order placed for {self.stock_code}: {position_qty} shares at {signal['price']}")
                self.last_position = 0
                return True
            else:
                logger.error(f"Failed to place sell order for {self.stock_code}")
                return False
        
        return False 