import sys
sys.path.append("..")
from api.redis_client import redis_client


if __name__ == '__main__':
    garch = redis_client.redis_conn.get("garch_rscript_trend")
    print(float(garch))
    
    # lstm = redis_client.redis_conn.get("ETH-USDT-SWAP_5m_trend") or b"-1"
    # print(lstm, lstm == b"2")
    # print(type(lstm))
    # print(int(lstm))
