from tornado.web import url
from handlers.StrategyBoll.StrategyBollHandler import StrategyBollHandler


urls = [
    url(r"/strategy_boll", StrategyBollHandler, name="forecast_model")
]