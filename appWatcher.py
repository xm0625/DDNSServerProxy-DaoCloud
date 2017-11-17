# coding=utf-8

# 解决py2.7中文出现write错误的问题
import sys

import signal
import subprocess
import threading
import time
import os
import traceback

from datetime import timedelta, tzinfo

reload(sys)
sys.setdefaultencoding('utf-8')
# 解决py2.7中文出现write错误的问题 #

import urllib, urllib2
import json
from dateutil.parser import parse

# 通用异常处理
class CommonException(Exception):
    code = "0"
    message = "system busy"
    """docstring for CommonException"""
    def __init__(self, code, message="system busy"):
        super(CommonException, self).__init__()
        if code:
            self.code = code
        if message:
            self.message = message


# Deprecated DaoCloud此API接口概率性重启失败
def restart_app(**kwargs):
    api_token = kwargs["api_token"]
    app_id = kwargs["app_id"]

    url = "https://openapi.daocloud.io/v1/apps/" + app_id + "/actions/restart"
    req = urllib2.Request(url=url, data=urllib.urlencode({}), headers={"Authorization": "token "+api_token})
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return json.loads(res)


def stop_app(**kwargs):
    api_token = kwargs["api_token"]
    app_id = kwargs["app_id"]

    url = "https://openapi.daocloud.io/v1/apps/" + app_id + "/actions/stop"
    req = urllib2.Request(url=url, data=urllib.urlencode({}), headers={"Authorization": "token "+api_token})
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return json.loads(res)


def start_app(**kwargs):
    api_token = kwargs["api_token"]
    app_id = kwargs["app_id"]

    url = "https://openapi.daocloud.io/v1/apps/" + app_id + "/actions/start"
    req = urllib2.Request(url=url, data=urllib.urlencode({}), headers={"Authorization": "token "+api_token})
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return json.loads(res)


def get_action_detail(**kwargs):
    api_token = kwargs["api_token"]
    app_id = kwargs["app_id"]
    action_id = kwargs["action_id"]

    url = "https://openapi.daocloud.io/v1/apps/" + app_id + "/actions/" + action_id
    req = urllib2.Request(url=url, headers={"Authorization": "token "+api_token})
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return json.loads(res)


def redeploy_app(**kwargs):
    api_token = kwargs["api_token"]
    app_id = kwargs["app_id"]

    if "release_name" not in kwargs:
        release_name = promise_success(get_app_detail, 5, **{"api_token": api_token, "app_id": app_id})["release_name"]
    else:
        release_name = kwargs["release_name"]
    print release_name
    url = "https://openapi.daocloud.io/v1/apps/" + app_id + "/actions/redeploy"
    req = urllib2.Request(url=url, data=json.dumps({"release_name": str(release_name)}), headers={"Authorization": "token "+api_token})
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    print res


# 累计一小时不能超过5000次
# state not_running(应用异常) restaging(重新部署中) starting(启动中) running(运行中) stopping(停止中) stopped(已停止)
def get_app_detail(**kwargs):
    api_token = kwargs["api_token"]
    app_id = kwargs["app_id"]

    url = "https://openapi.daocloud.io/v1/apps/" + app_id
    req = urllib2.Request(url=url, headers={"Authorization": "token " + api_token})
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    # print res
    # print res_data.headers
    return json.loads(res)


def promise_success(func, retry_count, **kwargs):
    while True:
        try:
            return func(**kwargs)
        except Exception, e:
            retry_count -= 1
            if retry_count < 0:
                traceback.print_exc()
                raise CommonException("-2", e.message)
            time.sleep(1)


def confirm_state(api_token, app_id, state, retry_count):
    while True:
        print "confirm_state while"
        if retry_count < 0:
            return False
        retry_count -= 1
        time.sleep(1)

        app_detail = promise_success(get_app_detail, 5, **{"api_token": api_token, "app_id": app_id})
        if app_detail["state"] == state:
            return True


def redeploy_app_promise_success(api_token, app_id, http_token, retry_count):
    while True:
        print "redeploy_app_promise_success while"
        if retry_count < 0:
            return False
        retry_count -= 1
        time.sleep(1)

        app_detail = promise_success(get_app_detail, 5, **{"api_token": api_token, "app_id": app_id})
        if app_detail["state"] != "stopped" and app_detail["state"] != "not_running":
            promise_success(cancel_action, 5, **{"http_token": http_token, "app_id": app_id})
            confirm_state(api_token, app_id, "stopped", 300)
        promise_success(redeploy_app, 5, **{"api_token": api_token, "app_id": app_id})
        if confirm_state(api_token, app_id, "running", 300):
            return True


def get_action_list(**kwargs):
    http_token = kwargs["http_token"]
    app_id = kwargs["app_id"]

    url = "https://api.daocloud.io/v1/apps/" + app_id + "/actions?limit=10"
    print url
    print http_token
    req = urllib2.Request(url=url, headers={"Authorization": http_token})
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return json.loads(res)


def cancel_action(**kwargs):
    http_token = kwargs["http_token"]
    app_id = kwargs["app_id"]

    if "action_id" not in kwargs:
        action_list = promise_success(get_action_list, 5, **{"http_token": http_token, "app_id": app_id})["actions"]
        if len(action_list) == 0:
            return
        action_id = action_list[0]["action_id"]
    else:
        action_id = kwargs["action_id"]
    print action_id
    url = "https://api.daocloud.io/v1/apps/" + app_id + "/actions/" + action_id + "/cancel"
    req = urllib2.Request(url=url, data=urllib.urlencode({}), headers={"Authorization": http_token})
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return json.loads(res)


ZERO_TIME_DELTA = timedelta(0)
LOCAL_TIME_DELTA = timedelta(hours=8)  # 本地时区偏差


class UTC(tzinfo):
    """实现了格林威治的tzinfo类"""

    def utcoffset(self, dt):
        return ZERO_TIME_DELTA

    def dst(self, dt):
        return ZERO_TIME_DELTA


class LocalTimezone(tzinfo):
    """实现北京时间的类"""

    def utcoffset(self, dt):
        return LOCAL_TIME_DELTA

    def dst(self, dt):
        return ZERO_TIME_DELTA

    def tzname(self, dt):  # tzname需要返回时区名
        return '+08:00'


if __name__ == '__main__':
    # Seconds
    start_time = time.time()
    if "API_TOKEN" not in os.environ:
        exit(1)
    if "WATCH_APP_ID" not in os.environ:
        exit(1)
    if "HTTP_TOKEN" not in os.environ:
        exit(1)
    api_token_input = os.environ["API_TOKEN"]
    watch_app_id_input = os.environ["WATCH_APP_ID"]
    http_token_input = os.environ["HTTP_TOKEN"]

    while True:
        time.sleep(1)
        if time.time()-start_time < 4 * 3600:
            continue
        action_list = promise_success(get_action_list, 5, **{"http_token": http_token_input, "app_id": watch_app_id_input})
        if len(action_list) > 0:
            last_operation_time = time.mktime(parse(action_list[0]["start_date"]).replace(tzinfo=UTC()).astimezone(LocalTimezone()).timetuple())
            if time.time() - last_operation_time < 6*3600:
                continue
        redeploy_app_promise_success(api_token_input, watch_app_id_input, http_token_input, 5)