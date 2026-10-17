# -*- coding: utf-8 -*-
import re
import urllib.parse
import urllib.request
import http.cookiejar

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
r = opener.open("http://127.0.0.1:8000/login/", timeout=10)
html = r.read().decode("utf-8", "replace")
token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html).group(1)
data = urllib.parse.urlencode({"username": "linxin", "password": "123456",
                               "csrfmiddlewaretoken": token}).encode()
req = urllib.request.Request("http://127.0.0.1:8000/login/", data=data,
                             headers={"Referer": "http://127.0.0.1:8000/login/"})
opener.open(req, timeout=10)

r = opener.open("http://127.0.0.1:8000/reserve/", timeout=10)
html = r.read().decode("utf-8", "replace")
print("含reserve_cancel:", "reserve_cancel" in html)
print("含cancel:", "cancel" in html)
i = html.find("我的预约")
seg = re.sub(r"\s+", " ", html[i:i+700])
print("---片段---")
print(seg)
