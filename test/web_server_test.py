import time
import requests


url = "http://localhost:8084/strategy_boll"
json_args = {
    "accounts": [
        {
            "account": {
                "accountbal": 2938.934589359535,
                "accountcurrency": "USDT",
                "accountnumber": 116,
                "accountordnum": 1
            },
            "agreement": [
                {
                    "adl": "",
                    "availPos": "",
                    "avgPx": "",
                    "cTime": "",
                    "ccy": "",
                    "deltaBS": "",
                    "deltaPA": "",
                    "gammaBS": "",
                    "gammaPA": "",
                    "imr": "",
                    "instId": "",
                    "instType": "",
                    "interest": "",
                    "last": "",
                    "lever": "",
                    "liab": "",
                    "liabCcy": "",
                    "liqPx": "",
                    "margin": "",
                    "mgnMode": "",
                    "mgnRatio": "",
                    "mmr": "",
                    "notionalUsd": "",
                    "optVal": "",
                    "pTime": "",
                    "pos": "",
                    "posCcy": "",
                    "posId": "",
                    "posSide": "",
                    "thetaBS": "",
                    "thetaPA": "",
                    "tradeId": "",
                    "uTime": "",
                    "upl": "",
                    "uplRatio": "",
                    "vegaBS": "",
                    "vegaPA": ""
                }
            ]
        },
        {
            "account": {
                "accountbal": 2938.934589359535,
                "accountcurrency": "USDT",
                "accountnumber": 1,
                "accountordnum": 3
            },
            "agreement": [
                {
                    "adl": "",
                    "availPos": "",
                    "avgPx": "",
                    "cTime": "",
                    "ccy": "",
                    "deltaBS": "",
                    "deltaPA": "",
                    "gammaBS": "",
                    "gammaPA": "",
                    "imr": "",
                    "instId": "",
                    "instType": "",
                    "interest": "",
                    "last": "",
                    "lever": "",
                    "liab": "",
                    "liabCcy": "",
                    "liqPx": "",
                    "margin": "",
                    "mgnMode": "",
                    "mgnRatio": "",
                    "mmr": "",
                    "notionalUsd": "",
                    "optVal": "",
                    "pTime": "",
                    "pos": "",
                    "posCcy": "",
                    "posId": "",
                    "posSide": "",
                    "thetaBS": "",
                    "thetaPA": "",
                    "tradeId": "",
                    "uTime": "",
                    "upl": "",
                    "uplRatio": "",
                    "vegaBS": "",
                    "vegaPA": ""
                }
            ]
        },
        {
            "account": {
                "accountbal": 2989.484909895857,
                "accountcurrency": "USDT",
                "accountnumber": 118,
                "accountordnum": 1
            },
            "agreement": [
                {
                    "adl": "",
                    "availPos": "",
                    "avgPx": "",
                    "cTime": "",
                    "ccy": "",
                    "deltaBS": "",
                    "deltaPA": "",
                    "gammaBS": "",
                    "gammaPA": "",
                    "imr": "",
                    "instId": "",
                    "instType": "",
                    "interest": "",
                    "last": "",
                    "lever": "",
                    "liab": "",
                    "liabCcy": "",
                    "liqPx": "",
                    "margin": "",
                    "mgnMode": "",
                    "mgnRatio": "",
                    "mmr": "",
                    "notionalUsd": "",
                    "optVal": "",
                    "pTime": "",
                    "pos": "1",
                    "posCcy": "",
                    "posId": "",
                    "posSide": "long",
                    "thetaBS": "",
                    "thetaPA": "",
                    "tradeId": "",
                    "uTime": "",
                    "upl": "",
                    "uplRatio": "",
                    "vegaBS": "",
                    "vegaPA": ""
                }
            ]
        }
    ],
    "batch": {
        "event": "QISMDL",
        "requestid": 0,
        "servicemode": "0"
    }
}


def run():
    res = requests.post(url=url, json=json_args).json()
    print(res)
    

if __name__ == '__main__':
    while True:
        try:
            run()
        except:
            pass
        time.sleep(10)
