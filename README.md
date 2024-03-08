# 量化策略

## 说明
> 除策略外(handlers/)的所有代码修改在本项目中
>> 2021-10-11 15:30:00
>>> 添加趋势预测部分代码
>>> + 修改 api/okex_client.py、api/redis_client.py
>>> + 添加 trends_forecasting 趋势预测模块代码
>>> + 增加 test/trade_base_webapii.py 根据web服务模拟交易脚本

## 项目结构

```
.
├── README.md                                       # 项目说明文件
├── setup.py                                        # 加密脚本, 打包项目为.so文件, 反编译和加速
├── server.py                                       # 服务启动文件, python server.py 启动web服务
├── train.py                                        # 模型训练文件, python train.py 训练模型   
├── config.py                                       # 项目配置文件, 服务、模型、日志等相关配置
├── clear_cache.sh                                  # 清除缓存文件脚本
├── data                                            # 项目数据文件
├── build                                           # 项目打包文件
├── lib                                             # 项目依赖文件
├── logs                                            # 项目日志文件
├── requirements.txt                                # 项目相关依赖文件, pip install -r requirements.txt 进行安装
├── api                                             # 请求 okex api 接口封装
│   ├── okex                                        # okex 公共方法
│   │   ├── consts.py                               # 常量配置
│   │   ├── exceptions.py                           # okex 异常类实现
│   │   └── utils.py                                # 请求公共方法
│   ├── okex_client.py                              # 封装请求 okex 接口的方法
│   └── redis_client.py                             # redis 缓存相关方法封装
├── handlers                                        # 接口方法具体实现位置
│   ├── BaseHandler.py                              # 基于 tornado.web.RequestHandler 的封装, 所有接口继承至该类
│   ├── StrategyBoll                                # 策略接口实现, 每种策略独立
│   │   ├── StrategyBollHandler.py                  # 策略具体实现
│   │   └── boll_params.py                          # 策略参数配置
├── model                                           # 训练好的模型
│   ├── keras.checkpoints.ETH-USDT-SWAP.1m.tar
│   └── keras.checkpoints.ETH-USDT-SWAP.5m.tar
├── test                                            # 测试样例
│   ├── forecasting_demo.py
│   ├── trade_base_webapii.py                       # 单账号交易测试脚本文件
│   └── web_server_test.py
├── trends_forecasting                              # 预测方法实现
│   └── lstm_attention_model.py                     # lstm 方法封装
└── utils                                           # 公共方法封装
    ├── data_preprocess.py                          # 数据预处理方法
    ├── emails.py                                   # 邮件服务方法
    ├── logger.py                                   # 日志记录
    ├── methods.py                                  # 公用方法
    └── urls.py                                     # tornado 路由配置
```