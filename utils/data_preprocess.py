import pandas as pd
import talib
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import config


def get_y_labels(x):
    if x > config.threshold:
        return 0, 0, 1
    elif x < -config.threshold:
        return 1, 0, 0
    elif abs(x) <= config.threshold:
        return 0, 1, 0
    else:
        return np.nan, np.nan, np.nan


def get_all_target(_):
    df = _.copy()
    # 调用ta-lib计算MACD指标
    df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(df.close.values, fastperiod=12, slowperiod=26, signalperiod=9)
    # 调用ta-lib计算rsi与动量
    df['rsi'] = talib.RSI(df.close.values, timeperiod=12)  # RSI的天数一般是6、12、24
    df['mom'] = talib.MOM(df.close.values, timeperiod=5)
    # 布林带
    df['upperband'], df['middleband'], df['lowerband'] = talib.BBANDS(df.close.values, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
    # 希尔伯特变换
    df['line1'] = talib.HT_TRENDLINE(df.close.values)
    # KAMA考夫曼的自适应移动平均线
    df['kama'] = talib.KAMA(df.close.values, timeperiod=30)
    # SAR抛物线指标
    df['sar'] = talib.SAR(df.high.values, df.low.values, acceleration=0, maximum=0)
    # CCI指标
    df['cci'] = talib.CCI(df.high.values, df.low.values, df.close.values, timeperiod=14)
    # KDJ中的KD指标
    df['slowk'], df['slowd'] = talib.STOCH(df.high.values, df.low.values, df.close.values, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
    # ULTOSC终极波动指标
    # 一种多方位功能的指标，除了趋势确认及超买超卖方面的作用之外，它的“突破”讯号不仅可以提供最适当的交易时机之外，更可以进一步加强指标的可靠度。
    df['ultosc'] = talib.ULTOSC(df.high.values, df.low.values, df.close.values, timeperiod1=7, timeperiod2=14, timeperiod3=28)
    # WILLR威廉指标
    # 市场处于超买还是超卖状态。股票投资分析方法主要有如下三种：基本分析、技术分析、演化分析。在实际应用中，它们既相互联系，又有重要区别。
    df['wtllr'] = talib.WILLR(df.high.values, df.low.values, df.close.values, timeperiod=14)
    # AD累积/派发线
    # 平衡交易量指标，以当日的收盘价位来估算成交流量，用于估定一段时间内该证券累积的资金流量。
    df['ad'] = talib.AD(df.high.values, df.low.values, df.close.values, df.vol.values)
    # ADOSC震荡指标
    df['adosc'] = talib.ADOSC(df.high.values, df.low.values, df.close.values, df.vol.values, fastperiod=3, slowperiod=10)
    # OBV能量潮
    # 通过统计成交量变动的趋势推测股价趋势
    df['obv'] = talib.OBV(df.close.values, df.vol.values)
    # ATR真实波动幅度均值
    # 以 N 天的指数移动平均数平均後的交易波动幅度。
    df['atr'] = talib.ATR(df.high.values, df.low.values, df.close.values, timeperiod=14)
    # HT_DCPERIOD希尔伯特变换-主导周期
    # 将价格作为信息信号，计算价格处在的周期的位置，作为择时的依据。
    df['line2'] = talib.HT_DCPERIOD(df.close.values)
    # HT_DCPHASE希尔伯特变换-主导循环阶段
    df['line3'] = talib.HT_DCPHASE(df.close.values)
    # HT_PHASOR希尔伯特变换-希尔伯特变换相量分量
    df['inphase'], df['quadrature'] = talib.HT_PHASOR(df.close.values)
    # HT_ SINE希尔伯特变换-正弦波
    df['sine'], df['leadsine'] = talib.HT_SINE(df.close.values)

    return df


def get_split_data(df, target, time_steps=config.time_steps, periods=config.periods, val=False):
    x, y = [], []
    scaler = StandardScaler()
    end = len(df)-periods
    while end > time_steps:
        x.append(scaler.fit_transform(df[end-time_steps:end]))
        y.append(target[end-1])

        end -= 1

    x = np.array(x)
    y = np.array(y)

    p = np.where(y[:, 1] == 1)[0]
    z = np.where(y[:, 2] == 1)[0]
    d = np.where(y[:, 0] == 1)[0]

    index = np.concatenate((np.random.choice(p, max(len(z), len(d))), d, z))
    x_train, x_test, y_train, y_test = train_test_split(x[index], y[index], test_size=0.3, shuffle=True, stratify=y[index])

    if val:
        x_val, x_test, y_val, y_test = train_test_split(x_test, y_test, test_size=0.6, shuffle=True)
        return x_train, x_val, x_test, y_train, y_val, y_test

    return x_train, x_test, y_train, y_test


def get_model_train_data(val=False):
    """
    获取训练和测试数据
    x_train : (samples_number, lstm_time_steps, features_dimension)
    y_train : (samples_number, classify_number)
    x_test  : (samples_number, lstm_time_steps, features_dimension)
    y_test  : (samples_number, classify_number)
    """
    data = pd.read_csv(config.debug_file)
    # 特征提取
    data = get_all_target(data).dropna()
    # 标签生成
    d, p, z = zip(*((data.shift(-config.periods).close - data.close) / data.close).apply(get_y_labels))
    target = np.array([d, p, z]).T
    # 训练集&测试集数据拆分
    if val:
        return get_split_data(data.values, target, val=True)
    else:
        return get_split_data(data.values, target)


if __name__ == '__main__':
    data = pd.read_csv("../data/ETH-USDT-SWAP_1m_train_data.csv")
    data = get_all_target(data).dropna()
    d, p, z = zip(*((data.shift(-config.periods).close - data.close) / data.close).apply(get_y_labels))
    target = np.array([d, p, z]).T
    x_train, x_test, y_train, y_test = get_split_data(data.values, target)