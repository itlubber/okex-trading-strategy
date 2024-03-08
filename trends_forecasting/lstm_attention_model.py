import os
import config
from traceback import format_exc
import numpy as np
from utils.logger import logger
from keras.models import load_model
from api.okex_client import Client


class ForecastModel:
    client = None
    model = None

    def __init__(self, contract_code="ETH-USDT-SWAP", period="5m"):
        self.contract_code = contract_code
        self.period = period
        if self.client is None:
            self.client = Client()
        if self.model is None:
            logger.info(f"load keras model {config.keras_checkpoint_file}{self.contract_code}.{self.period}.tar ...")
            self.model = load_model(f"{config.keras_checkpoint_file}{self.contract_code}.{self.period}.tar")

    def predict(self):
        x = self.client.get_market_data(contract_code=self.contract_code, period=self.period)
        try:
            return self.model.predict(np.expand_dims(x, axis=0))
        except Exception as error:
            logger.error(f"predict {self.contract_code} {self.period} data error : {error}")
            raise Exception(f"{format_exc()}")


if __name__ == '__main__':
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
    lstm_attention_model = ForecastModel(contract_code="ETH-USDT-SWAP", period="5m")
    try:
        trend = lstm_attention_model.predict()
        # 预测涨跌震荡的概率
        logger.info(trend)
        # 输出最终预测标签
        logger.info(np.argmax(trend))
    except Exception as error:
        logger.error(f"{error}")
