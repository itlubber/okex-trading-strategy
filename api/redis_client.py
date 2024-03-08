import time
import redis
import pickle
import threading
from traceback import format_exc
import numpy as np
import requests.exceptions
import config
from utils.logger import logger
from utils.methods import get_period_gap
from api.okex_client import Client
from trends_forecasting.lstm_attention_model import ForecastModel
from handlers.StrategyBoll import boll_params


class RedisClient(threading.Thread):

    client = Client()
    redis_pool = redis.ConnectionPool(**config.redis_connect_options)
    redis_conn = redis.Redis(connection_pool=redis_pool)

    def cache_dataframe(self, df, key):
        self.redis_conn.set(key, pickle.dumps(df))
        # 5 分钟未更新行情数据, 将从缓存中删除相应的 key
        self.redis_conn.expire(key, config.market_time_sleep * 50)

    def load_dataframe(self, key):
        return pickle.loads(self.redis_conn.get(key))

    def run(self):
        # 每秒钟获取行情数据存储至redis缓存
        while True:
            try:
                quotations = self.client.get_history_candlesticks(instId=boll_params.underlying, bar=boll_params.time_bar, limit=boll_params.window_limit, c1=boll_params.c1, c2=boll_params.c2, window=boll_params.window, cx=boll_params.cx, window_short=boll_params.window_short, window_long=boll_params.window_long)
                if quotations is not None and len(quotations) > 0:
                    self.cache_dataframe(quotations, "market")

            except requests.exceptions.ConnectionError as error:
                logger.error(f"请求行情数据失败, 错误信息 {format_exc()}")

            time.sleep(config.market_time_sleep)


class LSTMAttentionModel(RedisClient):
    model = None
    
    def __init__(self, contract_code="ETH-USDT-SWAP", period="5m"):
        super().__init__()
        self.contract_code = contract_code
        self.bar = period
        self.key = f"{self.contract_code}_{self.bar}_trend"
        self.expire_time = int(get_period_gap(period)/1000) * config.periods
        if self.model is None:
            self.model = ForecastModel(contract_code=self.contract_code, period=self.bar)

    def run(self):
        while True:
            try:
                trend = self.model.predict()
                logger.info(trend)
                self.redis_conn.set(self.key, int(np.argmax(trend)))
                self.redis_conn.expire(self.key, self.expire_time)
            except Exception as error:
                logger.error(f"使用 lstm attention 模型预测未来 T+{config.periods}期涨跌失败, 错误信息 {error}")

            time.sleep(config.market_time_sleep)
    
    def get_trend_forecast(self):
        return self.redis_conn.get(self.key)


redis_client = RedisClient()
eth_lstm_model = LSTMAttentionModel(contract_code="ETH-USDT-SWAP", period="5m")


if __name__ == '__main__':
    redis_client.start()
    eth_lstm_model.start()

