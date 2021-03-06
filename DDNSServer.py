# coding=utf-8

# 解决py2.7中文出现write错误的问题
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
# 解决py2.7中文出现write错误的问题 #

# server.py
# 从wsgiref模块导入:
from wsgiref.simple_server import make_server
from cgi import parse_qs, escape
import urllib
import urllib2
import json
import base64


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


# 调用3322 API接口
def perform_dns_update(hostname, user, password, ip):
    url = "http://members.3322.net/dyndns/update?system=dyndns&hostname=%s&myip=%s" % (hostname, ip)
    request = urllib2.Request(url)
    base64_string = base64.b64encode('%s:%s' % (user, password))
    request.add_header("Authorization", "Basic %s" % base64_string)
    try:
        res = urllib2.urlopen(request)
        res_data = res.read()
        return {"httpCode": 200, "response": res_data}
    except urllib2.HTTPError as e:
        return {"httpCode": e.code}
    except urllib2.URLError as e:
        return {"httpCode": "-1", "reason": e.reason}


# 路径为"/"的控制逻辑方法(MVC中的C)
def parse_and_fetch(request, remote_address):
    if "hostname" not in request.keys():
        raise CommonException("-1", "hostname not exist")
    if "user" not in request.keys():
        raise CommonException("-1", "user not exist")
    if "password" not in request.keys():
        raise CommonException("-1", "password not exist")
    return perform_dns_update(request["hostname"], request["user"], request["password"], remote_address)


# http server 主逻辑, 这里是一个简陋的路由
def app(environ, start_response):
    request_method = environ["REQUEST_METHOD"] #GET
    path_info = environ["PATH_INFO"]  # /hi/name/index.action
    query_string = environ["QUERY_STRING"] # ?后面的东西
    remote_address = environ["REMOTE_ADDR"] # 访问者ip
    if "HTTP_X_FORWARDED_FOR" in environ:
        ip_array = str(environ["HTTP_X_FORWARDED_FOR"]).split(",")
        if len(ip_array) > 0:
            remote_address = ip_array[0].strip()

    print "request_method:"+request_method
    print "path_info:"+path_info
    print "remote_address:"+remote_address

    if request_method == "GET" :
        request = parse_qs(query_string)
    else:
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0
        request_body = environ['wsgi.input'].read(request_body_size)
        request = parse_qs(request_body)
    for (d,x) in request.items():
        if isinstance(x, list) and len(x) == 1:
            request[d] = x[0]
    for (d,x) in request.items():
        print "key:"+d+",value:"+str(x)

    if path_info == "/" :
        response_string = ""
        response_code = "200 OK"
        response_header = [('Content-type', 'text/html')]
        try:

            fetch_result = parse_and_fetch(request, remote_address)
            response_data = {"code":"1","message":"success","result":fetch_result}
            response_string = json.dumps(response_data)
        except CommonException as ce:
            response_string ='{"code":"'+ce.code+'","message":"'+ce.message+'"}'
        except ValueError:
            response_string ='{"code":"0","message":"system busy"}'
    else:
        response_string = "404 NOT FOUND"
        response_code = "404 NOT FOUND"
        response_header = [('Content-type', 'text/html')]

    start_response(response_code,response_header)
    return [response_string]

# 创建一个服务器，IP地址为空，端口是8090，处理函数是app:
httpd = make_server('', 8090, app)
print "Serving HTTP on port 8090..."
# 开始监听HTTP请求:
httpd.serve_forever()
