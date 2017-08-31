# coding=utf-8

# 解决py2.7中文出现write错误的问题
import sys

import signal
import subprocess
import threading
import time
import os

reload(sys)
sys.setdefaultencoding('utf-8')
# 解决py2.7中文出现write错误的问题 #

import urllib,urllib2
import json


def restart_app(api_token, app_id):
    url = "https://openapi.daocloud.io/v1/apps/" + app_id + "/actions/restart"
    req = urllib2.Request(url=url, data={}, headers={"Authorization": "token "+api_token})
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    print res

if __name__ == '__main__':
    exit(1)
    if "API_TOKEN" not in os.environ:
        exit(1)
    if "APP_ID" not in os.environ:
        exit(1)
    time.sleep(10 * 3600)
    restart_app(os.environ["API_TOKEN"], os.environ["APP_ID"])

