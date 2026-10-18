# -*- coding: utf-8 -*-
"""诊断admin视角各页面状态"""
import re
import urllib.error
import urllib.request
import http.cookiejar

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

r = opener.open("http://127.0.0.1:8000/login/", timeout=10)
h = r.read().decode("utf-8", "replace")
t = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', h).group(1)
d = urllib.parse.urlencode({"username": "admin", "password": "Admin@123",
                            "csrfmiddlewaretoken": t}).encode()
req = urllib.request.Request("http://127.0.0.1:8000/login/", data=d,
                             headers={"Referer": "http://127.0.0.1:8000/login/"})
opener.open(req, timeout=10)

for path in ["/redeem/", "/dashboard/", "/vote/", "/me/", "/orders/"]:
    try:
        r = opener.open("http://127.0.0.1:8000" + path, timeout=10)
        h = r.read().decode("utf-8", "replace")
        print(f"{path} -> 200 len={len(h)}")
    except urllib.error.HTTPError as e:
        h = e.read().decode("utf-8", "replace")
        i = h.find("Exception Value")
        detail = h[i:i + 220].replace("\n", " ") if i >= 0 else "no-detail"
        print(f"{path} -> 500 | {detail}")
