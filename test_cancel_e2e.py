# -*- coding: utf-8 -*-
"""预约取消完整E2E: 渲染→POST取消→状态chip验证"""
import re
import urllib.parse
import urllib.request
import http.cookiejar

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def get_csrf(url):
    r = opener.open(url, timeout=10)
    html = r.read().decode("utf-8", "replace")
    return re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html).group(1)


def login(user, pwd):
    token = get_csrf("http://127.0.0.1:8000/login/")
    data = urllib.parse.urlencode({"username": user, "password": pwd,
                                   "csrfmiddlewaretoken": token}).encode()
    req = urllib.request.Request("http://127.0.0.1:8000/login/", data=data,
                                 headers={"Referer": "http://127.0.0.1:8000/login/"})
    opener.open(req, timeout=10)


login("linxin", "123456")
token = get_csrf("http://127.0.0.1:8000/reserve/")
data = urllib.parse.urlencode({"seat": "3", "date": "2026-10-25",
                               "start": "15:00", "end": "17:00",
                               "csrfmiddlewaretoken": token}).encode()
req = urllib.request.Request("http://127.0.0.1:8000/reserve/", data=data,
                             headers={"Referer": "http://127.0.0.1:8000/reserve/"})
r = opener.open(req, timeout=10)
print("预约10-25:", "预约成功" in r.read().decode("utf-8", "replace"))

token = get_csrf("http://127.0.0.1:8000/reserve/")
data = urllib.parse.urlencode({"rid": "5", "csrfmiddlewaretoken": token}).encode()
req = urllib.request.Request("http://127.0.0.1:8000/reserve/5/cancel/", data=data,
                             headers={"Referer": "http://127.0.0.1:8000/reserve/"})
r = opener.open(req, timeout=10)
body = r.read().decode("utf-8", "replace")
print("取消10-25:", "预约已取消" in body)

# 验证状态chip
r = opener.open("http://127.0.0.1:8000/reserve/", timeout=10)
body = r.read().decode("utf-8", "replace")
print("列表含已取消chip:", "chip-off" in body and "已取消" in body)
print("列表含已确认(剩余):", body.count("chip-ok"))
