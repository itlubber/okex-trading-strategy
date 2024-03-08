import os
import sys


sys.path.append(os.path.dirname(__file__))


# logging
log_file = os.path.join(os.path.dirname(__file__), "logs/info.log")
log_format = "[ %(levelname)s ][ %(asctime)s ][ %(filename)s:%(funcName)s:%(lineno)d ] %(message)s"
log_date_format = '%Y-%m-%d %H:%M:%S'


# tornado
port = 80
settings = dict(
    # 调试模式
    debug=False,
    # 修改代码自动重载
    autoreload=False
)

max_workers = 8

# redis
redis_connect_options = {
    "host": "localhost",
    "port": 6379,
    "db": 1,
}

market_time_sleep = 2

market_time_sleep_r = 5* 60
r_work_dir='/root/finance_predict/R'

# emails
email_options = {
    "host": "smtp.qq.com",
    "port": 465,
    "email": "xxx@qq.com",
    "account": "xxx",
    "passphrase": "xxx",
    "receivers": [
        "xxx@qq.com",
    ]
}


# keras model config
threshold = 0.01
periods = 36  # 预测 T+n 的涨跌
classify_num = 3  # 标签的分类数
batch_size = 64
time_steps = 128  # lstm 和 attention 的时间长度
epochs = 50  # 训练次数
learn_rate = 0.0005  # 学习率
feature_dims = 32  # 输入特征维数
lstm_units = 64  # lstm cell 个数

parent_dir = os.path.dirname(__file__)
data_dir = os.path.join(parent_dir, 'data')
model_dir = os.path.join(parent_dir, 'model')
keras_checkpoint_file = os.path.join(model_dir, 'keras.checkpoints.')
tensorboard_dir = os.path.join(parent_dir, 'logs')
debug_file = os.path.join(data_dir, 'ETH-USDT-SWAP_5m_train_data.csv')


# create relate files

if not os.path.exists(os.path.dirname(log_file)):
    os.makedirs(os.path.dirname(log_file))
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
if not os.path.exists(model_dir):
    os.makedirs(model_dir)
if not os.path.exists(tensorboard_dir):
    os.makedirs(tensorboard_dir)
