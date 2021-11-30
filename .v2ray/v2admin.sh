#!/usr/bin/zsh

cd ~/.v2ray

if [ $1 = "start" ]; then
	nohup v2ray > /dev/null 2>&1 & echo $! > id
elif [ $1 = "restart" ]; then
	kill -9 `cat id`
	nohup v2ray > /dev/null 2>&1 & echo $! > id
elif [ $1 = "stop" ]; then
	kill -9 `cat id`
fi

cd -
