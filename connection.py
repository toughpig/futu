from futu import OpenQuoteContext, OpenHKTradeContext, OpenUSTradeContext, OpenCNTradeContext, RspHandlerBase
import futu as ft
import config
import logging
import hashlib
from utils import hash_password

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FutuTrader")

class FutuConnection:
    """Manages connection to Futu OpenD"""
    
    def __init__(self):
        self.quote_ctx = None
        self.trade_ctx = None
        self.connected = False
        self.market = config.DEFAULT_MARKET
        
    def connect(self):
        """Establish connection to OpenD"""
        try:
            # Connect to quote context
            logger.debug(f"Connecting to OpenD at {config.OPEND_HOST}:{config.OPEND_PORT}")
            self.quote_ctx = OpenQuoteContext(host=config.OPEND_HOST, port=config.OPEND_PORT)
            
            # Select appropriate trade context based on market
            if self.market == 'HK':
                self.trade_ctx = OpenHKTradeContext(host=config.OPEND_HOST, port=config.OPEND_PORT)
            elif self.market == 'US':
                self.trade_ctx = OpenUSTradeContext(host=config.OPEND_HOST, port=config.OPEND_PORT)
            elif self.market in ['CN', 'SH', 'SZ']:
                self.trade_ctx = OpenCNTradeContext(host=config.OPEND_HOST, port=config.OPEND_PORT)
            else:
                raise ValueError(f"Unsupported market: {self.market}")
            
            # Check OpenD version and connection status
            logger.debug("Checking OpenD connection status...")
            ret, data = self.quote_ctx.get_global_state()
            if ret != ft.RET_OK:
                logger.error(f"Failed to get OpenD state: {data}")
                return False
                
            # Log connection success with available info
            logger.debug(f"OpenD state response: {data}")
            
            if isinstance(data, dict):
                version = data.get('ver', 'unknown')
                qot_logined = data.get('qot_logined', False)
                trd_logined = data.get('trd_logined', False)
                
                logger.info(f"Connected to OpenD version: {version}")
                logger.info(f"Quote login status: {qot_logined}")
                logger.info(f"Trade login status: {trd_logined}")
            else:
                logger.info(f"Connected to OpenD. Response type: {type(data)}")
                
            self.connected = True
            return True
            
        except Exception as e:
            import traceback
            logger.error(f"Error connecting to OpenD: {str(e)}")
            logger.debug(f"Exception traceback: {traceback.format_exc()}")
            self.close()
            return False
    
    def unlock_trade(self):
        """Unlock trade with trade password"""
        if not self.connected or not self.trade_ctx:
            logger.error("Not connected to OpenD")
            return False
            
        if not config.UNLOCK_TRADE_PWD:
            logger.error("Trade password not configured")
            return False
            
        try:
            # Apply MD5 hashing if needed
            password = config.UNLOCK_TRADE_PWD
            # hash_password(
            #     config.UNLOCK_TRADE_PWD, 
            #     use_md5=config.USE_MD5_HASH, 
            #     is_already_hashed=config.IS_PASSWORD_HASHED
            # )
            
            logger.debug(f"Attempting to unlock trade (password length: {len(password)})")
            
            # 较新版本的Futu API不再支持is_password_md5参数
            try:
                # 首先尝试新版API的调用方式
                ret, data = self.trade_ctx.unlock_trade(password=password)
                
            except Exception as api_err:
                # 如果新版失败，尝试旧版API的调用方式
                logger.debug(f"New API call failed, trying legacy API call: {str(api_err)}")
                ret, data = self.trade_ctx.unlock_trade(
                    password=password,
                    is_password_md5=config.IS_PASSWORD_HASHED
                )
                
            if ret != ft.RET_OK:
                logger.error(f"Failed to unlock trade: {data}, ret: {ret}")
                return False
                
            logger.info("Trade unlocked successfully")
            return True
            
        except Exception as e:
            import traceback
            logger.error(f"Error unlocking trade: {str(e)}")
            logger.debug(f"Unlock exception traceback: {traceback.format_exc()}")
            return False
    
    def set_market(self, market):
        """Change the current market"""
        if market not in config.MARKET_MAP:
            logger.error(f"Unsupported market: {market}")
            return False
            
        self.market = config.MARKET_MAP[market]
        logger.info(f"Market set to {self.market}")
        
        # Reconnect if already connected
        if self.connected:
            self.close()
            return self.connect()
        return True
    
    def close(self):
        """Close connections"""
        if self.quote_ctx:
            self.quote_ctx.close()
        if self.trade_ctx:
            self.trade_ctx.close()
        self.connected = False
        logger.info("Connection closed")
        
    def __del__(self):
        """Destructor to ensure connections are closed"""
        self.close() 