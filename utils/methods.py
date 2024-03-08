import time
import datetime
from utils.logger import logger


def timestamp2datetime(stamp,format='%Y-%m-%d %H:%M:%S'):
    if not isinstance(stamp, int):
        try:
            stamp = int(stamp)
        except ValueError as error:
            raise Exception(f"timestamp is not digital. error info {error}")

    if len(str(stamp)) == 10:
        _ = time.localtime(stamp)
        _ = time.strftime(format, _)
        return datetime.datetime.strptime(_, format)
    elif 10 < len(str(stamp)) < 15:
        _ = len(str(stamp)) - 10
        _ = datetime.datetime.fromtimestamp(stamp/(1 * 10 ** _))
        return _.strftime(format)
    else:
        return


def get_timestamp(date=None, query="s", time_format="%Y-%m-%d %H:%M:%S"):
    if query == "ms":
        return int(round(time.mktime(time.strptime(date, time_format))) * 1000)
    else:
        return int(time.mktime(time.strptime(date, time_format)))


def get_timestamp_millisecond(query=None):
    _ = time.time()
    if query:
        return int(_)
    else:
        return int(round(_ * 1000))


def get_period_gap(period="1m"):
    if "m" in period:
        return int(period.split("m")[0]) * 60 * 1000
    elif "H" in period:
        return int(period.split("H")[0]) * 60 * 60 * 1000
    elif "D" in period:
        return int(period.split("D")[0]) * 24 * 60 * 60 * 1000
    elif "W" in period:
        return int(period.split("W")[0]) * 7 * 24 * 60 * 60 * 1000
    elif "M" in period:
        return int(period.split("W")[0]) * 30 * 24 * 60 * 60 * 1000
    elif "Y" in period:
        return int(period.split("W")[0]) * 365 * 24 * 60 * 60 * 1000
    else:
        return 1000


def timer(func):
    def func_wrapper(*args, **kwargs):
        time_start = time.time()
        result = func(*args, **kwargs)
        time_end = time.time()
        time_spend = time_end - time_start
        logger.info('function {0}() cost time {1} s'.format(func.__name__, time_spend))
        return result

    return func_wrapper