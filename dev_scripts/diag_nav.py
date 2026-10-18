# -*- coding: utf-8 -*-
"""抓vote页HTML检查领奖台渲染"""
import re
import urllib.parse
import urllib.request
import http.cookiejar

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
r = op.open("http://127.0.0.1:8000/login/")
html = r.read().decode("utf-8", "replace")
t = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html).group(1)
body = urllib.parse.urlencode({"username": "admin", "password": "Admin@123",
                               "csrfmiddlewaretoken": t}).encode()
req = urllib.request.Request("http://127.0.0.1:8000/login/", data=body,
                             headers={"Referer": "http://127.0.0.1:8000/login/"})
op.open(req)
h = op.open("http://127.0.0.1:8000/vote/").read().decode("utf-8", "replace")
i = h.find("podium")
print(h[max(0, i - 80):i + 600])
