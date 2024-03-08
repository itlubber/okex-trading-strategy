import json
import time
import math
import requests
import numpy as np
from traceback import format_exc
import pandas as pd
from utils.logger import logger
from utils.methods import get_timestamp_millisecond, get_period_gap, timestamp2datetime, get_timestamp
from utils.data_preprocess import *
import api.okex.consts as c
import api.okex.utils as utils
import api.okex.exceptions as exceptions
from datetime import datetime
from handlers.StrategyBoll import boll_params as params


class Client:

    def __init__(self, use_server_time=False, API_KEY="", API_SECRET_KEY="", PASSPHRASE=""):
        self.API_KEY = API_KEY
        self.API_SECRET_KEY = API_SECRET_KEY
        self.PASSPHRASE = PASSPHRASE
        self.use_server_time = use_server_time

    @staticmethod
    def _get_timestamp():
        url = c.API_URL + c.SERVER_TIMESTAMP_URL
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return ""

    @staticmethod
    def stamp2time(_):
        return datetime.fromtimestamp(int(np.ceil(_ * 0.001))).isoformat()

    @staticmethod
    def time2stamp(_):
        return int(1000 * datetime.strptime(_, "%Y-%m-%dT%H:%M:%S").timestamp())

    def _request(self, method, request_path, params, cursor=False):
        if method == c.GET:
            request_path = request_path + utils.parse_params_to_str(params)
        url = c.API_URL + request_path
        timestamp = utils.get_timestamp()

        if self.use_server_time:
            timestamp = self._get_timestamp()

        body = json.dumps(params) if method == c.POST else ""
        sign = utils.sign(utils.pre_hash(timestamp, method, request_path, str(body)), self.API_SECRET_KEY)
        header = utils.get_header(self.API_KEY, sign, timestamp, self.PASSPHRASE)

        response = None
        if method == c.GET:
            response = requests.get(url, headers=header)
        elif method == c.POST:
            response = requests.post(url, data=body, headers=header)
        elif method == c.DELETE:
            response = requests.delete(url, headers=header)

        if not str(response.status_code).startswith('2'):
            raise exceptions.OkexAPIException(response)
        try:
            res_header = response.headers
            if cursor:
                r = dict()
                try:
                    r['before'] = res_header['OK-BEFORE']
                    r['after'] = res_header['OK-AFTER']
                except:
                    pass
                return response.json(), r
            else:
                return response.json()

        except ValueError:
            raise exceptions.OkexRequestException('Invalid Response: %s' % response.text)

    def get_balance(self, ccy="USDT"):
        res = self._request("GET", "/api/v5/account/balance", {"ccy": ccy})
        if res.get("code") == "0":
            _ = res.get("data", [])
            if _ and len(_):
                _ = _[0].get("details", [])
                if _ and len(_):
                    return _[0]
        else:
            raise Exception(f"获取账户余额信息失败, 错误信息: {res}")

    def get_positions(self, underlying_type="SWAP", underlying="ETH-USDT-SWAP"):
        res = self._request("GET", "/api/v5/account/positions", {"instType": underlying_type, "instId": underlying})
        if res.get("code") == "0":
            _ = res.get("data", [])
            if _ and len(_) > 0:
                return _[0]
            else:
                return {
                    "adl": "",
                    "availPos": "",
                    "avgPx": "",
                    "cTime": "",
                    "ccy": "",
                    "deltaBS": "",
                    "deltaPA": "",
                    "gammaBS": "",
                    "gammaPA": "",
                    "imr": "",
                    "instId": "",
                    "instType": "",
                    "interest": "",
                    "last": "",
                    "lever": "",
                    "liab": "",
                    "liabCcy": "",
                    "liqPx": "",
                    "margin": "",
                    "mgnMode": "",
                    "mgnRatio": "",
                    "mmr": "",
                    "notionalUsd": "",
                    "optVal": "",
                    "pTime": "",
                    "pos": "",
                    "posCcy": "",
                    "posId": "",
                    "posSide": "",
                    "thetaBS": "",
                    "thetaPA": "",
                    "tradeId": "",
                    "uTime": "",
                    "upl": "",
                    "uplRatio": "",
                    "vegaBS": "",
                    "vegaPA": ""
                }
        else:
            raise Exception(f"获取持仓信息失败, 错误信息: {res}")

    def get_history_candlesticks(self, instId="ETH-USDT-SWAP", bar=params.time_bar, limit=params.window_limit,
                                 c1=params.c1, c2=params.c2, window=params.window, cx=params.cx,
                                 window_short=params.window_short, window_long=params.window_long):

        short = 'ma' + str(window_short)
        long = 'ma' + str(window_long)

        _ = int(time.time() * 1000)
        result = self._request("GET", "/api/v5/market/candles",
                               {'instId': instId, 'after': _, 'bar': bar, 'limit': limit, "before": ""})

        quotations = pd.DataFrame(result.get("data"), dtype=np.float64,
                                  columns=["timestamp", "open", "high", "low", "close", "volume", "currency_volume"])
        quotations = quotations.sort_values("timestamp")
        quotations.index = range(-len(quotations) + 1, 1)

        quotations['boll'] = quotations["close"].rolling(window=window, min_periods=1, center=False).mean()
        quotations['std'] = quotations["close"].rolling(window=window, min_periods=1, center=False).std(ddof=0)
        short = 'ma' + str(window_short)
        long = 'ma' + str(window_long)
        quotations[short] = quotations["close"].rolling(window=window_short, min_periods=1, center=False).mean()
        quotations[long] = quotations["close"].rolling(window=window_long, min_periods=1, center=False).mean()
        quotations["c1"] = np.where(quotations[short] > quotations[long], cx, c1)
        quotations["c2"] = np.where(quotations[short] > quotations[long], c2, cx)
        quotations['upper'] = quotations['boll'] + quotations["c1"] * quotations['std']
        quotations['lower'] = quotations['boll'] - quotations["c2"] * quotations['std']
        quotations['gi'] = abs(quotations['close'].diff().rolling(window=6 - 1).apply(lambda x: np.sum(x[x > 0])))
        quotations['gd'] = abs(quotations['close'].diff().rolling(window=6 - 1).apply(lambda x: np.sum(x[x < 0])))
        quotations['rsi'] = quotations['gi'] / (quotations['gi'] + quotations['gd']) * 100
        quotations['avg_vol'] = quotations["volume"].rolling(window=25, min_periods=1, center=False).mean()
        quotations['amplitude'] = (quotations['upper'] - quotations['lower']) / quotations['close']

        return quotations

    def get_history_candlesticks_for_R(self, instId="ETH-USDT-SWAP", bar="5m", limit="100"):
        size = 0
        _ = int(time.time() * 1000)
        quotations_all = None
        while size < 600:
            result = self._request("GET", "/api/v5/market/candles",
                                   {'instId': instId, 'after': int(_), 'bar': bar, 'limit': limit, "before": ""})
            quotations = pd.DataFrame(result.get("data"), dtype=np.float64,
                                      columns=["timestamp", "open", "high", "low", "close", "volume",
                                               "currency_volume"])
            ts =  list(quotations.tail(1)['timestamp'])
            if ts :
                _ = ts[0]
            quotations = quotations.sort_values("timestamp")
            quotations['timestamp'] = quotations['timestamp'].apply(func=lambda x: timestamp2datetime(x, format='%Y-%m-%dT%H:%M:%S'))
            logger.info(quotations)
            quotations_all = pd.concat([quotations,quotations_all])
            size = len(quotations_all)
        return quotations_all

    def get_latest_close(self, instId="ETH-USDT-SWAP", bar='1m', limit='1', after=""):
        if after is None or after.strip() == "":
            return 0.0
        res = self._request("GET", "/api/v5/market/candles",
                            {'instId': instId, 'after': after, 'bar': bar, 'limit': limit}).get("data", [])[0]
        return float(res[4])

    def place_order(self, signale: dict = {}):
        _ = self._request("POST", "/api/v5/trade/order", {
            'instId': signale.get("instId", "ETH-USDT-SWAP")
            , 'ordType': signale.get("ordType", "market")
            , 'tdMode': signale.get("tdMode", "cross")
            , 'side': signale.get("side", "")
            , 'sz': signale.get("sz", "")
            , 'ccy': signale.get("ccy", "")
            , 'clOrdId': signale.get("clOrdId", "")
            , 'tag': signale.get("tag", "")
            , 'posSide': signale.get("posSide", "")
            , 'px': signale.get("px", "")
            , 'reduceOnly': signale.get("reduceOnly", "")
        })
        if _ and _.get("code") == 0:
            return _
        else:
            raise Exception(f"下单交易失败\n策略交易信号:\n{signale}\n下单返回信息:\n{_}")

    def get_market_data(self, contract_code="ETH-USDT-SWAP", period="1m"):
        batch_size = get_period_gap(period) * 100
        end = get_timestamp_millisecond()
        start = end - math.ceil(config.time_steps / 100 + 1) * 100 * get_period_gap(period)
        try:
            data = pd.DataFrame(columns=["id", "open", "high", "low", "close", "vol", "amount"])
            while start < end:
                try:
                    _ = self._request(
                        method="GET"
                        , request_path="/api/v5/market/history-candles"
                        , params={"instId": contract_code, "bar": period, "before": start, "after": start + batch_size}
                    )

                    if _ and _.get("code") == "0":
                        data = pd.concat([data, pd.DataFrame(_.get("data"),
                                                             columns=["id", "open", "high", "low", "close", "vol",
                                                                      "amount"])])
                    else:
                        continue
                except requests.exceptions.ConnectionError as error:
                    logger.info(
                        f"{timestamp2datetime(start)} - {timestamp2datetime(start + batch_size)} request error : {error}")
                    continue

                time.sleep(0.1)
                start += batch_size

            logger.info(f"current date is {timestamp2datetime(data.id.max())}")
            data = data.sort_values("id").drop_duplicates(subset=["id"], keep="last").reset_index(drop=True).drop(
                columns=["id"])
            data = data.astype(float)
            data = get_all_target(data)
            return StandardScaler().fit_transform(data.values[-config.time_steps:])
        except Exception as error:
            logger.info(f"query data error, trace back {error}")
            return StandardScaler().fit_transform(np.random.random((config.time_steps, config.feature_dims)))

    def get_train_data(self, contract_code="ETH-USDT-SWAP", period="1m",
                       start=get_timestamp("2020-01-01 00:00:00", query="ms"), end=get_timestamp_millisecond(),
                       batch_size=100):
        data = pd.DataFrame(columns=["id", "open", "high", "low", "close", "vol", "amount"])
        logger.info(
            f"query {contract_code} {period} kline data, from {timestamp2datetime(start)} to {timestamp2datetime(end)}")
        batch_size *= get_period_gap(period)
        while start < end:
            try:
                _ = self._request(
                    method="GET"
                    , request_path="/api/v5/market/history-candles"
                    , params={"instId": contract_code, "bar": period, "before": start, "after": start + batch_size}
                )
            except requests.exceptions.ConnectionError as error:
                logger.info(
                    f"{timestamp2datetime(start)} - {timestamp2datetime(start + batch_size)} request error : {error}")
                continue
            if _:
                _ = _.get("data", [])
                if len(_):
                    data = pd.concat(
                        [data, pd.DataFrame(_, columns=["id", "open", "high", "low", "close", "vol", "amount"])])
                    logger.info(
                        f"date range : {timestamp2datetime(start)} - {timestamp2datetime(start + batch_size)}, response data length : {len(_)}")
                else:
                    logger.info(f"{timestamp2datetime(start)} - {timestamp2datetime(start + batch_size)} no data.")

            time.sleep(0.1)
            start += batch_size

        data = data.sort_values("id").drop_duplicates(subset=["id"], keep="last").reset_index(
            drop=True)  # .drop(columns=["id"])
        # data = data.astype(float)

        data.to_csv(f"{contract_code}_{period}_train_data.csv", index=False)

        return data


if __name__ == '__main__':
    client = Client()
    # data = client.get_train_data(contract_code="ETH-USDT-SWAP", period="1m", start=get_timestamp("2019-01-01 00:00:00", query="ms"))
    data = client.get_market_data(contract_code="ETH-USDT-SWAP", period="5m")
    logger.info(data.shape)
