import os
import numpy as np
from sklearn.metrics import classification_report
from tensorflow.keras import optimizers
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import TensorBoard, EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, TerminateOnNaN
from tensorflow.keras.layers import Input, Dense, LSTM, Dropout, Conv1D, MaxPooling1D, Bidirectional, Multiply
import config
from utils.logger import logger
from utils.data_preprocess import get_model_train_data


def create_model():
    """
    创建keras模型
    """
    inputs = Input(shape=(config.time_steps, config.feature_dims))
    _ = Dropout(0.3)(inputs)  # 训练时随机选择部分特征作为输入
    _ = Conv1D(filters=64, kernel_size=1, activation='relu', padding="same")(_)
    _ = MaxPooling1D(pool_size=5)(_)  # 通过卷积&池化提取高维特征
    _ = Dropout(0.3)(_)
    lstm_out = Bidirectional(LSTM(config.lstm_units, activation='relu'))(_)
    attention_out = Dense(128, activation='sigmoid')(lstm_out)  # 加入attention机制
    attention_mul = Multiply()([lstm_out, attention_out])
    output = Dense(config.classify_num, activation='sigmoid')(attention_mul)  # 预测涨跌标签
    _model = Model(inputs=inputs, outputs=output)
    _model.summary()

    return _model


def train(contract_code="ETH-USDT-SWAP", period="1m", val=False):
    """
    训练模型
    :param val: 是否验证集
    :param contract_code: 品种名称
    :param period: k线类型
    :param debug: 是否为调试模式, 调试模式只读取本地数据
    """
    if val:
        x_train, x_val, x_test, y_train, y_val, y_test = get_model_train_data(val=True)
    else:
        x_train, x_test, y_train, y_test = get_model_train_data()
    logger.info(f"x_train : {x_train.shape}, y_train : {y_train.shape}, x_test : {x_test.shape}, y_test : {y_test.shape}")

    _model = create_model()
    keras_callback = [
                        EarlyStopping(monitor='val_loss', patience=10, verbose=1)
                        # , TensorBoard(log_dir=config.tensorboard_dir, histogram_freq=0, write_grads=True)
                        , ReduceLROnPlateau(factor=0.1, monitor="val_loss", patience=5)
                        , ModelCheckpoint(f"{config.keras_checkpoint_file}{contract_code}.{period}.tar", monitor='val_loss', verbose=1, save_best_only=True, save_weights_only=False, period=1)
                        , TerminateOnNaN()
                      ]

    _model.compile(loss='categorical_crossentropy', optimizer=optimizers.Adam(lr=config.learn_rate, clipnorm=1), metrics=["categorical_accuracy"])

    if val:
        _model.fit(x_train, y_train, epochs=config.epochs, batch_size=config.batch_size, shuffle=True, validation_data=(x_val, y_val), callbacks=keras_callback)
    else:
        _model.fit(x_train, y_train, epochs=config.epochs, batch_size=config.batch_size, shuffle=True, validation_data=(x_test, y_test), callbacks=keras_callback)

    logger.info("\nTrain Data Set Classification Report")
    logger.info(classification_report(np.argmax(y_train, 1), np.argmax(_model.predict(x_train), 1)))
    logger.info("\nTest Data Set Classification Report")
    logger.info(classification_report(np.argmax(y_test, 1), np.argmax(_model.predict(x_test), 1)))


if __name__ == '__main__':
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    train(contract_code="ETH-USDT-SWAP", period="5m", val=True)
