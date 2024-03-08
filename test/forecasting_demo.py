import os
import numpy as np
import sys
sys.path.append("..")
from utils.logger import logger
from trends_forecasting.lstm_attention_model import ForecastModel


# 去除tensorflow的警告信息，可以不加
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# 初始化模型，加载model下面训练好的model
lstm_attention_model = ForecastModel(contract_code="ETH-USDT-SWAP", period="5m")
trend = lstm_attention_model.predict()
# 预测涨跌震荡的概率
print(trend)
# 输出最终预测标签
print(np.argmax(trend))
