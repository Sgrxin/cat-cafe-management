# -*- coding: utf-8 -*-
"""预约取消完整闭环: 建预约 → 抓取消表单地址 → POST取消 → 验证chip"""
import re
import urllib.parse
import urllib.request
import http.cookiejar

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
BASE = "http://127.0.0.1:8000"


def get_csrf(url):
    r = opener.open(url, timeout=10)
    h = r.read().decode("utf-8", "replace")
    return re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', h).group(1)


def login(u, p):
    t = get_csrf(BASE + "/login/")
    d = urllib.parse.urlencode({"username": u, "password": p,
                                "csrfmiddlewaretoken": t}).encode()
    req = urllib.request.Request(BASE + "/login/", data=d,
                                 headers={"Referer": BASE + "/login/"})
    opener.open(req, timeout=10)


login("linxin", "123456")

# 1. 建10-25预约
t = get_csrf(BASE + "/reserve/")
d = urllib.parse.urlencode({"seat": "3", "date": "2026-10-25",
                            "start": "15:00", "end": "17:00",
                            "csrfmiddlewaretoken": t}).encode()
req = urllib.request.Request(BASE + "/reserve/", data=d,
                             headers={"Referer": BASE + "/reserve/"})
r = opener.open(req, timeout=10)
print("预约10-25:", "预约成功" in r.read().decode("utf-8", "replace"))

# 2. 渲染预约页, 抓取取消表单的真实action
r = opener.open(BASE + "/reserve/", timeout=10)
h = r.read().decode("utf-8", "replace")
actions = re.findall(r'action="(/reserve/\d+/cancel/)"', h)
print("取消表单:", actions)
if actions:
    t = get_csrf(BASE + "/reserve/")
    d = urllib.parse.urlencode({"csrfmiddlewaretoken": t}).encode()
    req = urllib.request.Request(BASE + actions[0], data=d,
                                 headers={"Referer": BASE + "/reserve/"})
    r = opener.open(req, timeout=10)
    print("取消POST:", "预约已取消" in r.read().decode("utf-8", "replace"))
    r = opener.open(BASE + "/reserve/", timeout=10)
    h = r.read().decode("utf-8", "replace")
    print("取消后页面含已取消chip:", "已取消" in h)
else:
    print("未找到取消表单")
