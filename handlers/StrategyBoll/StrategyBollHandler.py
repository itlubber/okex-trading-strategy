import json
import time
from jsonpath import jsonpath
import traceback
import numpy as np
import math
import pandas as pd
from api.okex_client import Client
from api.redis_client import redis_client
from handlers.BaseHandler import *
from utils.emails import write_response_html
from handlers.StrategyBoll import boll_params as params
from utils.logger import logger


pd.set_option('display.width', 5000)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)


def get_poss(row):
    """
    根据持仓方向获取当前持仓数
    """
    if row["posSide"] == "long":
        return row["pos"]
    elif row["posSide"] == "short":
        return -row["pos"]
    else:
        return 0


def adjustment_size_buy(row, smax=params.smax, smin=-params.smin, sz=params.sz):
    """
    根据账户最大持仓和账户服务购买数量返回可以开仓或加仓的数量
    """
    if smin*row["account_ordnum"] <= row["posS"] <= smax*row["account_ordnum"]:
        if smin*row["account_ordnum"] > row["posS"] - sz*row["account_ordnum"]:
            return row["posS"] - smin*row["account_ordnum"]
        elif row["posS"] + sz*row["account_ordnum"] > smax*row["account_ordnum"]:
            return smax*row["account_ordnum"] - row["posS"]
        else:
            return sz*row["account_ordnum"]
    else:
        return 0


def adjustment_size_sell(row, sz=params.sz):
    """
    根据账户最大持仓和账户服务购买数量返回可以平仓的数量
    """
    if 0 < abs(row["posS"]) <= sz*row["account_ordnum"]:
        return abs(row["posS"])
    elif abs(row["posS"]) > sz*row["account_ordnum"]:
        return sz*row["account_ordnum"]
    else:
        return 0


def get_market_signal(ca1=params.ca1, key1="ETH-USDT-SWAP_5m_trend", key2="garch_rscript_trend"):
    # 获取预测标签，如果redis里不存在该键，返回 -1
    lstm = int(redis_client.redis_conn.get(key1) or -1)
    garch = float(redis_client.redis_conn.get(key2) or -1)
    logger.info(f"lstm:{lstm}")
    logger.info(f"garch:{garch}")


    if garch > ca1 and lstm > -1:
        cons_buy_com = lstm == 2
        cons_sel_com = lstm == 0
    else:
        cons_buy_com = False
        cons_sel_com = False

    return cons_buy_com, cons_sel_com


def write_strategy(row, instId=params.underlying, tdMode=params.tdMode, ordType=params.ordType):
    """
    返回操作策略信息
    """
    if row["strategy"] in ["cut", "close"] and row["sz_adjustment_sell"] > 0:
        return {"account_number": row["account_number"], "agreement": {"instId": instId, "tdMode": tdMode, "side": row["side"], "posSide": row["posSide"], "ordType": ordType, "sz": str(row["sz_adjustment_sell"])}}
    elif row["strategy"] in ["open", "add"] and row["sz_adjustment_buy"] > 0:
        return {"account_number": row["account_number"], "agreement": {"instId": instId, "tdMode": tdMode, "side": row["side"], "posSide": row["posSide"], "ordType": ordType, "sz": str(row["sz_adjustment_buy"])}}
    else:
        return np.nan


def trade_mix_strategy_Boll_1X2(quotations, query, ca1=params.ca1, ca2=params.ca2, ca3=params.ca3, tpls=params.tpls, smax=params.smax, smin=-params.smin, slr=params.slr, slp=params.slp, spp=params.spp, spr=params.spr):
    cons_buy_com, cons_sel_com = get_market_signal(ca1=ca1)

    cons_stop = (query["uplRatio"] > spr) | (query["uplRatio"] < -slr) | (query["upl"] > spp) | (query["upl"] < -slp) & (cons_buy_com==False) & (cons_sel_com==False)
    
    cons_buy_limit = query["posS"] < smax * query.reset_index()["account_ordnum"].values
    cons_sel_limit = query["posS"] > smin * query.reset_index()["account_ordnum"].values

    cons_buy_open = (query["posS"] == 0) & cons_buy_com & cons_buy_limit
    cons_sel_open = (query["posS"] == 0) & cons_sel_com & cons_sel_limit

    cons_buy_add = (query["posS"] > 0) & cons_buy_limit & cons_buy_com & (quotations['close'][0] < query["tpli"] - tpls)
    cons_sel_add = (query["posS"] < 0) & cons_sel_limit & cons_sel_com & (quotations['close'][0] > query["tpli"] + tpls)

    cons_buy_cut = (query["posS"] < 0) & (cons_buy_com | cons_stop)
    cons_sel_cut = (query["posS"] > 0) & (cons_sel_com | cons_stop)
    
    cons_buy_close = (query["posS"] < 0) & cons_buy_com & False   #【新增】
    cons_sel_close = (query["posS"] > 0) & cons_sel_com & False   #【新增】
    
    # 将市场信号与目标信息合并 [side, posSide, strategy]
    # 必须保证 减仓和平仓操作在 加仓和开仓之前, 如果出现账户即有加仓和平仓信号, 优先平仓操作(一个账号保证一次只返回一种操作)
    res = pd.DataFrame(data=np.vstack((
                np.hstack((cons_buy_close.reset_index().values, np.array([['buy', 'short', "close"]]).repeat(len(query), axis=0))),   #【新增】
                np.hstack((cons_sel_close.reset_index().values, np.array([['sell', 'long', "close"]]).repeat(len(query), axis=0))),   #【新增】
                np.hstack((cons_buy_cut.reset_index().values, np.array([['buy', 'short', "cut"]]).repeat(len(query), axis=0))),
                np.hstack((cons_sel_cut.reset_index().values, np.array([['sell', 'long', "cut"]]).repeat(len(query), axis=0))),
                np.hstack((cons_buy_open.reset_index().values, np.array([['buy', 'long', "open"]]).repeat(len(query), axis=0))),
                np.hstack((cons_sel_open.reset_index().values, np.array([['sell', 'short', "open"]]).repeat(len(query), axis=0))),
                np.hstack((cons_buy_add.reset_index().values, np.array([['buy', 'long', "add"]]).repeat(len(query), axis=0))),
                np.hstack((cons_sel_add.reset_index().values, np.array([['sell', 'short', "add"]]).repeat(len(query), axis=0))),
            )), columns=["account_number", "account_ordnum", "sz_adjustment_buy", "sz_adjustment_sell", "filter", "side", "posSide", "strategy"])

    res = res[res["filter"]].drop_duplicates(subset=["account_number"], keep="first")

    if len(res):
        return res.apply(write_strategy, axis=1).dropna().tolist()
    else:
        return


class StrategyBollHandler(BaseHandler):
    # client = Client()

    def post(self):
        batch = self.json_args.get("batch", {})
        accounts = self.json_args.get("accounts", [])

        if accounts is not None and len(accounts) > 0:
            account_number = jsonpath(accounts, "$[*].account.accountnumber")
            account_ordnum = jsonpath(accounts, "$[*].account.accountordnum")
            # 账户盈亏金额
            account_upl = jsonpath(accounts, "$[*].account.accountpnl")
            tpli = jsonpath(accounts, "$[*].agreement[0].avgPx")
            upl = jsonpath(accounts, "$[*].agreement[0].upl")
            uplRatio = jsonpath(accounts, "$[*].agreement[0].uplRatio")
            pos = jsonpath(accounts, "$[*].agreement[0].pos")
            posSide = jsonpath(accounts, "$[*].agreement[0].posSide")

            # 将获取的参数转为pd.DataFrame()
            query = pd.DataFrame(list(zip(account_number, account_ordnum, tpli, pos, posSide, upl, uplRatio, account_upl)), columns=["account_number", "account_ordnum", "tpli", "pos", "posSide", "upl", "uplRatio", "account_upl"]).replace("", np.nan).dropna(how="all").fillna("0")
            query[["account_number", "account_ordnum", "pos"]] = query[["account_number", "account_ordnum", "pos"]].astype(int)
            query[["tpli", "upl", "uplRatio", "account_upl"]] = query[["tpli", "upl", "uplRatio", "account_upl"]].astype(float)
            # query = query[query["account_number"].isin([197, 324, 321, 196, 190, 349, 194, 366, 363, 347, 127, 125, 123, 121, 126, 124, 128, 119, 118, 441, 120, 101, 471])]
            query["posS"] = query[["posSide", "pos"]].apply(get_poss, axis=1).astype(int)
            
            # 依据购买的服务数量, 对账户的持仓、可买数量、可卖数量进行计算
            query["posS_adjustment"] = (query["posS"]/query["account_ordnum"]).apply(lambda x: math.ceil(x) if x > 0 else math.floor(x))
            query["sz_adjustment_buy"] = query[["account_ordnum", "posS"]].apply(lambda row: adjustment_size_buy(row, smax=params.smax, smin=-params.smin, sz=params.sz), axis=1)
            query["sz_adjustment_sell"] = query[["account_ordnum", "posS"]].apply(lambda row: adjustment_size_sell(row, sz=params.sz), axis=1)
            
            # 将计算信号后需要用到的字段通过 index 传递
            query = query.set_index(["account_number", "account_ordnum", "sz_adjustment_buy", "sz_adjustment_sell"])
            logger.info(f"Positions\n{query}")
            
            quotations = redis_client.load_dataframe("market")
            # quotations = self.client.get_history_candlesticks(instId=params.underlying, bar=params.time_bar, limit=params.window_limit, c1=params.c1, c2=params.c2, window=params.window, cx=params.cx, window_short=params.window_short, window_long=params.window_long)
            # logger.info(f"Pre Channel:{'%.2f' % quotations['upper'].values[-2]},{'%.2f' % quotations['boll'].values[-2]},{'%.2f' % quotations['lower'].values[-2]}")
            # logger.info(f"Cur Channel:{'%.2f' % quotations['upper'].values[-1]},{'%.2f' % quotations['boll'].values[-1]},{'%.2f' % quotations['lower'].values[-1]}")
            logger.info(f"Close:{quotations['close'][0]}")
            # logger.info(f"4std:{'%.2f' % (4*quotations['std'][0])}")
            # logger.info(f"rsi:{'%.2f' % quotations['rsi'][0]}")
            # logger.info(f"amplitude:{'%.4f' % quotations['amplitude'][0]}")
            logger.info(f"Parameters:{params.underlying, params.time_bar, params.window, params.window_short, params.window_long, params.c1, params.c2, params.cx, params.ca1, params.ca2, params.ca3, params.tpls, params.sz, params.smax, params.smin, params.spr, params.slr, params.spp, params.slp}")

            try:
                res = trade_mix_strategy_Boll_1X2(quotations=quotations, query=query, ca1=params.ca1, ca2=params.ca2, ca3=params.ca3, tpls=params.tpls, smax=params.smax, smin=params.smin, slr=params.slr, slp=params.slp, spp=params.spp, spr=params.spr)
            except Exception as error:
                logger.info(f"strategy error: {traceback.format_exc()}")
                res = None

            # if res:
            #     write_response_html(self.json_args, {"status": 0, "msg": "succees", "batch": batch, "accounts": res})

            return self.write({"status": 0, "msg": "succees", "batch": batch, "accounts": res})
        else:
            return self.write({"status": 0, "msg": "null accont request", "batch": batch, "accounts": None})


class MarketSignalHandler(BaseHandler):

    def get(self):
        try:
            quotations = redis_client.load_dataframe("market")
            cons_buy_com, cons_sel_com = get_market_signal(quotations=quotations)
            return self.write({"status": 0, "msg": "succees", "signal": {"long": bool(cons_buy_com), "short": bool(cons_sel_com)}})
        except Exception as error:
            logger.info(f"get market signal error: {traceback.format_exc()}")
            return self.write({"status": 1, "msg": "get market signal error, return default values", "signal": {"buy": bool(False), "sell": bool(False)}})