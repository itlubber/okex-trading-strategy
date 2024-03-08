underlying = "ETH-USDT-SWAP"
underlying_type = "SWAP"
ccy_type = "USDT"


posS = 0   #持仓数量（张）-APP端发送#
sz = 5   #每次开仓数量#
smax = 5  #最大多单数量#
smin = 5  #最大空单数量#
spr = 0.5   #【止盈比率】#
slr = 0.2   #【止损比率】#
spp = 306.0  #止盈绝对数值#
slp = 145.0  #止损绝对数值#
tpli = 0.0   #上一次开仓价格-APP端发送#
tpls = 100.0  #加仓价格增减绝对数值#
tdMode = "cross"
ordType = "market"
time_bar = "15m"    #K线的时间颗粒#
window_limit = 30


c1 = 2.0    #上轨（std的倍数）#
c2 = 2.0    #下轨（std的倍数）#
cx = 2.0    #备用轨（std的倍数）#
ca1 = 0.28    ## 4*std > ca1 ： 追涨杀跌#
ca2 = 40    ## ca2 > 4*std > ca3 :  低买高卖#
ca3 = 40    ## 4*std < ca3 :  不交易#
window = 20   #Boll线的窗口期#
window_short = 10    #短期均线的窗口期（判断短期趋势）#
window_long = 10    #长期均线的窗口期（判断短期趋势）#

upl = 0.0     #浮盈绝对数值-APP端发送#
uplRatio = 0.0    #浮盈比率-APP端发送#