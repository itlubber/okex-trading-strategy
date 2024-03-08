#!/bin/bash

start_server(){
    echo "nohup python3 server.py &" | /bin/bash
    if [ $? -ne 0 ];then
        echo "交易策略web服务启动失败, 请重新运行当前脚本或手动开启web服务"
    else
        echo "交易策略web服务后台启动成功, 以下查看实时输出, 使用 CTRL + C 可以退出实时状态监控, 且不影响web服务运行状态"
        echo "退出监控状态后, 可通过 tail -f logs/info.log 或 tail -f nohup.out 查看服务实时运行情况"
        tail -f nohup.out
    fi
}


kill -9 $(lsof -i:80 -t)
if [ $? -ne 0 ];then
    echo "策略服务未启动, 开始启动策略服务 ..."
    start_server
else
    echo "策略服务已启动, 正在重新启动策略服务 ..."
    start_server
fi
