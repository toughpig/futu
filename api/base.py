#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Examples of FUTU OpenAPI basic functionality.
This includes connection handling, system notifications, and other base API functions.
"""

import time
import logging
from futu import *

# Set up logging
logger = logging.getLogger('futu.api.base')
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

class SysNotifyTest(SysNotifyHandlerBase):
    """
    系统通知处理类示例
    """
    def on_recv_rsp(self, rsp_str):
        ret_code, data = super(SysNotifyTest, self).on_recv_rsp(rsp_str)
        notify_type, sub_type, msg = data
        if ret_code != RET_OK:
            logger.debug("SysNotifyTest: error, msg: {}".format(msg))
            return RET_ERROR, data
            
        if notify_type == SysNotifyType.GTW_EVENT:  # OpenD 事件通知
            print("GTW_EVENT, type: {} msg: {}".format(sub_type, msg))
            
        elif notify_type == SysNotifyType.PROGRAM_STATUS:  # 程序状态变化通知
            print("PROGRAM_STATUS, type: {} msg: {}".format(sub_type, msg))
            
        elif notify_type == SysNotifyType.CONN_STATUS:  # 连接状态变化通知
            print("CONN_STATUS, qot: {}".format(msg['qot_logined']))
            print("CONN_STATUS, trd: {}".format(msg['trd_logined']))
            
        elif notify_type == SysNotifyType.QOT_RIGHT:  # 行情权限变化通知
            print("QOT_RIGHT, hk: {}".format(msg['hk_qot_right']))
            print("QOT_RIGHT, hk_option: {}".format(msg['hk_option_qot_right']))
            print("QOT_RIGHT, hk_future: {}".format(msg['hk_future_qot_right']))
            print("QOT_RIGHT, us: {}".format(msg['us_qot_right']))
            print("QOT_RIGHT, us_option: {}".format(msg['us_option_qot_right']))
            print("QOT_RIGHT, cn: {}".format(msg['cn_qot_right']))
            print("QOT_RIGHT, us_index: {}".format(msg['us_index_qot_right']))
            print("QOT_RIGHT, us_otc: {}".format(msg['us_otc_qot_right']))
            print("QOT_RIGHT, sg_future: {}".format(msg['sg_future_qot_right']))
            print("QOT_RIGHT, jp_future: {}".format(msg['jp_future_qot_right']))
            print("QOT_RIGHT, us_future_cme: {}".format(msg['us_future_qot_right_cme']))
            print("QOT_RIGHT, us_future_cbot: {}".format(msg['us_future_qot_right_cbot']))
            print("QOT_RIGHT, us_future_nymex: {}".format(msg['us_future_qot_right_nymex']))
            print("QOT_RIGHT, us_future_comex: {}".format(msg['us_future_qot_right_comex']))
            print("QOT_RIGHT, us_future_cboe: {}".format(msg['us_future_qot_right_cboe']))
            
        return RET_OK, data

def example_sys_notify():
    """
    系统通知监听示例
    """
    print_divider("系统通知监听")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    handler = SysNotifyTest()
    quote_ctx.set_handler(handler)  # 设置回调
    
    print("开始接收系统通知，将持续15秒...")
    time.sleep(15)  # 设置脚本接收 OpenD 的推送持续时间为15秒
    
    quote_ctx.close()  # 结束后记得关闭当条连接，防止连接条数用尽

def example_init_connect():
    """
    初始化连接示例
    
    注意：这是直接使用底层API的示例，通常您不需要直接调用此函数，
    因为在创建OpenQuoteContext和OpenSecTradeContext时会自动完成初始化连接
    """
    print_divider("初始化连接")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    print(f"连接ID: {quote_ctx.get_conn_id()}")
    print(f"连接状态: {'已连接' if quote_ctx.is_connected() else '未连接'}")
    print(f"用户ID: {quote_ctx.get_login_user_id()}")
    
    # 获取全局状态
    ret, data = quote_ctx.get_global_state()
    if ret == RET_OK:
        print(f"市场状态: {data}")
    else:
        print(f"获取市场状态失败: {data}")
    
    quote_ctx.close()

def example_keep_alive():
    """
    心跳保活示例
    
    注意：这是底层API的示例，通常您不需要直接调用此函数，
    因为OpenQuoteContext和OpenSecTradeContext会自动处理心跳
    """
    print_divider("心跳保活")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    print("模拟客户端运行10秒钟，自动发送心跳...")
    start_time = time.time()
    
    # 正常情况下，SDK会自动发送心跳，此处仅作演示
    while time.time() - start_time < 10:
        time.sleep(1)
        
        # 检查连接状态
        if quote_ctx.is_connected():
            print("连接正常，心跳保持中...")
        else:
            print("连接已断开!")
            break
    
    quote_ctx.close()

def example_get_login_info():
    """
    获取登录信息示例
    """
    print_divider("获取登录信息")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 获取用户ID
    user_id = quote_ctx.get_login_user_id()
    print(f"登录用户ID: {user_id}")
    
    # 获取全局状态
    ret, data = quote_ctx.get_global_state()
    if ret == RET_OK:
        print(f"全局状态: {data}")
        if data['qot_logined']:
            print("行情已登录")
        if data['trd_logined']:
            print("交易已登录")
    else:
        print(f"获取全局状态失败: {data}")
    
    quote_ctx.close()

def example_error_handling():
    """
    错误处理示例
    """
    print_divider("错误处理")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 故意使用错误的证券代码来演示错误处理
    ret, data = quote_ctx.get_market_snapshot(['INVALID.CODE'])
    if ret == RET_OK:
        print(data)
    else:
        print(f"调用失败: {data}")
        # 根据错误信息进行处理
        if "stock_code is wrong" in data:
            print("证券代码格式错误，请使用正确的市场前缀，如HK.00700")
    
    quote_ctx.close()

def example_async_callback():
    """
    使用异步回调的示例 - 监听系统通知
    """
    print_divider("使用异步回调")
    
    class MyHandler(SysNotifyHandlerBase):
        def on_recv_rsp(self, rsp_str):
            ret_code, data = super(MyHandler, self).on_recv_rsp(rsp_str)
            if ret_code != RET_OK:
                print(f"系统通知接收错误: {data}")
                return RET_ERROR, data
                
            notify_type, sub_type, msg = data
            print(f"收到系统通知: {notify_type}, 子类型: {sub_type}")
            print(f"详细信息: {msg}")
            return RET_OK, data
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 设置回调处理对象
    handler = MyHandler()
    quote_ctx.set_handler(handler)
    
    print("等待系统通知，10秒后结束...")
    time.sleep(10)
    
    quote_ctx.close()

def example_connection_options():
    """
    连接参数选项示例
    """
    print_divider("连接参数选项")
    
    # 详细指定连接选项
    quote_ctx = OpenQuoteContext(
        host='127.0.0.1',           # OpenD的地址
        port=11111,                 # OpenD的端口
        is_encrypt=False,           # 是否加密通信，一般本地连接不加密
        password_md5=None,          # 密码的MD5值，用于需要密码的情况
        block=True,                 # 初始化时是否阻塞
        connect_timeout=10,         # 连接超时设置，单位秒
        recv_timeout=10,            # 接收数据超时设置，单位秒
        client_id=0,                # 用于区分不同连接的ID
        is_auto_retry=True          # 是否自动重连
    )
    
    print(f"连接ID: {quote_ctx.get_conn_id()}")
    print(f"连接状态: {'已连接' if quote_ctx.is_connected() else '未连接'}")
    
    quote_ctx.close()

def example_set_log_config():
    """
    日志配置示例
    """
    print_divider("日志配置")
    
    # 配置Futu API日志
    set_futu_debug_model(True)  # 开启调试模式
    
    # 设置日志配置
    common_config = FutuCommonConfig()
    common_config.enable_proto_encrypt = True    # 启用协议加密
    common_config.client_info = "MyFutuAPIApp"   # 设置客户端信息标识
    common_config.proto_fmt = ProtoFMT.Json       # 协议格式
    common_config.is_enable_proto_encrypt_file = False  # 是否写入加密通信协议文件
    common_config.init_all()  # 初始化应用配置项
    
    # 创建上下文
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 验证配置是否生效
    print("已启用调试模式和协议加密")
    
    quote_ctx.close()

def example_get_global_state():
    """
    获取全局状态示例
    """
    print_divider("获取全局状态")
    
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    ret, data = quote_ctx.get_global_state()
    if ret == RET_OK:
        print("全局状态:")
        for key, value in data.items():
            print(f"  {key}: {value}")
            
        # 检查交易日期
        if 'trade_date' in data:
            print(f"当前交易日: {data['trade_date']}")
            
        # 检查行情登录状态
        if 'qot_logined' in data and data['qot_logined']:
            print("行情已登录，可以请求行情数据")
        else:
            print("行情未登录")
            
        # 检查交易登录状态
        if 'trd_logined' in data and data['trd_logined']:
            print("交易已登录，可以进行交易操作")
        else:
            print("交易未登录")
    else:
        print(f"获取全局状态失败: {data}")
    
    quote_ctx.close()

def run_all_examples():
    """
    运行所有基础API示例
    """
    # try:
    #     example_sys_notify()
    # except Exception as e:
    #     print(f"系统通知示例运行失败: {e}")
    
    # try:
    #     example_init_connect()
    # except Exception as e:
    #     print(f"初始化连接示例运行失败: {e}")
    
    # try:
    #     example_keep_alive()
    # except Exception as e:
    #     print(f"心跳保活示例运行失败: {e}")
    
    try:
        example_get_login_info()
    except Exception as e:
        print(f"获取登录信息示例运行失败: {e}")
        
    # try:
    #     example_error_handling()
    # except Exception as e:
    #     print(f"错误处理示例运行失败: {e}")
        
    # try:
    #     example_async_callback()
    # except Exception as e:
    #     print(f"异步回调示例运行失败: {e}")
        
    # try:
    #     example_connection_options()
    # except Exception as e:
    #     print(f"连接参数选项示例运行失败: {e}")
        
    # try:
    #     example_set_log_config()
    # except Exception as e:
    #     print(f"日志配置示例运行失败: {e}")
        
    # try:
    #     example_get_global_state()
    # except Exception as e:
    #     print(f"获取全局状态示例运行失败: {e}")

if __name__ == "__main__":
    print("富途OpenAPI基础功能示例程序\n")
    print("注意: 运行前请确保OpenD已正确启动且连接到富途服务器\n")
    
    # 运行所有示例
    run_all_examples() 