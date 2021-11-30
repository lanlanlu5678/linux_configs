#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
V2Ray automatic configuration
@date    : 2021/11/28
@author  : jcz
@comment :
    1. automatic test & choose the fastest server to the target url
    2. target url can be specified, default 'www.google.com.hk'
    3. all active server (timeout 500ms) will be saved, for altering manully
'''

import os
import re
import json
import time
import base64
import requests
import argparse

subscription = 'https://www.thismiao.xyz/link/5gRDIUdouAXvA59E?sub=3&extend=1'

config_template = '\
{\
    "log": {\
        "access": "/home/lanlanlu/.v2ray/access.log",\
        "error": "/home/lanlanlu/.v2ray/error.log",\
        "loglevel": "info"\
    },\
    "inbounds": [\
        {\
            "tag": "http",\
            "port": 10909,\
            "listen": "127.0.0.1",\
            "protocol": "http",\
            "sniffing": {\
                "enabled": true,\
                "destOverride": [\
                    "http",\
                    "tls"\
                ]\
            },\
            "settings": {\
                "udp": false,\
                "allowTransparent": false\
            }\
        },\
        {\
            "tag": "socks",\
            "port": 10808,\
            "listen": "127.0.0.1",\
            "protocol": "socks",\
            "sniffing": {\
                "enabled": true,\
                "destOverride": [\
                    "http",\
                    "tls"\
                ]\
            },\
            "settings": {\
                "auth": "noauth",\
                "udp": true\
            }\
        }\
    ],\
    "outbounds": [\
        {\
            "tag": "proxy",\
            "protocol": "vmess",\
            "settings": {\
                "vnext": [\
                    {\
                        "address": "$add",\
                        "port": "$port",\
                        "users": [\
                            {\
                                "id": "$id",\
                                "alterId": 0,\
                                "security": "auto"\
                            }\
                        ]\
                    }\
                ]\
            },\
            "streamSettings": {\
                "network" : "$net"\
            },\
            "mux": {\
                "enabled": false,\
                "concurrency": -1\
            }\
        }\
    ]\
}'

proxies = {
    'http': 'http://127.0.0.1:10909',
    'https': 'http://127.0.0.1:10909'
}

config_path = './config.json'
vsds_path = './vsds.json'


def genConfig(vsd):
    config = json.loads(config_template)
    if len(re.findall('\d+\.\d+\.\d+\.\d+', vsd['add'])) == 0:
        return False
    config['outbounds'][0]['settings']['vnext'][0]['address'] = vsd['add']
    config['outbounds'][0]['settings']['vnext'][0]['port'] = int(vsd['port'])
    config['outbounds'][0]['settings']['vnext'][0]['users'][0]['id'] = vsd['id']
    config['outbounds'][0]['settings']['vnext'][0]['users'][0]['alterId'] = int(vsd['aid'])
    config['outbounds'][0]['streamSettings']['network'] = vsd['net']
    if vsd['net'] == 'ws':
        config['outbounds'][0]['streamSettings']['wsSettings'] = {}
        config['outbounds'][0]['streamSettings']['wsSettings']['path'] = vsd['path']
        config['outbounds'][0]['streamSettings']['wsSettings']['headers'] = {}
        config['outbounds'][0]['streamSettings']['wsSettings']['headers']['Host'] = vsd['host']
    
    with open(config_path, 'w') as f:
        # print(config)
        json.dump(config, f, indent='\t')
    
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', type=str, default='http://www.google.com.hk')
    parser.add_argument('-s', '--server', type=int, default=-1)
    args = parser.parse_args()

    if args.server > 0:
        if not os.path.exists(vsds_path):
            print("Error: no server configs available, exiting ...")
            exit()

        with open(vsds_path, 'r') as f:
            vsd = json.load(f)[args.server]
        
        # assume active server with valid vmess configs
        genConfig(vsd)
    else:
        res = requests.get(subscription).content
        rawlinks = base64.b64decode(res).decode('utf-8').split('\n')
        vmlinks = [link for link in rawlinks if len(link) > 3]

        vsds = []
        ids = 0
        scores = []
        for vlink in vmlinks:
            print('\rtesting server {0} with url {1}'.format(ids, args.url), end='')
            vsd = json.loads(base64.b64decode(vlink[8:]).decode('utf-8'))
            if genConfig(vsd):
                vsds.append(vsd)
                os.system('~/.v2ray/v2admin.sh restart')
                time.sleep(0.5)
                timer = time.clock_gettime(0)
                try:
                    requests.get(args.url, proxies=proxies, timeout=1)
                except requests.exceptions.ReadTimeout:
                    pass
                scores.append([ids, (time.clock_gettime(0) - timer) * 1000])
                ids += 1
        print('testing complete')

        scores = sorted(scores, key=lambda x: x[1])
        for i in scores:
            print('{0:2}: server {1:30} with delay {2}'.format(i[0], vsds[i[0]]['ps'].strip(), 'timeout' if i[1] > 1000 else '{0:.2f}ms'.format(i[1])))

        genConfig(vsds[scores[0][0]])
        with open(vsds_path, 'w') as f:
            json.dump(vsds, f, indent='\t')

    os.system('~/.v2ray/v2admin.sh restart')
