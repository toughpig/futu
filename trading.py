import logging
import futu as ft
import hashlib
from connection import FutuConnection
import config
import pandas as pd

logger = logging.getLogger("FutuTrader")

class Trading:
    """Handles trading operations"""
    
    def __init__(self, connection):
        """
        Initialize with a FutuConnection
        
        Args:
            connection: FutuConnection instance
        """
        self.conn = connection
    
    def place_order(self, stock_code, price, qty, order_type, direction):
        """
        Place a trade order
        
        Args:
            stock_code: Stock code with prefix (e.g., 'HK.00700')
            price: Order price
            qty: Order quantity
            order_type: Order type (e.g., ft.OrderType.NORMAL, ft.OrderType.ABSOLUTE_LIMIT)
            direction: Order direction (e.g., ft.TrdSide.BUY, ft.TrdSide.SELL)
        
        Returns:
            dict with order data or None if error
        """
        if not self.conn.connected:
            logger.error("Not connected to OpenD")
            return None
            
        # Unlock trade if needed
        if not self.conn.unlock_trade():
            return None
            
        try:
            # Get trd_market from stock code prefix
            market_prefix = stock_code.split('.')[0] if '.' in stock_code else 'HK'
            trd_market = getattr(ft.TrdMarket, market_prefix) if hasattr(ft.TrdMarket, market_prefix) else ft.TrdMarket.HK
            
            # Determine trading environment from config
            trd_env = ft.TrdEnv.REAL if config.TRADING_ENV == 'REAL' else ft.TrdEnv.SIMULATE
            
            logger.debug(f"Placing order: stock={stock_code}, price={price}, qty={qty}, " 
                         f"order_type={order_type}, direction={direction}, market={trd_market}, "
                         f"environment={trd_env}")
            
            # In newer Futu API versions, we need to specify all parameters explicitly
            ret, data = self.conn.trade_ctx.place_order(
                price=price,
                qty=qty,
                code=stock_code,
                trd_side=direction,
                order_type=order_type,
                trd_env=trd_env,  # Use configured trading environment
                remark=''  # Optional remark for the order
            )
            
            if ret != ft.RET_OK:
                logger.error(f"Failed to place order: {data}")
                return None
                
            logger.info(f"Order placed: {data}")
            return data
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return None
    
    def cancel_order(self, order_id):
        """
        Cancel an existing order
        
        Args:
            order_id: Order ID to cancel
        
        Returns:
            bool: Success or failure
        """
        if not self.conn.connected:
            logger.error("Not connected to OpenD")
            return False
            
        # Unlock trade if needed
        if not self.conn.unlock_trade():
            return False
            
        try:
            logger.debug(f"Cancelling order: {order_id}")
            # Determine trading environment from config
            trd_env = ft.TrdEnv.REAL if config.TRADING_ENV == 'REAL' else ft.TrdEnv.SIMULATE
            
            ret, data = self.conn.trade_ctx.modify_order(
                modify_order_op=ft.ModifyOrderOp.CANCEL,
                order_id=order_id,
                qty=0,
                price=0,
                trd_env=trd_env  # Specify trading environment
            )
            
            if ret != ft.RET_OK:
                logger.error(f"Failed to cancel order: {data}")
                return False
                
            logger.info(f"Order cancelled: {order_id}")
            return True
        except Exception as e:
            logger.error(f"Error cancelling order: {str(e)}")
            return False
    
    def modify_order(self, order_id, price=None, qty=None):
        """
        Modify an existing order
        
        Args:
            order_id: Order ID to modify
            price: New price or None to keep current
            qty: New quantity or None to keep current
        
        Returns:
            bool: Success or failure
        """
        if not self.conn.connected:
            logger.error("Not connected to OpenD")
            return False
            
        # Unlock trade if needed
        if not self.conn.unlock_trade():
            return False
            
        # Determine trading environment from config
        trd_env = ft.TrdEnv.REAL if config.TRADING_ENV == 'REAL' else ft.TrdEnv.SIMULATE
            
        # Get current order info
        try:
            ret, data = self.conn.trade_ctx.order_list_query(
                trd_env=trd_env
            )
            if ret != ft.RET_OK:
                logger.error(f"Failed to get order list: {data}")
                return False
        except Exception as e:
            logger.error(f"Error getting order list: {str(e)}")
            return False
            
        # Find the order in the list
        try:
            order_info = data[data['order_id'] == order_id] if 'order_id' in data.columns else None
            if order_info is None or order_info.empty:
                logger.error(f"Order not found: {order_id}")
                return False
                
            # Use existing values if not provided
            if price is None:
                price = float(order_info['price'].iloc[0])
            if qty is None:
                qty = int(order_info['qty'].iloc[0])
        except Exception as e:
            logger.error(f"Error processing order data: {str(e)}")
            return False
            
        try:
            logger.debug(f"Modifying order {order_id}: price={price}, qty={qty}")
            ret, data = self.conn.trade_ctx.modify_order(
                modify_order_op=ft.ModifyOrderOp.NORMAL,
                order_id=order_id,
                price=price,
                qty=qty,
                trd_env=trd_env  # Specify trading environment
            )
            
            if ret != ft.RET_OK:
                logger.error(f"Failed to modify order: {data}")
                return False
                
            logger.info(f"Order modified: {order_id}, price={price}, qty={qty}")
            return True
        except Exception as e:
            logger.error(f"Error modifying order: {str(e)}")
            return False
    
    def get_order_list(self, status_filter=None, stock_code=None):
        """
        Get list of orders
        
        Args:
            status_filter: Filter by order status or None for all
            stock_code: Optional stock code to filter orders
        
        Returns:
            pandas.DataFrame with order data or None if error
        """
        if not self.conn.connected:
            logger.error("Not connected to OpenD")
            return None
            
        try:
            logger.debug(f"Getting order list with filter: {status_filter}{', code: '+stock_code if stock_code else ''}")
            # Determine trading environment from config
            trd_env = ft.TrdEnv.REAL if config.TRADING_ENV == 'REAL' else ft.TrdEnv.SIMULATE
            
            # 获取账户列表，以便找到正确的acc_id
            try:
                ret, accounts = self.conn.trade_ctx.get_acc_list()
                if ret != ft.RET_OK:
                    logger.warning(f"Failed to get account list: {accounts}")
                else:
                    logger.debug(f"Got {len(accounts)} accounts")
            except Exception as e:
                logger.warning(f"Error getting account list: {str(e)}")
                accounts = None
                
            # 尝试找到匹配环境的账户ID
            acc_id = 0
            if accounts is not None and isinstance(accounts, pd.DataFrame) and not accounts.empty:
                # 尝试找到与当前交易环境匹配的账户
                matching_accounts = accounts[accounts['trd_env'] == trd_env] if 'trd_env' in accounts.columns else pd.DataFrame()
                if not matching_accounts.empty:
                    acc_id = matching_accounts['acc_id'].iloc[0]
                    logger.debug(f"Using matching account ID: {acc_id}")
                else:
                    # 使用第一个可用账户
                    acc_id = accounts['acc_id'].iloc[0]
                    logger.debug(f"Using first available account ID: {acc_id}")
            
            # Create filter list if status filter is provided
            status_filter_list = [status_filter] if status_filter is not None else []
            
            # 尝试不同的参数组合
            try:
                # 完整参数调用
                logger.debug(f"Querying orders with trd_env={trd_env}, acc_id={acc_id}, code={stock_code}")
                ret, data = self.conn.trade_ctx.order_list_query(
                    code=stock_code if stock_code else '',
                    status_filter_list=status_filter_list,
                    trd_env=trd_env,
                    acc_id=acc_id
                )
            except TypeError as te:
                # 某些参数可能不受支持，尝试更简单的调用
                logger.debug(f"Full parameter call not supported: {te}, trying simplified call")
                try:
                    # 不带code参数的调用
                    ret, data = self.conn.trade_ctx.order_list_query(
                        status_filter_list=status_filter_list,
                        trd_env=trd_env,
                        acc_id=acc_id
                    )
                except Exception as e2:
                    # 最基本的调用
                    logger.debug(f"Simplified call failed: {e2}, using basic call")
                    ret, data = self.conn.trade_ctx.order_list_query(
                        status_filter_list=status_filter_list,
                        trd_env=trd_env
                    )
            
            if ret != ft.RET_OK:
                error_msg = str(data)
                logger.error(f"Failed to get order list: {error_msg}")
                
                # 处理常见错误
                if "Nonexisting acc_id" in error_msg:
                    logger.warning(f"账户ID {acc_id} 不存在，请检查账户配置")
                elif "API not ready" in error_msg or "Network failed" in error_msg:
                    logger.warning("API连接问题，请检查与OpenD的连接")
                
                return None
            
            # 添加数据验证和详细的日志记录
            if data is None:
                logger.warning("API返回的订单数据为None")
                return pd.DataFrame()  # 返回空DataFrame而不是None
                
            if not isinstance(data, pd.DataFrame):
                logger.warning(f"API返回的订单数据类型不是DataFrame: {type(data)}")
                try:
                    # 尝试转换为DataFrame
                    if isinstance(data, (list, dict)):
                        data = pd.DataFrame(data)
                    else:
                        logger.error(f"无法将类型 {type(data)} 转换为DataFrame")
                        return pd.DataFrame()
                except Exception as conv_err:
                    logger.error(f"转换订单数据至DataFrame失败: {str(conv_err)}")
                    return pd.DataFrame()
            
            # 检查数据是否为空
            if data.empty:
                logger.info("账户没有订单")
                return data
                
            logger.debug(f"Got order list with {len(data)} orders")    
            logger.debug(f"Order columns: {data.columns.tolist()}")
            
            return data
        except Exception as e:
            logger.error(f"Error getting order list: {str(e)}")
            return None
    
    def get_positions(self, stock_code=None):
        """
        Get current positions
        
        Args:
            stock_code: Optional stock code to filter positions
        
        Returns:
            pandas.DataFrame with position data or None if error
        """
        if not self.conn.connected:
            logger.error("Not connected to OpenD")
            return None
            
        try:
            logger.debug(f"Getting positions{' for '+stock_code if stock_code else ''}")
            # Determine trading environment from config
            trd_env = ft.TrdEnv.REAL if config.TRADING_ENV == 'REAL' else ft.TrdEnv.SIMULATE
            
            # 获取账户列表，以便找到正确的acc_id
            try:
                ret, accounts = self.conn.trade_ctx.get_acc_list()
                if ret != ft.RET_OK:
                    logger.warning(f"Failed to get account list: {accounts}")
                else:
                    logger.debug(f"Got {len(accounts)} accounts")
            except Exception as e:
                logger.warning(f"Error getting account list: {str(e)}")
                accounts = None
                
            # 尝试找到匹配环境的账户ID
            acc_id = 0
            if accounts is not None and isinstance(accounts, pd.DataFrame) and not accounts.empty:
                # 尝试找到与当前交易环境匹配的账户
                matching_accounts = accounts[accounts['trd_env'] == trd_env] if 'trd_env' in accounts.columns else pd.DataFrame()
                if not matching_accounts.empty:
                    acc_id = matching_accounts['acc_id'].iloc[0]
                    logger.debug(f"Using matching account ID: {acc_id}")
                else:
                    # 使用第一个可用账户
                    acc_id = accounts['acc_id'].iloc[0]
                    logger.debug(f"Using first available account ID: {acc_id}")
            
            # 根据API文档设置参数
            try:
                # 完整参数调用
                logger.debug(f"Querying positions with trd_env={trd_env}, acc_id={acc_id}, code={stock_code}")
                ret, data = self.conn.trade_ctx.position_list_query(
                    code=stock_code if stock_code else '',  # 过滤特定股票代码
                    position_market=ft.TrdMarket.HK,  # 指定香港市场
                    trd_env=trd_env,  # 交易环境
                    acc_id=acc_id,  # 账户ID
                    refresh_cache=True  # 刷新缓存获取最新数据
                )
            except TypeError as te:
                # 某些参数可能不受支持，尝试更简单的调用
                logger.debug(f"Full parameter call not supported: {te}, trying simplified call")
                try:
                    # 简化参数但仍包含关键参数
                    ret, data = self.conn.trade_ctx.position_list_query(
                        code=stock_code if stock_code else '',
                        trd_env=trd_env,
                        acc_id=acc_id
                    )
                except Exception as e2:
                    # 最基本的调用
                    logger.debug(f"Simplified call failed: {e2}, using basic call")
                    ret, data = self.conn.trade_ctx.position_list_query(
                        trd_env=trd_env
                    )
            
            if ret != ft.RET_OK:
                error_msg = str(data)
                logger.error(f"Failed to get positions: {error_msg}")
                
                # 处理常见错误
                if "Market not open" in error_msg:
                    logger.warning("市场未开盘，无法获取持仓数据")
                elif "API not ready" in error_msg or "Network failed" in error_msg:
                    logger.warning("API连接问题，请检查与OpenD的连接")
                elif "Nonexisting acc_id" in error_msg:
                    logger.warning(f"账户ID {acc_id} 不存在，请检查账户配置")
                
                return None
            
            # 添加数据验证
            if data is None:
                logger.warning("API返回的持仓数据为None")
                return pd.DataFrame()  # 返回空DataFrame而不是None，表示无持仓
            
            if not isinstance(data, pd.DataFrame):
                logger.warning(f"API返回的持仓数据类型不是DataFrame: {type(data)}")
                try:
                    # 尝试转换为DataFrame
                    if isinstance(data, (list, dict)):
                        data = pd.DataFrame(data)
                    else:
                        logger.error(f"无法将类型 {type(data)} 转换为DataFrame")
                        return pd.DataFrame()
                except Exception as conv_err:
                    logger.error(f"转换持仓数据至DataFrame失败: {str(conv_err)}")
                    return pd.DataFrame()
            
            # 检查数据是否为空
            if data.empty:
                logger.info("账户没有持仓")
                return data
            
            # 记录详细的持仓信息用于调试
            logger.debug(f"Got positions: {len(data)} positions")
            logger.debug(f"Position columns: {data.columns.tolist()}")
            
            # 检查关键字段是否存在
            required_cols = ['code', 'qty', 'cost_price', 'market_val']
            missing_cols = [col for col in required_cols if col not in data.columns]
            if missing_cols:
                logger.warning(f"持仓数据缺少预期的列: {missing_cols}. 可用列: {data.columns.tolist()}")
            
            # 输出简要的持仓摘要
            for i, pos in data.iterrows():
                code = pos.get('code', 'Unknown')
                qty = pos.get('qty', 'Unknown')
                logger.debug(f"Position {i+1}: {code} x {qty}")
                
            return data
        except Exception as e:
            import traceback
            logger.error(f"Error getting positions: {str(e)}")
            logger.debug(f"Position query exception traceback: {traceback.format_exc()}")
            return None
            
    def get_account_info(self):
        """
        Get account information including cash and assets
        
        Returns:
            dict with account data or None if error
        """
        if not self.conn.connected:
            logger.error("Not connected to OpenD")
            return None
            
        try:
            logger.debug("Getting account info")
            # Determine trading environment from config
            trd_env = ft.TrdEnv.REAL if config.TRADING_ENV == 'REAL' else ft.TrdEnv.SIMULATE
            
            # 获取账户列表，以便找到正确的acc_id
            try:
                ret, accounts = self.conn.trade_ctx.get_acc_list()
                if ret != ft.RET_OK:
                    logger.warning(f"Failed to get account list: {accounts}")
                else:
                    logger.debug(f"Got {len(accounts)} accounts")
            except Exception as e:
                logger.warning(f"Error getting account list: {str(e)}")
                accounts = None
                
            # 尝试找到匹配环境的账户ID
            acc_id = 0
            if accounts is not None and isinstance(accounts, pd.DataFrame) and not accounts.empty:
                # 尝试找到与当前交易环境匹配的账户
                matching_accounts = accounts[accounts['trd_env'] == trd_env] if 'trd_env' in accounts.columns else pd.DataFrame()
                if not matching_accounts.empty:
                    acc_id = matching_accounts['acc_id'].iloc[0]
                    logger.debug(f"Using matching account ID: {acc_id}")
                else:
                    # 使用第一个可用账户
                    acc_id = accounts['acc_id'].iloc[0]
                    logger.debug(f"Using first available account ID: {acc_id}")
            
            # 尝试不同的参数组合
            try:
                # 完整参数调用
                logger.debug(f"Querying account info with trd_env={trd_env}, acc_id={acc_id}")
                ret, data = self.conn.trade_ctx.accinfo_query(
                    trd_env=trd_env,
                    acc_id=acc_id
                )
            except Exception as e:
                # 最基本的调用
                logger.debug(f"Full parameter call not supported: {e}, using basic call")
                ret, data = self.conn.trade_ctx.accinfo_query(
                    trd_env=trd_env
                )
            
            if ret != ft.RET_OK:
                error_msg = str(data)
                logger.error(f"Failed to get account info: {error_msg}")
                
                # 处理常见错误
                if "Nonexisting acc_id" in error_msg:
                    logger.warning(f"账户ID {acc_id} 不存在，请检查账户配置")
                elif "API not ready" in error_msg or "Network failed" in error_msg:
                    logger.warning("API连接问题，请检查与OpenD的连接")
                    
                return None
            
            # Log the entire response for debugging
            logger.debug(f"Got account info: {data}")    
            
            # 数据验证和处理
            if data is None:
                logger.warning("API返回的账户信息为None")
                return pd.DataFrame()
                
            if not isinstance(data, pd.DataFrame):
                logger.warning(f"API返回的账户信息类型不是DataFrame: {type(data)}")
                try:
                    if isinstance(data, (list, dict)):
                        data = pd.DataFrame(data)
                    else:
                        logger.error(f"无法将类型 {type(data)} 转换为DataFrame")
                        return pd.DataFrame()
                except Exception as conv_err:
                    logger.error(f"转换账户信息至DataFrame失败: {str(conv_err)}")
                    return pd.DataFrame()
            
            if data.empty:
                logger.warning("账户信息为空")
                return data
            
            if data is not None and len(data) > 0:
                # Use get() with a default to avoid KeyError if the key doesn't exist
                power_val = data['power'].iloc[0] if 'power' in data.columns else 0
                cash_val = data['cash'].iloc[0] if 'cash' in data.columns else 0
                logger.info(f"Account info: power={power_val}, cash={cash_val}")
                
            return data
        except Exception as e:
            logger.error(f"Error getting account info: {str(e)}")
            return None
            
    def get_account_list(self):
        """
        Get list of available trading accounts
        
        Returns:
            pandas.DataFrame with account list or None if error
        """
        if not self.conn.connected:
            logger.error("Not connected to OpenD")
            return None
            
        try:
            logger.debug("Getting account list")
            ret, data = self.conn.trade_ctx.get_acc_list()
            if ret != ft.RET_OK:
                logger.error(f"Failed to get account list: {data}")
                return None
                
            logger.debug(f"Got account list: {data}")
            return data
        except Exception as e:
            logger.error(f"Error getting account list: {str(e)}")
            return None

    def _get_hk_account_id(self, trd_env):
        """
        获取HK账户的ID
        
        Args:
            trd_env: 交易环境
            
        Returns:
            HK账户ID或None
        """
        try:
            ret, acc_list = self.conn.trade_ctx.get_acc_list()
            if ret != ft.RET_OK:
                logger.error(f"Failed to get account list: {acc_list}")
                return None
                
            logger.debug(f"Account list: {acc_list}")
            
            if not isinstance(acc_list, pd.DataFrame) or acc_list.empty:
                logger.warning("Account list is empty or not a DataFrame")
                return None
                
            # 首先尝试使用交易环境和账户ID确定有效账户
            # 在测试结果中我们看到账户ID可能因为选错了而不存在
            # 所以我们先验证账户列表中存在哪些账户ID
            valid_acc_ids = set(acc_list['acc_id'].tolist())
            logger.debug(f"Valid account IDs: {valid_acc_ids}")
            
            # 检查是否有账户类型或市场信息列
            if 'trd_env' in acc_list.columns and 'trd_market_auth' in acc_list.columns:
                # 查找具有HK市场权限且环境匹配的账户
                for _, acc in acc_list.iterrows():
                    if acc['trd_env'] == trd_env:
                        trd_market_auth = acc['trd_market_auth']
                        
                        # 检查市场授权的数据类型和结构
                        if isinstance(trd_market_auth, (list, tuple)) and ft.TrdMarket.HK in trd_market_auth:
                            return acc['acc_id']
                        elif isinstance(trd_market_auth, int) and trd_market_auth & (1 << ft.TrdMarket.HK.value):
                            return acc['acc_id']
                        
            # 备选方案1：直接使用账户ID列表中的第一个账户
            # 在生产环境中这可能不是理想选择，但在测试环境中可以接受
            if len(valid_acc_ids) > 0:
                first_acc_id = acc_list['acc_id'].iloc[0]
                logger.info(f"使用第一个可用账户ID: {first_acc_id}")
                return first_acc_id
            
            # 如果上面的方法都失败了，返回None表示未找到合适的账户
            logger.warning("未找到任何有效的账户ID")
            return None
        except Exception as e:
            logger.error(f"Error finding HK account: {str(e)}")
            return None 