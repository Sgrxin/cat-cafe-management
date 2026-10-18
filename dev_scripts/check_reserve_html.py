# -*- coding: utf-8 -*-
"""检查reserve页面渲染的HTML中取消表单"""
import urllib.request

# 先登录拿cookie
import http.cookiejar
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

data = urllib.parse.urlencode({"username": "linxin", "password": "123456"}).encode()
# 获取登录页拿csrf
r = opener.open("http://127.0.0.1:8000/login/", timeout=10)
html = r.read().decode("utf-8", "replace")
import re
m = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)
token = m.group(1)
data = urllib.parse.urlencode({"username": "linxin", "password": "123456", "csrfmiddlewaretoken": token}).encode()
req = urllib.request.Request("http://127.0.0.1:8000/login/", data=data, headers={"Referer": "http://127.0.0.1:8000/login/"})
r = opener.open(req, timeout=10)
print("登录后URL:", r.geturl())

r = opener.open("http://127.0.0.1:8000/reserve/", timeout=10)
html = r.read().decode("utf-8", "replace")
print("含reserve_cancel:", "reserve_cancel" in html)
i = html.find("我的预约")
print(html[i:i+600] if i >= 0 else "未找到我的预约")
