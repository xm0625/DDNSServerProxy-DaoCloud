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


# Deprecated DaoCloud此API接口概率性重启失败
def restart_app(api_token, app_id):
    url = "https://openapi.daocloud.io/v1/apps/" + app_id + "/actions/restart"
    req = urllib2.Request(url=url, data=urllib.urlencode({}), headers={"Authorization": "token "+api_token})
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    print res


def stop_app(api_token, app_id):
    url = "https://openapi.daocloud.io/v1/apps/" + app_id + "/actions/stop"
    req = urllib2.Request(url=url, data=urllib.urlencode({}), headers={"Authorization": "token "+api_token})
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    print res


def start_app(api_token, app_id):
    url = "https://openapi.daocloud.io/v1/apps/" + app_id + "/actions/start"
    req = urllib2.Request(url=url, data=urllib.urlencode({}), headers={"Authorization": "token "+api_token})
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    print res


def get_action_detail(api_token, app_id, action_id):
    url = "https://openapi.daocloud.io/v1/apps/" + app_id + "/actions/" + action_id
    req = urllib2.Request(url=url, headers={"Authorization": "token "+api_token})
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    print res


def redeploy_app(api_token, app_id, release_name=None):
    if release_name is None:
        release_name = get_app_detail(api_token, app_id)["release_name"]
    print release_name
    url = "https://openapi.daocloud.io/v1/apps/" + app_id + "/actions/redeploy"
    req = urllib2.Request(url=url, data=json.dumps({"release_name": str(release_name)}), headers={"Authorization": "token "+api_token})
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    print res


def get_app_detail(api_token, app_id):
    url = "https://openapi.daocloud.io/v1/apps/" + app_id
    req = urllib2.Request(url=url, headers={"Authorization": "token " + api_token})
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    print res
    return json.loads(res)


if __name__ == '__main__':
    if "API_TOKEN" not in os.environ:
        exit(1)
    if "APP_ID" not in os.environ:
        exit(1)
    time.sleep(10 * 3600)
    redeploy_app(os.environ["API_TOKEN"], os.environ["APP_ID"])


