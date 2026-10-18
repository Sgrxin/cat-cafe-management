# -*- coding: utf-8 -*-
import re
import urllib.error
import urllib.parse
import urllib.request
import http.cookiejar

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

r = opener.open("http://127.0.0.1:8000/login/", timeout=10)
h = r.read().decode("utf-8", "replace")
t = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', h).group(1)
d = urllib.parse.urlencode({"username": "linxin", "password": "123456",
                            "csrfmiddlewaretoken": t}).encode()
req = urllib.request.Request("http://127.0.0.1:8000/login/", data=d,
                             headers={"Referer": "http://127.0.0.1:8000/login/"})
opener.open(req, timeout=10)

try:
    r = opener.open("http://127.0.0.1:8000/vote/", timeout=10)
    h = r.read().decode("utf-8", "replace")
    print("status:", r.status)
    print("含奖牌🥇:", "🥇" in h)
    print("含已投:", "已投" in h)
    print("含无投票券:", "无投票券" in h)
except urllib.error.HTTPError as e:
    h = e.read().decode("utf-8", "replace")
    i = h.find("Exception Value")
    print("HTTP", e.code, "|", h[i:i+240] if i >= 0 else "无详情")
