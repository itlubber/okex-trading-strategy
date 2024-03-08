import os
import time
import config
import warnings
import requests.exceptions
from utils.logger import logger
import rpy2.robjects as robjects
from traceback import format_exc
from api.redis_client import RedisClient


warnings.filterwarnings("ignore")


class RTaskClient(RedisClient):

    def __init__(self):
        super().__init__()
        self.key = "garch_rscript_trend"
        self.expire_time = config.market_time_sleep_r
        self.data_file_name = os.path.join(config.data_dir, "data.csv")

    def run(self):
        while True:
            try:
                quotations = self.client.get_history_candlesticks_for_R()
                quotations.to_csv(self.data_file_name, index=False)

                r_script = f'''
library(xts)
library(rugarch)
library(PerformanceAnalytics)
Raw.Data <- read.csv("{self.data_file_name}")
row.names(Raw.Data) <- as.POSIXct(strptime(Raw.Data[,1], "%Y-%m-%dT%H:%M:%S"))
Data <- Raw.Data[,c(5, 6)]
colnames(Data) <- c("Price", "Volume")
Raw.Return <- diff(log(Data[,1])) * 100
Return <- cbind(Data[-1,], Raw.Return)
Return1 <- Return[,c(-1, -2)]
Return1 <- xts(x = Return1, order.by = as.POSIXct(strptime(Raw.Data[,1], "%Y-%m-%dT%H:%M:%S")[-1]))
garch_spec <- ugarchspec(mean.model = list(armaOrder = c(1, 1), include.mean =TRUE),
                         variance.model = list(model = "sGARCH", garchOrder = c(1, 1)))
GARCH.Fit <- ugarchfit(spec = garch_spec, data = Return[,3])
Out.of.Sample <- round(dim(Return)[1] / 2)
Return.Out.of.Sample <- tail(Return, Out.of.Sample)
garch_spec <- ugarchspec(mean.model = list(armaOrder = c(1, 1), include.mean =TRUE),
                         variance.model = list(model = "sGARCH", garchOrder = c(1, 1)))
GARCH.Fit.Forecasting <- ugarchfit(spec = garch_spec, data = Return1)
GARCH.Forecast <- ugarchforecast(GARCH.Fit.Forecasting, n.ahead = 1)
Forecast.Return <- GARCH.Forecast@forecast$seriesFor[1,]
Forecast.Volatility <- GARCH.Forecast@forecast$sigmaFor[1,]
                '''

                robjects.r(r_script)
                volatility =  robjects.r("Forecast.Volatility")
                if volatility:
                    self.redis_conn.set(self.key, volatility[0])
                    self.redis_conn.expire(self.key, self.expire_time)

            except requests.exceptions.ConnectionError as error:
                logger.error(f"请求行情数据失败, 错误信息 {format_exc()}")

            time.sleep(config.market_time_sleep)


r_task_client = RTaskClient()