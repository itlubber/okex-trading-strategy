import os
import config
from logging.handlers import TimedRotatingFileHandler
from logging import getLogger, StreamHandler, Formatter, INFO


def get_logger_lubber(log_file=config.log_file, log_format=config.log_format, date_format=config.log_date_format):
    _logger = getLogger("lubber")

    if not os.path.exists(os.path.dirname(log_file)):
        try:
            os.makedirs(os.path.dirname(log_file))
        except Exception as error:
            _logger.critical(f"错误 >> 创建日志目录失败,清手动创建目录文件位置,运行 sudo mkdir -p {os.path.dirname(config.log_file)}")
            _logger.critical("错误 >> 报错信息 : {}".format(error))

    _logger.setLevel(INFO)

    formatter = Formatter(log_format, datefmt=date_format)

    fh = TimedRotatingFileHandler(filename=log_file, when="D", interval=1, backupCount=30, encoding="utf-8")
    fh.setLevel(INFO)
    fh.setFormatter(formatter)
    _logger.addHandler(fh)

    # ch = StreamHandler()
    # ch.setLevel(INFO)
    # ch.setFormatter(formatter)
    # _logger.addHandler(ch)

    return _logger


logger = get_logger_lubber()