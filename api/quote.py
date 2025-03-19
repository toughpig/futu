#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Examples of FUTU OpenAPI quote functionality.
This includes subscription, market data, historical data, and other quote API functions.
"""

import time
import logging
from futu import *

# Set up logging
logger = logging.getLogger('futu.api.quote')
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def print_divider(title):
    """Print a divider with title for better output formatting"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

class StockQuoteHandler(StockQuoteHandlerBase):
    """
    报价推送回调处理类
    """
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(StockQuoteHandler, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            logger.debug(f"StockQuoteHandler: error, msg: {data}")
            return RET_ERROR, data
        
        logger.debug(f"StockQuoteHandler: receive {len(data)} stocks' quote data")
        for stock_data in data:
            logger.debug(f"StockQuoteHandler: {stock_data}")
        
        return RET_OK, data

class OrderBookHandler(OrderBookHandlerBase):
    """
    摆盘推送回调处理类
    """
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(OrderBookHandler, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            logger.debug(f"OrderBookHandler: error, msg: {data}")
            return RET_ERROR, data
        
        logger.debug(f"OrderBookHandler: {data}")
        return RET_OK, data

class CurKlineHandler(CurKlineHandlerBase):
    """
    K线推送回调处理类
    """
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(CurKlineHandler, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            logger.debug(f"CurKlineHandler: error, msg: {data}")
            return RET_ERROR, data
        
        logger.debug(f"CurKlineHandler: receive K线 data: {len(data)} items")
        return RET_OK, data

class TickerHandler(TickerHandlerBase):
    """
    逐笔推送回调处理类
    """
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(TickerHandler, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            logger.debug(f"TickerHandler: error, msg: {data}")
            return RET_ERROR, data
        
        logger.debug(f"TickerHandler: receive ticker data: {len(data)} items")
        return RET_OK, data

class RTDataHandler(RTDataHandlerBase):
    """
    分时推送回调处理类
    """
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(RTDataHandler, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            logger.debug(f"RTDataHandler: error, msg: {data}")
            return RET_ERROR, data
        
        logger.debug(f"RTDataHandler: receive {len(data)} stocks' RT data")
        return RET_OK, data

class BrokerHandler(BrokerHandlerBase):
    """
    经纪队列推送回调处理类
    """
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(BrokerHandler, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            logger.debug(f"BrokerHandler: error, msg: {data}")
            return RET_ERROR, data
        
        logger.debug(f"BrokerHandler: {data}")
        return RET_OK, data

def example_subscribe():
    """
    订阅数据示例
    """
    print_divider("订阅数据")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 设置回调处理对象
    handler = OrderBookHandler()
    quote_ctx.set_handler(handler)
    
    # 订阅订单簿
    ret_sub, err_message = quote_ctx.subscribe(['HK.00700'], [SubType.ORDER_BOOK])
    if ret_sub == RET_OK:
        print(f"订阅成功: 港股00700订单簿数据")
        
        # 等待3秒接收推送数据
        print("等待接收数据推送...")
        time.sleep(3)
    else:
        print(f"订阅失败: {err_message}")
    
    print("\n查询订阅状态")
    ret, data = quote_ctx.query_subscription()
    if ret == RET_OK:
        print(f"当前订阅状态: {data}")
    
    quote_ctx.close()

def example_unsubscribe():
    """
    取消订阅示例
    """
    print_divider("取消订阅")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 订阅
    ret_sub, err_message = quote_ctx.subscribe(['HK.00700'], [SubType.QUOTE, SubType.TICKER], subscribe_push=False)
    if ret_sub == RET_OK:
        print("订阅成功!")
        ret, data = quote_ctx.query_subscription()
        print(f"当前订阅状态: {data}")
        
        # 需要等待至少60秒才能取消订阅
        print("正常情况需要等待60秒后才能取消订阅,此处为示例所以不等待")
        
        # 取消部分订阅
        ret_unsub, err_message_unsub = quote_ctx.unsubscribe(['HK.00700'], [SubType.QUOTE])
        if ret_unsub == RET_OK:
            ret, data = quote_ctx.query_subscription()
            print(f"取消部分订阅成功,当前订阅状态: {data}")
        else:
            print(f"取消订阅失败: {err_message_unsub}")
    else:
        print(f"订阅失败: {err_message}")
    
    quote_ctx.close()

def example_unsubscribe_all():
    """
    取消所有订阅示例
    """
    print_divider("取消所有订阅")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 订阅
    ret_sub, err_message = quote_ctx.subscribe(['HK.00700'], [SubType.QUOTE, SubType.TICKER], subscribe_push=False)
    if ret_sub == RET_OK:
        print("订阅成功!")
        ret, data = quote_ctx.query_subscription()
        print(f"当前订阅状态: {data}")
        
        # 需要等待至少60秒才能取消订阅
        print("正常情况需要等待60秒后才能取消订阅,此处为示例所以不等待")
        
        # 取消所有订阅
        ret_unsub, err_message_unsub = quote_ctx.unsubscribe_all()
        if ret_unsub == RET_OK:
            ret, data = quote_ctx.query_subscription()
            print(f"取消所有订阅成功,当前订阅状态: {data}")
        else:
            print(f"取消所有订阅失败: {err_message_unsub}")
    else:
        print(f"订阅失败: {err_message}")
    
    quote_ctx.close()

def example_get_market_snapshot():
    """
    获取市场快照示例
    """
    print_divider("获取市场快照")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    ret, data = quote_ctx.get_market_snapshot(['SH.600000', 'HK.00700'])
    if ret == RET_OK:
        print(data)
        print(f"第一条股票代码: {data['code'][0]}")
        print(f"所有股票代码: {data['code'].values.tolist()}")
    else:
        print(f"获取市场快照失败: {data}")
    
    quote_ctx.close()

def example_get_stock_quote():
    """
    获取实时报价示例
    """
    print_divider("获取实时报价")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 先订阅
    ret_sub, err_message = quote_ctx.subscribe(['HK.00700'], [SubType.QUOTE], subscribe_push=False)
    if ret_sub == RET_OK:
        # 然后获取报价
        ret, data = quote_ctx.get_stock_quote(['HK.00700'])
        if ret == RET_OK:
            print(data)
            print(f"第一条股票代码: {data['code'][0]}")
            print(f"所有股票代码: {data['code'].values.tolist()}")
        else:
            print(f"获取实时报价失败: {data}")
    else:
        print(f"订阅失败: {err_message}")
    
    quote_ctx.close()

def example_get_order_book():
    """
    获取实时摆盘示例
    """
    print_divider("获取实时摆盘")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 先订阅
    ret_sub = quote_ctx.subscribe(['HK.00700'], [SubType.ORDER_BOOK], subscribe_push=False)[0]
    if ret_sub == RET_OK:
        # 然后获取实时摆盘数据
        ret, data = quote_ctx.get_order_book('HK.00700', num=3)  # 获取一次3档实时摆盘数据
        if ret == RET_OK:
            print(data)
            print(f"Bid买方档口: {data['Bid']}")
            print(f"Ask卖方档口: {data['Ask']}")
        else:
            print(f"获取实时摆盘失败: {data}")
    else:
        print("订阅失败")
    
    quote_ctx.close()

def example_get_cur_kline():
    """
    获取实时K线示例
    """
    print_divider("获取实时K线")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 先订阅
    ret_sub, err_message = quote_ctx.subscribe(['HK.00700'], [SubType.K_DAY], subscribe_push=False)
    if ret_sub == RET_OK:
        # 然后获取K线数据
        ret, data = quote_ctx.get_cur_kline('HK.00700', 5, KLType.K_DAY, AuType.QFQ)  # 获取港股00700最近5个K线数据
        if ret == RET_OK:
            print(data)
            print(f"第一条K线收盘价: {data['close'][0]}")
            print(f"所有K线收盘价: {data['close'].values.tolist()}")
        else:
            print(f"获取实时K线失败: {data}")
    else:
        print(f"订阅失败: {err_message}")
    
    quote_ctx.close()

def example_get_rt_ticker():
    """
    获取实时逐笔示例
    """
    print_divider("获取实时逐笔")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 先订阅
    ret_sub, err_message = quote_ctx.subscribe(['HK.00700'], [SubType.TICKER], subscribe_push=False)
    if ret_sub == RET_OK:
        # 然后获取逐笔数据
        ret, data = quote_ctx.get_rt_ticker('HK.00700', 5)  # 获取港股00700最近5个逐笔
        if ret == RET_OK:
            print(data)
            print(f"第一条逐笔成交金额: {data['turnover'][0]}")
            print(f"所有逐笔成交金额: {data['turnover'].values.tolist()}")
        else:
            print(f"获取实时逐笔失败: {data}")
    else:
        print(f"订阅失败: {err_message}")
    
    quote_ctx.close()

def example_get_rt_data():
    """
    获取分时数据示例
    """
    print_divider("获取分时数据")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 先订阅
    ret_sub, err_message = quote_ctx.subscribe(['HK.00700'], [SubType.RT_DATA], subscribe_push=False)
    if ret_sub == RET_OK:
        # 然后获取分时数据
        ret, data = quote_ctx.get_rt_data('HK.00700')  # 获取港股00700分时数据
        if ret == RET_OK:
            print(data)
            print(f"记录条数: {len(data)}")
        else:
            print(f"获取分时数据失败: {data}")
    else:
        print(f"订阅失败: {err_message}")
    
    quote_ctx.close()

def example_get_broker_queue():
    """
    获取经纪队列示例
    """
    print_divider("获取经纪队列")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 先订阅
    ret_sub, err_message = quote_ctx.subscribe(['HK.00700'], [SubType.BROKER], subscribe_push=False)
    if ret_sub == RET_OK:
        # 然后获取经纪队列数据
        ret, bid_frame_table, ask_frame_table = quote_ctx.get_broker_queue('HK.00700')
        if ret == RET_OK:
            print("买盘经纪队列:")
            print(bid_frame_table)
            print("\n卖盘经纪队列:")
            print(ask_frame_table)
        else:
            print(f"获取经纪队列失败: {bid_frame_table}")
    else:
        print(f"订阅失败: {err_message}")
    
    quote_ctx.close()

def example_request_history_kline():
    """
    请求历史K线示例
    """
    print_divider("请求历史K线")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    import datetime
    today = datetime.datetime.now()
    start_date = (today - datetime.timedelta(days=10)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    
    ret, data, page_req_key = quote_ctx.request_history_kline('HK.00700', start=start_date, end=end_date, max_count=5)  # 每页5条记录
    if ret == RET_OK:
        print(data)
        print(f"第一条的股票代码: {data['code'][0]}")
        print(f"收盘价列表: {data['close'].values.tolist()}")
        
        # 请求后续页
        while page_req_key is not None:
            print("\n继续获取下一页数据")
            ret, data, page_req_key = quote_ctx.request_history_kline('HK.00700', 
                                                               start=start_date, 
                                                               end=end_date, 
                                                               max_count=5, 
                                                               page_req_key=page_req_key)
            if ret == RET_OK:
                print(data)
            else:
                print(f"获取历史K线分页数据失败: {data}")
                break
    else:
        print(f"获取历史K线失败: {data}")
    
    quote_ctx.close()

def example_get_market_state():
    """
    获取市场状态示例
    """
    print_divider("获取市场状态")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    ret, data = quote_ctx.get_market_state(['HK.00700', 'SH.600000', 'US.AAPL'])
    if ret == RET_OK:
        print(data)
    else:
        print(f"获取市场状态失败: {data}")
    
    quote_ctx.close()

def example_get_capital_flow():
    """
    获取资金流向示例
    """
    print_divider("获取资金流向")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    ret, data = quote_ctx.get_capital_flow('HK.00700')
    if ret == RET_OK:
        print(data)
    else:
        print(f"获取资金流向失败: {data}")
    
    quote_ctx.close()

def example_get_capital_distribution():
    """
    获取资金分布示例
    """
    print_divider("获取资金分布")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    ret, data = quote_ctx.get_capital_distribution('HK.00700')
    if ret == RET_OK:
        print(data)
    else:
        print(f"获取资金分布失败: {data}")
    
    quote_ctx.close()

def example_get_owner_plate():
    """
    获取股票所属板块示例
    """
    print_divider("获取股票所属板块")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    ret, data = quote_ctx.get_owner_plate(['HK.00700', 'SH.600000'])
    if ret == RET_OK:
        print(data)
    else:
        print(f"获取股票所属板块失败: {data}")
    
    quote_ctx.close()

def example_get_rehab():
    """
    获取复权因子示例
    """
    print_divider("获取复权因子")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    ret, data = quote_ctx.get_rehab('HK.00700')
    if ret == RET_OK:
        print(data)
    else:
        print(f"获取复权因子失败: {data}")
    
    quote_ctx.close()

def example_get_plate_stock():
    """
    获取板块内股票示例
    """
    print_divider("获取板块内股票")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    ret, data = quote_ctx.get_plate_stock('HK.BK1001') # 恒生指数成份股
    if ret == RET_OK:
        print(data)
        print(f"板块股票数量: {len(data)}")
    else:
        print(f"获取板块内股票失败: {data}")
    
    quote_ctx.close()

def example_get_plate_list():
    """
    获取板块集合示例
    """
    print_divider("获取板块集合")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    ret, data = quote_ctx.get_plate_list(Market.HK, Plate.ALL)
    if ret == RET_OK:
        print(data)
        print(f"板块数量: {len(data)}")
    else:
        print(f"获取板块集合失败: {data}")
    
    quote_ctx.close()

def example_get_stock_basicinfo():
    """
    获取股票基本信息示例
    """
    print_divider("获取股票基本信息")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 方式1：获取指定市场的指定类型股票
    ret, data = quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.STOCK)
    if ret == RET_OK:
        print(f"香港市场股票数量: {len(data)}")
        print(data.head())  # 仅显示前几条记录
    else:
        print(f"获取股票基本信息失败: {data}")
    
    print("\n获取指定股票基本信息:")
    # 方式2：获取指定股票代码的基本信息
    ret, data = quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.STOCK, ['HK.00700', 'HK.00388'])
    if ret == RET_OK:
        print(data)
        print(f"首只股票名称: {data['name'][0]}")
        print(f"所有股票名称: {data['name'].values.tolist()}")
    else:
        print(f"获取股票基本信息失败: {data}")
    
    quote_ctx.close()

def example_get_ipo_list():
    """
    获取IPO列表示例
    """
    print_divider("获取IPO列表")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    ret, data = quote_ctx.get_ipo_list(Market.HK)
    if ret == RET_OK:
        print(data)
        print(f"即将IPO数量: {len(data)}")
    else:
        print(f"获取IPO列表失败: {data}")
    
    quote_ctx.close()

def example_get_global_state():
    """
    获取全局状态示例
    """
    print_divider("获取全局状态")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    ret, data = quote_ctx.get_global_state()
    if ret == RET_OK:
        print(data)
        print(f"交易日: {data['trade_date']}")
        print(f"服务器时间: {data['server_ver']}")
    else:
        print(f"获取全局状态失败: {data}")
    
    quote_ctx.close()

def example_request_trading_days():
    """
    获取交易日历示例
    """
    print_divider("获取交易日历")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 获取最近30天交易日
    import datetime
    today = datetime.datetime.now()
    start_date = (today - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    
    ret, data = quote_ctx.request_trading_days(Market.HK, start=start_date, end=end_date)
    if ret == RET_OK:
        print(data)
        print(f"交易日天数: {len(data['trading_day'].values)}")
    else:
        print(f"获取交易日历失败: {data}")
    
    quote_ctx.close()

def example_get_history_kl_quota():
    """
    获取历史K线额度示例
    """
    print_divider("获取历史K线额度")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    ret, data = quote_ctx.get_history_kl_quota(get_detail=True)
    if ret == RET_OK:
        print(data)
    else:
        print(f"获取历史K线额度失败: {data}")
    
    quote_ctx.close()

def example_get_price_reminder():
    """
    获取到价提醒示例
    """
    print_divider("获取到价提醒")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 先设置到价提醒
    price_reminder_op = PriceReminderOp.ADD
    code = 'HK.00700' 
    reminder_type = PriceReminderType.PRICE_UP
    reminder_freq = PriceReminderFreq.ALWAYS
    value = 400.0
    note = "价格上涨到400提示"
    
    ret, data = quote_ctx.set_price_reminder(price_reminder_op, code, 
                                           reminder_type, reminder_freq, 
                                           value, note)
    if ret == RET_OK:
        print(f"设置到价提醒成功: {data}")
        
        # 获取到价提醒
        ret, data = quote_ctx.get_price_reminder(code=code)
        if ret == RET_OK:
            print(f"获取到价提醒成功:")
            print(data)
        else:
            print(f"获取到价提醒失败: {data}")
    else:
        print(f"设置到价提醒失败: {data}")
    
    # 清理：删除设置的提醒
    ret, data = quote_ctx.set_price_reminder(PriceReminderOp.DEL, code, 
                                        reminder_type, reminder_freq, 
                                        value, note)
    if ret == RET_OK:
        print(f"删除到价提醒成功")
    
    quote_ctx.close()

def example_get_user_security_group():
    """
    获取自选股分组示例
    """
    print_divider("获取自选股分组")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    ret, data = quote_ctx.get_user_security_group()
    if ret == RET_OK:
        print(data)
        print(f"自选股分组数量: {len(data)}")
    else:
        print(f"获取自选股分组失败: {data}")
    
    quote_ctx.close()

def example_get_user_security():
    """
    获取自选股列表示例
    """
    print_divider("获取自选股列表")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 先获取分组
    ret, data = quote_ctx.get_user_security_group()
    if ret == RET_OK and len(data) > 0:
        group_id = data['group_id'][0]  # 使用第一个分组
        
        # 获取指定分组的自选股
        ret, data = quote_ctx.get_user_security(group_id)
        if ret == RET_OK:
            print(data)
            print(f"自选股数量: {len(data)}")
        else:
            print(f"获取自选股列表失败: {data}")
    else:
        print("无法获取自选股分组或没有分组")
    
    quote_ctx.close()

def example_set_price_reminder():
    """
    设置到价提醒示例
    """
    print_divider("设置到价提醒")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 设置到价提醒
    ret, data = quote_ctx.set_price_reminder(
        op=PriceReminderOp.ADD,
        code='HK.00700',
        reminder_type=PriceReminderType.PRICE_UP,
        reminder_freq=PriceReminderFreq.ALWAYS,
        value=400.0,
        note="价格上涨到400提示"
    )
    
    if ret == RET_OK:
        print(f"设置到价提醒成功: {data}")
        
        # 查询现有提醒
        ret, data = quote_ctx.get_price_reminder(code='HK.00700')
        if ret == RET_OK:
            print(f"查询到价提醒成功:")
            print(data)
            
            # 删除提醒
            if len(data) > 0:
                for _, row in data.iterrows():
                    ret, result = quote_ctx.set_price_reminder(
                        op=PriceReminderOp.DEL,
                        code=row['code'],
                        reminder_type=row['reminder_type'],
                        reminder_freq=row['reminder_freq'],
                        value=row['value'],
                        note=row['note'] if 'note' in row else ""
                    )
                    if ret == RET_OK:
                        print(f"删除到价提醒成功: {row['code']}")
                    else:
                        print(f"删除到价提醒失败: {result}")
    else:
        print(f"设置到价提醒失败: {data}")
    
    quote_ctx.close()

def run_all_examples():
    """
    运行所有行情API示例
    """
    try:
        example_subscribe()
    except Exception as e:
        print(f"订阅数据示例失败: {e}")
    
    try:
        example_unsubscribe()
    except Exception as e:
        print(f"取消订阅示例失败: {e}")
    
    try:
        example_unsubscribe_all()
    except Exception as e:
        print(f"取消所有订阅示例失败: {e}")
    
    try:
        example_get_market_snapshot()
    except Exception as e:
        print(f"获取市场快照示例失败: {e}")
    
    try:
        example_get_stock_quote()
    except Exception as e:
        print(f"获取实时报价示例失败: {e}")
    
    try:
        example_get_order_book()
    except Exception as e:
        print(f"获取实时摆盘示例失败: {e}")
    
    try:
        example_get_cur_kline()
    except Exception as e:
        print(f"获取实时K线示例失败: {e}")
    
    try:
        example_get_rt_ticker()
    except Exception as e:
        print(f"获取实时逐笔示例失败: {e}")
    
    try:
        example_get_rt_data()
    except Exception as e:
        print(f"获取分时数据示例失败: {e}")
    
    try:
        example_get_broker_queue()
    except Exception as e:
        print(f"获取经纪队列示例失败: {e}")
    
    try:
        example_request_history_kline()
    except Exception as e:
        print(f"请求历史K线示例失败: {e}")
    
    try:
        example_get_market_state()
    except Exception as e:
        print(f"获取市场状态示例失败: {e}")
    
    try:
        example_get_capital_flow()
    except Exception as e:
        print(f"获取资金流向示例失败: {e}")
    
    try:
        example_get_capital_distribution()
    except Exception as e:
        print(f"获取资金分布示例失败: {e}")
    
    try:
        example_get_owner_plate()
    except Exception as e:
        print(f"获取股票所属板块示例失败: {e}")
    
    try:
        example_get_rehab()
    except Exception as e:
        print(f"获取复权因子示例失败: {e}")
    
    try:
        example_get_plate_stock()
    except Exception as e:
        print(f"获取板块内股票示例失败: {e}")
    
    try:
        example_get_plate_list()
    except Exception as e:
        print(f"获取板块集合示例失败: {e}")
    
    try:
        example_get_stock_basicinfo()
    except Exception as e:
        print(f"获取股票基本信息示例失败: {e}")
    
    try:
        example_get_ipo_list()
    except Exception as e:
        print(f"获取IPO列表示例失败: {e}")
    
    try:
        example_get_global_state()
    except Exception as e:
        print(f"获取全局状态示例失败: {e}")
    
    try:
        example_request_trading_days()
    except Exception as e:
        print(f"获取交易日历示例失败: {e}")
    
    try:
        example_get_history_kl_quota()
    except Exception as e:
        print(f"获取历史K线额度示例失败: {e}")
    
    try:
        example_get_price_reminder()
    except Exception as e:
        print(f"获取到价提醒示例失败: {e}")
    
    try:
        example_get_user_security_group()
    except Exception as e:
        print(f"获取自选股分组示例失败: {e}")
    
    try:
        example_get_user_security()
    except Exception as e:
        print(f"获取自选股列表示例失败: {e}")
    
    try:
        example_set_price_reminder()
    except Exception as e:
        print(f"设置到价提醒示例失败: {e}")

if __name__ == "__main__":
    print("富途OpenAPI行情接口示例程序\n")
    print("注意: 运行前请确保OpenD已正确启动且连接到富途服务器\n")
    
    # 运行所有示例
    run_all_examples() 