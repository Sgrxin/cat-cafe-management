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
print("含 reserve_cancel:", "reserve_cancel" in html)
i = html.find("我的预约")
seg = html[i:i+900]
print("---渲染片段---")
print(re.sub(r"\s+", " ", seg)[:800])
