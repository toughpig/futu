#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Examples of FUTU OpenAPI trade functions
"""

from futu import *
import time

pwd_unlock = '123456'  # 交易密码，实盘时请替换为实际密码

def print_divider(title):
    """Print a divider with title for better output formatting"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def example_get_acc_list():
    """
    获取交易业务账户列表示例
    """
    print_divider("获取交易业务账户列表")
    
    trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, 
                                 security_firm=SecurityFirm.FUTUSECURITIES)
    
    ret, data = trd_ctx.get_acc_list()
    if ret == RET_OK:
        print(data)
        if data.shape[0] > 0:
            print(f"第一个账号: {data['acc_id'][0]}")  # 取第一个账号
            print(f"所有账号: {data['acc_id'].values.tolist()}")  # 转为 list
    else:
        print('get_acc_list error: ', data)
    
    trd_ctx.close()  # 关闭当条连接

def example_unlock_trade():
    """
    解锁交易示例
    """
    print_divider("解锁交易")
    
    
    trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, 
                                 security_firm=SecurityFirm.FUTUSECURITIES)
    
    ret, data = trd_ctx.unlock_trade(pwd_unlock)
    if ret == RET_OK:
        print('unlock success!')
    else:
        print('unlock_trade failed: ', data)
    
    trd_ctx.close()  # 关闭当条连接

def example_accinfo_query():
    """
    查询账户资金信息示例
    """
    print_divider("查询账户资金信息")
    
    trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, 
                                 security_firm=SecurityFirm.FUTUSECURITIES)
    
    ret, data = trd_ctx.accinfo_query()
    if ret == RET_OK:
        print(data)
        print(f"购买力: {data['power'][0]}")  # 取第一行的购买力
        print(f"购买力列表: {data['power'].values.tolist()}")  # 转为 list
    else:
        print('accinfo_query error: ', data)
    
    trd_ctx.close()  # 关闭当条连接

def example_acctradinginfo_query():
    """
    查询最大可买可卖量示例
    """
    print_divider("查询最大可买可卖量")
    
    trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, 
                                 security_firm=SecurityFirm.FUTUSECURITIES)
    
    ret, data = trd_ctx.acctradinginfo_query(order_type=OrderType.NORMAL, code='HK.00700', price=400)
    if ret == RET_OK:
        print(data)
        print(f"最大融资可买数量: {data['max_cash_and_margin_buy'][0]}")
    else:
        print('acctradinginfo_query error: ', data)
    
    trd_ctx.close()  # 关闭当条连接

def example_position_list_query():
    """
    查询持仓列表示例
    """
    print_divider("查询持仓列表")
    
    trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, 
                                 security_firm=SecurityFirm.FUTUSECURITIES)
    
    ret, data = trd_ctx.position_list_query()
    if ret == RET_OK:
        print(data)
        if data.shape[0] > 0:  # 如果持仓列表不为空
            print(f"第一个股票名称: {data['stock_name'][0]}")
            print(f"所有股票名称: {data['stock_name'].values.tolist()}")
    else:
        print('position_list_query error: ', data)
    
    trd_ctx.close()  # 关闭当条连接

def example_get_margin_ratio():
    """
    查询股票融资融券数据示例
    """
    print_divider("查询股票融资融券数据")
    
    trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, 
                                 security_firm=SecurityFirm.FUTUSECURITIES)
    
    ret, data = trd_ctx.get_margin_ratio(code_list=['HK.00700','HK.09988'])
    if ret == RET_OK:
        print(data)
        print(f"是否允许融资: {data['is_long_permit'][0]}")  # 取第一条的是否允许融资
        print(f"融券初始保证金率: {data['im_short_ratio'].values.tolist()}")  # 转为 list
    else:
        print('error:', data)
    
    trd_ctx.close()  # 结束后记得关闭当条连接，防止连接条数用尽

def example_get_acc_cash_flow():
    """
    查询账户现金流水示例
    """
    print_divider("查询账户现金流水")
    
    trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, 
                                 security_firm=SecurityFirm.FUTUSECURITIES)
    
    # 查询前一天的现金流水
    import datetime
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    
    ret, data = trd_ctx.get_acc_cash_flow(clearing_date=yesterday)
    if ret == RET_OK:
        print(data)
        if data.shape[0] > 0:  # 如果现金流水列表不为空
            print(f"第一条流水类型: {data['cashflow_type'][0]}")
            print(f"所有流水金额: {data['cashflow_amount'].values.tolist()}")
    else:
        print('get_acc_cash_flow error: ', data)
    
    trd_ctx.close()

def example_place_order():
    """
    下单示例
    """
    print_divider("下单")
    
    
    trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, 
                                 security_firm=SecurityFirm.FUTUSECURITIES)
    
    ret, data = trd_ctx.unlock_trade(pwd_unlock)  # 若使用真实账户下单，需先对账户进行解锁
    if ret == RET_OK:
        # 模拟交易下单，参数：价格，数量，代码，方向，环境
        ret, data = trd_ctx.place_order(price=510.0, qty=100, code="HK.00700", 
                                       trd_side=TrdSide.BUY, trd_env=TrdEnv.SIMULATE)
        if ret == RET_OK:
            print(data)
            print(f"订单号: {data['order_id'][0]}")  # 获取下单的订单号
            print(f"所有订单号: {data['order_id'].values.tolist()}")  # 转为 list
        else:
            print('place_order error: ', data)
    else:
        print('unlock_trade failed: ', data)
    
    trd_ctx.close()

def example_modify_order():
    """
    改单/撤单示例
    """
    print_divider("改单/撤单")
    
    
    trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, 
                                 security_firm=SecurityFirm.FUTUSECURITIES)
    
    ret, data = trd_ctx.unlock_trade(pwd_unlock)  # 若使用真实账户改单/撤单，需先对账户进行解锁
    if ret == RET_OK:
        # 先下单
        ret, place_data = trd_ctx.place_order(price=510.0, qty=100, code="HK.00700", 
                                            trd_side=TrdSide.BUY, trd_env=TrdEnv.SIMULATE)
        if ret == RET_OK:
            order_id = place_data['order_id'][0]
            print(f"下单成功，订单号: {order_id}")
            
            # 等待一秒后撤单
            time.sleep(1)
            
            # 撤单操作
            ret, data = trd_ctx.modify_order(ModifyOrderOp.CANCEL, order_id, 0, 0, trd_env=TrdEnv.SIMULATE)
            if ret == RET_OK:
                print(data)
                print(f"撤单订单号: {data['order_id'][0]}")
                print(f"撤单订单号列表: {data['order_id'].values.tolist()}")
            else:
                print('modify_order error: ', data)
        else:
            print('place_order error: ', place_data)
    else:
        print('unlock_trade failed: ', data)
    
    trd_ctx.close()

def example_cancel_all_order():
    """
    全部撤单示例
    """
    print_divider("全部撤单")
    
    
    trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, 
                                 security_firm=SecurityFirm.FUTUSECURITIES)
    
    ret, data = trd_ctx.unlock_trade(pwd_unlock)  # 若使用真实账户改单/撤单，需先对账户进行解锁
    if ret == RET_OK:
        # 执行全部撤单
        ret, data = trd_ctx.cancel_all_order(trd_env=TrdEnv.REAL)
        if ret == RET_OK:
            print(data)
        else:
            print('cancel_all_order error: ', data)
    else:
        print('unlock_trade failed: ', data)
    
    trd_ctx.close()

def example_order_list_query():
    """
    查询未完成订单示例
    """
    print_divider("查询未完成订单")
    
    trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, 
                                 security_firm=SecurityFirm.FUTUSECURITIES)
    
    ret, data = trd_ctx.order_list_query(trd_env=TrdEnv.SIMULATE)
    if ret == RET_OK:
        print(data)
        if data.shape[0] > 0:  # 如果订单列表不为空
            print(f"第一个订单号: {data['order_id'][0]}")
            print(f"所有订单号: {data['order_id'].values.tolist()}")
    else:
        print('order_list_query error: ', data)
    
    trd_ctx.close()

def example_order_fee_query():
    """
    查询订单费用示例
    """
    print_divider("查询订单费用")
    
    trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US, host='127.0.0.1', port=11111, 
                                 security_firm=SecurityFirm.FUTUSECURITIES)
    
    # 先查询已成交订单
    ret1, data1 = trd_ctx.history_order_list_query(status_filter_list=[OrderStatus.FILLED_ALL], 
                                                 trd_env=TrdEnv.SIMULATE)
    if ret1 == RET_OK:
        if data1.shape[0] > 0:  # 如果订单列表不为空
            # 查询订单费用
            ret2, data2 = trd_ctx.order_fee_query(data1['order_id'].values.tolist(), trd_env=TrdEnv.SIMULATE)
            if ret2 == RET_OK:
                print(data2)
                if data2.shape[0] > 0:
                    print(f"第一笔订单的收费明细: {data2['fee_details'][0]}")
            else:
                print('order_fee_query error: ', data2)
        else:
            print("没有已成交订单")
    else:
        print('history_order_list_query error: ', data1)
    
    trd_ctx.close()

def example_history_order_list_query():
    """
    查询历史订单示例
    """
    print_divider("查询历史订单")
    
    trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, 
                                 security_firm=SecurityFirm.FUTUSECURITIES)
    
    # 查询最近30天的历史订单
    import datetime
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    
    ret, data = trd_ctx.history_order_list_query(start=start_date, end=end_date, trd_env=TrdEnv.SIMULATE)
    if ret == RET_OK:
        print(data)
        if data.shape[0] > 0:  # 如果订单列表不为空
            print(f"第一个历史订单号: {data['order_id'][0]}")
            print(f"所有历史订单号: {data['order_id'].values.tolist()}")
    else:
        print('history_order_list_query error: ', data)
    
    trd_ctx.close()

def example_deal_list_query():
    """
    查询当日成交示例
    """
    print_divider("查询当日成交")
    
    trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, 
                                 security_firm=SecurityFirm.FUTUSECURITIES)
    
    ret, data = trd_ctx.deal_list_query(trd_env=TrdEnv.REAL)
    if ret == RET_OK:
        print(data)
        if data.shape[0] > 0:  # 如果成交列表不为空
            print(f"第一个成交订单号: {data['order_id'][0]}")
            print(f"所有成交订单号: {data['order_id'].values.tolist()}")
    else:
        print('deal_list_query error: ', data)
    
    trd_ctx.close()

def example_history_deal_list_query():
    """
    查询历史成交示例
    """
    print_divider("查询历史成交")
    
    trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, 
                                 security_firm=SecurityFirm.FUTUSECURITIES)
    
    # 查询最近30天的历史成交
    import datetime
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    
    ret, data = trd_ctx.history_deal_list_query(start=start_date, end=end_date, trd_env=TrdEnv.REAL)
    if ret == RET_OK:
        print(data)
        if data.shape[0] > 0:  # 如果成交列表不为空
            print(f"第一个历史成交号: {data['deal_id'][0]}")
            print(f"所有历史成交号: {data['deal_id'].values.tolist()}")
    else:
        print('history_deal_list_query error: ', data)
    
    trd_ctx.close()

def example_trade_order_push():
    """
    订单状态推送示例
    """
    print_divider("订单状态推送")
    
    # 自定义推送处理类
    class TradeOrderTest(TradeOrderHandlerBase):
        def on_recv_rsp(self, rsp_pb):
            ret, content = super(TradeOrderTest, self).on_recv_rsp(rsp_pb)
            if ret == RET_OK:
                print(f"收到订单推送: {content}")
            return ret, content
    
    
    trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, 
                                 security_firm=SecurityFirm.FUTUSECURITIES)
    
    # 设置推送处理对象
    trd_ctx.set_handler(TradeOrderTest())
    
    # 解锁交易
    ret, data = trd_ctx.unlock_trade(pwd_unlock)
    if ret == RET_OK:
        # 下单触发推送
        print(trd_ctx.place_order(price=518.0, qty=100, code="HK.00700", 
                                 trd_side=TrdSide.SELL, trd_env=TrdEnv.SIMULATE))
        
        # 等待接收推送
        print("等待接收订单推送...")
        time.sleep(5)
    else:
        print('unlock_trade failed: ', data)
    
    trd_ctx.close()

def example_trade_deal_push():
    """
    成交状态推送示例
    """
    print_divider("成交状态推送")
    
    # 自定义推送处理类
    class TradeDealTest(TradeDealHandlerBase):
        def on_recv_rsp(self, rsp_pb):
            ret, content = super(TradeDealTest, self).on_recv_rsp(rsp_pb)
            if ret == RET_OK:
                print(f"收到成交推送: {content}")
            return ret, content
    
    
    trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, 
                                 security_firm=SecurityFirm.FUTUSECURITIES)
    
    # 设置推送处理对象
    trd_ctx.set_handler(TradeDealTest())
    
    # 解锁交易
    ret, data = trd_ctx.unlock_trade(pwd_unlock)
    if ret == RET_OK:
        # 下单触发成交推送
        print(trd_ctx.place_order(price=518.0, qty=100, code="HK.00700", 
                                 trd_side=TrdSide.BUY, trd_env=TrdEnv.SIMULATE))
        
        # 等待接收推送
        print("等待接收成交推送...")
        time.sleep(5)
    else:
        print('unlock_trade failed: ', data)
    
    trd_ctx.close()

def run_all_examples():
    """
    运行所有交易API示例
    """
    # try:
    #     example_get_acc_list()
    # except Exception as e:
    #     print(f"获取账户列表示例失败: {e}")
    
    try:
        example_unlock_trade()
    except Exception as e:
        print(f"解锁交易示例失败: {e}")
    
    # try:
    #     example_accinfo_query()
    # except Exception as e:
    #     print(f"查询账户资金信息示例失败: {e}")
    
    # try:
    #     example_acctradinginfo_query()
    # except Exception as e:
    #     print(f"查询最大可买可卖量示例失败: {e}")
    
    # try:
    #     example_position_list_query()
    # except Exception as e:
    #     print(f"查询持仓列表示例失败: {e}")
    
    # try:
    #     example_get_margin_ratio()
    # except Exception as e:
    #     print(f"查询股票融资融券数据示例失败: {e}")
    
    # try:
    #     example_get_acc_cash_flow()
    # except Exception as e:
    #     print(f"查询账户现金流水示例失败: {e}")
    
    # try:
    #     example_place_order()
    # except Exception as e:
    #     print(f"下单示例失败: {e}")
    
    # try:
    #     example_modify_order()
    # except Exception as e:
    #     print(f"改单/撤单示例失败: {e}")
    
    # try:
    #     example_cancel_all_order()
    # except Exception as e:
    #     print(f"全部撤单示例失败: {e}")
    
    # try:
    #     example_order_list_query()
    # except Exception as e:
    #     print(f"查询未完成订单示例失败: {e}")
    
    # try:
    #     example_order_fee_query()
    # except Exception as e:
    #     print(f"查询订单费用示例失败: {e}")
    
    # try:
    #     example_history_order_list_query()
    # except Exception as e:
    #     print(f"查询历史订单示例失败: {e}")
    
    # try:
    #     example_deal_list_query()
    # except Exception as e:
    #     print(f"查询当日成交示例失败: {e}")
    
    # try:
    #     example_history_deal_list_query()
    # except Exception as e:
    #     print(f"查询历史成交示例失败: {e}")
    
    # try:
    #     example_trade_order_push()
    # except Exception as e:
    #     print(f"订单状态推送示例失败: {e}")
    
    # try:
    #     example_trade_deal_push()
    # except Exception as e:
    #     print(f"成交状态推送示例失败: {e}")

if __name__ == "__main__":
    print("富途OpenAPI交易接口示例程序\n")
    print("注意: 运行前请确保OpenD已正确启动且连接到富途服务器\n")
    
    # 运行所有示例
    run_all_examples() 