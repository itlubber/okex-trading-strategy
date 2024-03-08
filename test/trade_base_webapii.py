import sys


# 将项目文件路径添加到环境变量中
sys.path.append(".")


import time
import requests
import threading
from utils.logger import logger
from api.okex_client import Client
from uuid import uuid4
from config import port, market_time_sleep


class TradingSimulator(threading.Thread):

    API_KEY = None
    API_SECRET_KEY = None
    PASSPHRASE = None
    ACCOUNTNUMBER = None
    ORDERNUMBER = None
    TREND_API = None
    CLIENT = None
    
    def __init__(self, API_KEY = "", API_SECRET_KEY = "", PASSPHRASE = "", TREND_API=f"http://127.0.0.1:{port}/strategy_boll", ACCOUNTNUMBER=-1, ORDERNUMBER=1):
        """
        模拟调用 策略web服务 进行交易, 测试账号无法完成下单操作和账户余额查询操作
        :param API_KEY : 测试账户 api key
        :param API_SECRET_KEY : 测试账户 api secret key
        :param PASSPHRASE : 测试账户 passphrase
        :param TREND_API : 在线服务的接口地址, 默认 http://127.0.0.1:80/strategy_boll
        :param ACCOUNTNUMBER : 测试账户编号, 默认为 -1
        :param ORDERNUMBER : 测试购买服务数量, 默认为 1
        """
        super().__init__()
        TradingSimulator.API_KEY = API_KEY
        TradingSimulator.API_SECRET_KEY = API_SECRET_KEY
        TradingSimulator.PASSPHRASE = PASSPHRASE
        
        TradingSimulator.TREND_API = TREND_API
        TradingSimulator.ACCOUNTNUMBER = ACCOUNTNUMBER
        TradingSimulator.ORDERNUMBER = ORDERNUMBER
        
        if TradingSimulator.CLIENT is None:
            TradingSimulator.CLIENT = Client(API_KEY=TradingSimulator.API_KEY, API_SECRET_KEY=TradingSimulator.API_SECRET_KEY, PASSPHRASE=TradingSimulator.PASSPHRASE)
    
    def get_strategy_signal(self, underlying_type="SWAP", underlying="ETH-USDT-SWAP", ccy="USDT"):
        """
        获取策略返回的信号, 获取信号后, 通过下单函数进行交易
        """
        position = TradingSimulator.CLIENT.get_positions(underlying_type=underlying_type, underlying=underlying)
        _account = TradingSimulator.CLIENT.get_balance(ccy=ccy)
        
        # 模拟盘账户无法获取账户相关的接口信息
        if _account is None:
            logger.error("无法获取账户信息, 默认当前账户为初始化状态 ......")
            # _account = {
            #     "cashBal": "0",
            #     "ccy": ccy,
            # }
            raise Exception(f"当前账户获取账户余额信息失败 ...")
        
        # 合成接口请求信息
        account = {
                        "account": {
                            "accountbal": float(_account.get("cashBal", "0")),
                            "accountcurrency": _account.get("ccy", ccy),
                            "accountnumber": TradingSimulator.ACCOUNTNUMBER,
                            "accountordnum": TradingSimulator.ORDERNUMBER,
                            "accountpnl": float(_account.get("cashBal", "0")) - 1000 * TradingSimulator.ORDERNUMBER
                        },
                        "agreement": [position]
                    }
        json_args = {
                        "batch": {
                            "event": "WEB_API_TEST",
                            "requestid": 0,
                            "servicemode": "0"
                        },
                        "accounts": [account]
                    }
        
        # 获取策略返回信号, 根据信号进行相关操作
        response = requests.post(url=TradingSimulator.TREND_API, json=json_args, timeout=market_time_sleep).json()
        
        if response.get("status") == 0:
            if response.get("accounts"):
                # 如果存在信号, 则返回相应的操作信息, 仅有一个账号的情况
                return response.get("accounts")[0].get("agreement", {})
        else:
            raise Exception("获取策略接口返回失败。")
    
    def run(self):
        while True:
            try:
                # 获取操作信号
                response = self.get_strategy_signal()
                if response:
                    # 自定义测试账号下单的订单编号: S{时间}{随机字符编码}
                    response["clOrdId"] = f"S{time.strftime('%Y%m%d%Z%H%M%S')}{str(uuid4()).split('-')[-1]}"
                    # 执行下单操作
                    res = TradingSimulator.CLIENT.place_order(response)
                    # 判断下单是否成功
                    if res and res.get("code") == "0":
                        logger.info(res.get("data"))
                else:
                    logger.info("no market signale.")
            except Exception as error:
                logger.error(f"{error}")
            
            # 每 6s 请求市场信号
            time.sleep(market_time_sleep)


if __name__ == '__main__':
    # 初始化
    trading_simulator = TradingSimulator()
    # 启动测试
    trading_simulator.start()
