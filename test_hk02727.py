#!/usr/bin/env python3
"""
测试脚本：以HK.02727为例测试账户登录、行情获取和交易功能
"""
import logging
import argparse
import sys
import time
import pandas as pd
from dotenv import load_dotenv

import futu as ft
from connection import FutuConnection
from market_data import MarketData
from trading import Trading

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('futu_test.log')
    ]
)
logger = logging.getLogger("FutuTest")

# 测试股票代码
TEST_STOCK = "HK.02727"  # 腾讯音乐

def test_connection():
    """测试与OpenD的连接"""
    logger.info("=== 测试与OpenD的连接 ===")
    conn = FutuConnection()
    success = conn.connect()
    
    if success:
        logger.info("✓ 成功连接到OpenD")
        
        # 测试解锁交易
        if conn.unlock_trade():
            logger.info("✓ 成功解锁交易")
        else:
            logger.error("✗ 解锁交易失败")
            
        conn.close()
        return True
    else:
        logger.error("✗ 连接到OpenD失败")
        return False

def test_market_data(test_stock=TEST_STOCK):
    """测试行情数据获取"""
    logger.info(f"=== 测试行情数据获取 ({test_stock}) ===")
    conn = FutuConnection()
    
    if not conn.connect():
        logger.error("✗ 连接到OpenD失败")
        return False
    
    market_data = MarketData(conn)
    
    try:
        # 测试股票订阅
        if market_data.subscribe_stock(test_stock):
            logger.info(f"✓ 成功订阅股票 {test_stock}")
        else:
            logger.error(f"✗ 订阅股票 {test_stock} 失败")
            conn.close()
            return False
            
        # 获取股票报价
        quote = market_data.get_stock_quote(test_stock)
        if quote is not None and not quote.empty:
            logger.info(f"✓ 成功获取股票报价")
            logger.info(f"  最新价格: {quote['last_price'].iloc[0] if 'last_price' in quote.columns else '未知'}")
            logger.info(f"  开盘价: {quote['open_price'].iloc[0] if 'open_price' in quote.columns else '未知'}")
            logger.info(f"  最高价: {quote['high_price'].iloc[0] if 'high_price' in quote.columns else '未知'}")
            logger.info(f"  最低价: {quote['low_price'].iloc[0] if 'low_price' in quote.columns else '未知'}")
            logger.info(f"  成交量: {quote['volume'].iloc[0] if 'volume' in quote.columns else '未知'}")
        else:
            logger.error(f"✗ 获取股票报价失败")
        
        # 获取K线数据
        kline = market_data.get_kline(test_stock, ft.KLType.K_DAY, 5)
        if kline is not None and not kline.empty:
            logger.info(f"✓ 成功获取K线数据")
            # 打印最近5天的K线数据
            for i in range(min(5, len(kline))):
                day = kline.iloc[i]
                logger.info(f"  {day['time_key'] if 'time_key' in kline.columns else i}: "
                            f"开盘 {day['open'] if 'open' in kline.columns else '未知'}, "
                            f"收盘 {day['close'] if 'close' in kline.columns else '未知'}, "
                            f"最高 {day['high'] if 'high' in kline.columns else '未知'}, "
                            f"最低 {day['low'] if 'low' in kline.columns else '未知'}")
        else:
            logger.error(f"✗ 获取K线数据失败")
            
        # 获取盘口数据
        order_book = market_data.get_order_book(test_stock)
        if order_book is not None:
            logger.info(f"✓ 成功获取盘口数据")
            # 检查数据结构
            if isinstance(order_book, dict) and 'Bid' in order_book and 'Ask' in order_book:
                # 打印买一价和卖一价
                bids = order_book['Bid']
                asks = order_book['Ask']
                
                if bids and len(bids) > 0:
                    logger.info(f"  买一价: {bids[0]['price'] if isinstance(bids[0], dict) and 'price' in bids[0] else '未知'} x "
                                f"{bids[0]['volume'] if isinstance(bids[0], dict) and 'volume' in bids[0] else '未知'}")
                
                if asks and len(asks) > 0:
                    logger.info(f"  卖一价: {asks[0]['price'] if isinstance(asks[0], dict) and 'price' in asks[0] else '未知'} x "
                                f"{asks[0]['volume'] if isinstance(asks[0], dict) and 'volume' in asks[0] else '未知'}")
            else:
                logger.info(f"  盘口数据结构不符合预期: {type(order_book)}")
        else:
            logger.error(f"✗ 获取盘口数据失败")
            
        conn.close()
        return True
    except Exception as e:
        import traceback
        logger.error(f"测试行情数据时出错: {str(e)}")
        logger.debug(f"异常堆栈: {traceback.format_exc()}")
        conn.close()
        return False

def test_account_info():
    """测试账户信息获取"""
    logger.info("=== 测试账户信息获取 ===")
    conn = FutuConnection()
    
    if not conn.connect():
        logger.error("✗ 连接到OpenD失败")
        return False
    
    trading = Trading(conn)
    
    try:
        # 解锁交易
        trade_unlocked = conn.unlock_trade()
        if not trade_unlocked:
            logger.warning("⚠ 解锁交易失败，但仍将尝试获取账户信息")
            
        # 获取账户列表
        accounts = trading.get_account_list()
        if accounts is not None and not (isinstance(accounts, pd.DataFrame) and accounts.empty):
            logger.info(f"✓ 成功获取账户列表")
            if isinstance(accounts, pd.DataFrame):
                logger.info(f"  账户数量: {len(accounts)}")
                for i, acc in accounts.iterrows():
                    acc_id = acc['acc_id'] if 'acc_id' in accounts.columns else '未知'
                    trd_env = acc['trd_env_name'] if 'trd_env_name' in accounts.columns else '未知'
                    logger.info(f"  账户 {i+1}: ID={acc_id}, 环境={trd_env}")
            else:
                logger.info(f"  账户列表数据类型: {type(accounts)}")
        else:
            logger.error(f"✗ 获取账户列表失败或没有账户")
            
        # 获取账户资金信息 (无论是否解锁交易都尝试)
        account_info = trading.get_account_info()
        if account_info is not None:
            logger.info(f"✓ 成功获取账户资金信息")
            if isinstance(account_info, pd.DataFrame) and not account_info.empty:
                # 输出账户资金详细信息
                logger.info(f"  账户资金详情:")
                
                # 检查可用的列
                available_cols = account_info.columns.tolist()
                logger.debug(f"  账户资金数据列: {available_cols}")
                
                # 逐一获取并记录账户资金信息
                fields = [
                    ('cash', '现金'),
                    ('power', '购买力'),
                    ('total_assets', '总资产'),
                    ('market_val', '市值'),
                    ('avl_withdrawal_cash', '可取资金'),
                    ('max_power_short', '融券限额'),
                    ('net_cash_power', '净现金购买力')
                ]
                
                for field, label in fields:
                    if field in available_cols:
                        value = account_info[field].iloc[0]
                        logger.info(f"  {label}: {value}")
                    else:
                        logger.debug(f"  {label}字段不可用")
            else:
                logger.info(f"  账户资金信息数据类型: {type(account_info)}")
                if account_info is not None:
                    logger.debug(f"  原始账户资金数据: {account_info}")
        else:
            logger.error(f"✗ 获取账户资金信息失败")
            
        # 获取持仓信息 (无论是否解锁交易都尝试)
        positions = trading.get_positions()
        if positions is not None:
            logger.info(f"✓ 成功查询持仓")
            
            if isinstance(positions, pd.DataFrame):
                if positions.empty:
                    logger.info(f"  账户没有持仓")
                else:
                    logger.info(f"  持仓数量: {len(positions)}")
                    # 检查我们需要的关键列是否存在
                    expected_cols = ['code', 'qty', 'cost_price', 'market_val', 'position_side', 'can_sell_qty', 'pl_ratio']
                    available_cols = positions.columns.tolist()
                    
                    logger.debug(f"  持仓数据列: {available_cols}")
                    
                    # 输出每个持仓的详细信息
                    for i, pos in positions.iterrows():
                        position_info = []
                        # 代码
                        code = pos['code'] if 'code' in available_cols else '未知'
                        position_info.append(f"代码={code}")
                        
                        # 持仓方向
                        side = pos['position_side'] if 'position_side' in available_cols else '未知'
                        position_info.append(f"方向={side}")
                        
                        # 数量
                        qty = pos['qty'] if 'qty' in available_cols else '未知'
                        position_info.append(f"数量={qty}")
                        
                        # 可卖数量
                        can_sell = pos['can_sell_qty'] if 'can_sell_qty' in available_cols else '未知'
                        position_info.append(f"可卖数量={can_sell}")
                        
                        # 成本价
                        cost = pos['cost_price'] if 'cost_price' in available_cols else '未知'
                        position_info.append(f"成本价={cost}")
                        
                        # 市值
                        val = pos['market_val'] if 'market_val' in available_cols else '未知'
                        position_info.append(f"市值={val}")
                        
                        # 盈亏比例
                        pl_ratio = pos['pl_ratio'] if 'pl_ratio' in available_cols else '未知'
                        if pl_ratio != '未知':
                            pl_ratio_pct = f"{float(pl_ratio) * 100:.2f}%"
                            position_info.append(f"盈亏比例={pl_ratio_pct}")
                        else:
                            position_info.append("盈亏比例=未知")
                        
                        # 输出拼接的持仓信息
                        logger.info(f"  持仓 {i+1}: {', '.join(position_info)}")
            else:
                logger.warning(f"  持仓数据结构异常: {type(positions)}")
        else:
            logger.error(f"✗ 获取持仓信息失败")
            
        conn.close()
        return True
    except Exception as e:
        import traceback
        logger.error(f"测试账户信息时出错: {str(e)}")
        logger.debug(f"异常堆栈: {traceback.format_exc()}")
        conn.close()
        return False

def test_order_simulation(test_stock=TEST_STOCK):
    """测试模拟下单（不实际下单）"""
    logger.info(f"=== 测试模拟下单 ({test_stock}) ===")
    conn = FutuConnection()
    
    if not conn.connect():
        logger.error("✗ 连接到OpenD失败")
        return False
    
    market_data = MarketData(conn)
    trading = Trading(conn)
    
    try:
        # 解锁交易
        trade_unlocked = conn.unlock_trade()
        if not trade_unlocked:
            logger.warning("⚠ 解锁交易失败，将跳过需要交易权限的测试")
            
        # 先订阅股票，否则无法获取报价
        if not market_data.subscribe_stock(test_stock):
            logger.error(f"✗ 订阅股票 {test_stock} 失败，无法获取报价")
            conn.close()
            return False
        
        # 获取股票最新价格
        quote = market_data.get_stock_quote(test_stock)
        if quote is None or quote.empty or 'last_price' not in quote.columns:
            logger.error(f"✗ 获取股票价格失败，无法进行模拟下单")
            conn.close()
            return False
            
        last_price = float(quote['last_price'].iloc[0])
        logger.info(f"股票 {test_stock} 最新价格: {last_price}")
        
        # 模拟下单参数 - 不实际发送
        qty = 100  # 股数
        price = round(last_price * 0.9, 2)  # 模拟以低于市价的价格买入
        
        logger.info(f"模拟限价买入: {test_stock}, 价格={price}, 数量={qty}")
        logger.info("注意: 本测试不会实际发送订单!")
        
        # 检查账户资金是否足够（只有在成功解锁交易的情况下）
        if trade_unlocked:
            account_info = trading.get_account_info()
            if account_info is not None and isinstance(account_info, pd.DataFrame) and not account_info.empty:
                if 'power' in account_info.columns:
                    buying_power = float(account_info['power'].iloc[0])
                    order_value = price * qty
                    
                    if buying_power >= order_value:
                        logger.info(f"✓ 账户资金充足，可以下单 (需要: {order_value}, 可用: {buying_power})")
                    else:
                        logger.warning(f"⚠ 账户资金不足 (需要: {order_value}, 可用: {buying_power})")
                else:
                    logger.warning("⚠ 无法获取账户购买力信息")
            else:
                logger.warning("⚠ 无法获取账户资金信息")
        else:
            logger.info("已跳过账户资金检查 (交易未解锁)")
        
        # 模拟构建订单参数 (不实际执行)
        """
        如果要实际下单，可以使用如下代码：
        ret, data = trading.place_order(
            stock_code=test_stock,
            price=price,
            qty=qty,
            order_type=ft.OrderType.NORMAL,
            direction=ft.TrdSide.BUY
        )
        
        if ret == ft.RET_OK:
            logger.info(f"✓ 下单成功: {data}")
        else:
            logger.error(f"✗ 下单失败: {data}")
        """
        
        logger.info("✓ 模拟下单测试完成")
        conn.close()
        return True
    except Exception as e:
        import traceback
        logger.error(f"测试下单时出错: {str(e)}")
        logger.debug(f"异常堆栈: {traceback.format_exc()}")
        conn.close()
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='富途API测试脚本')
    parser.add_argument('--connection', action='store_true', help='测试与OpenD的连接')
    parser.add_argument('--market', action='store_true', help='测试行情数据获取')
    parser.add_argument('--account', action='store_true', help='测试账户信息获取')
    parser.add_argument('--order', action='store_true', help='测试模拟下单')
    parser.add_argument('--all', action='store_true', help='运行所有测试')
    parser.add_argument('--stock', type=str, default=TEST_STOCK, help=f'要测试的股票代码 (默认: {TEST_STOCK})')
    parser.add_argument('--strict', action='store_true', help='严格模式：任何测试失败都返回失败状态码')
    
    args = parser.parse_args()
    
    # 如果没有指定任何测试，默认运行所有测试
    if not (args.connection or args.market or args.account or args.order or args.all):
        args.all = True
        
    # 加载环境变量
    load_dotenv()
    
    # 运行测试
    test_results = []
    
    # 定义测试类型
    critical_tests = ["连接测试", "行情数据测试"]  # 关键测试，必须成功
    optional_tests = ["账户信息测试", "模拟下单测试"]  # 可选测试，允许失败
    
    if args.connection or args.all:
        test_results.append(("连接测试", test_connection()))
        
    if args.market or args.all:
        test_results.append(("行情数据测试", test_market_data(args.stock)))
        
    if args.account or args.all:
        test_results.append(("账户信息测试", test_account_info()))
        
    if args.order or args.all:
        test_results.append(("模拟下单测试", test_order_simulation(args.stock)))
        
    # 打印测试结果摘要
    logger.info("\n=== 测试结果摘要 ===")
    for name, result in test_results:
        status = "✓ 通过" if result else "✗ 失败"
        logger.info(f"{status} - {name}")
        
    # 计算成功率
    success_count = sum(1 for _, result in test_results if result)
    total_count = len(test_results)
    success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
    
    logger.info(f"总测试: {total_count}, 成功: {success_count}, 失败: {total_count - success_count}")
    logger.info(f"成功率: {success_rate:.1f}%")
    
    # 根据严格模式或测试类型决定返回码
    if args.strict:
        # 严格模式：任何测试失败都返回失败状态码
        return 0 if all(result for _, result in test_results) else 1
    else:
        # 宽松模式：只有关键测试失败才返回失败状态码
        critical_failed = any(not result for name, result in test_results if name in critical_tests)
        if critical_failed:
            logger.error("关键测试失败，返回错误状态码")
            return 1
        else:
            # 即使可选测试失败，也返回成功
            optional_failed = any(not result for name, result in test_results if name in optional_tests)
            if optional_failed:
                logger.warning("部分可选测试失败，但关键测试通过，返回成功状态码")
            return 0

if __name__ == "__main__":
    sys.exit(main()) 