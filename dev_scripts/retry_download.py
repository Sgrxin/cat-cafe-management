# -*- coding: utf-8 -*-
"""第二轮: 问题商品的候选图重抓"""
import html as html_mod
import json
import os
import re
import ssl
import time
import urllib.parse
import urllib.request

BASE = r"C:\Users\lx\Desktop\agent\agent\毕设\media\products"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE


def html_unescape(s):
    return html_mod.unescape(s)


def fetch(url, path, timeout=12):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r, open(path, "wb") as f:
        f.write(r.read())
    with open(path, "rb") as f:
        head = f.read(4)
    return os.path.getsize(path) > 4000 and (head[:2] == b"\xff\xd8" or head[:1] == b"\x89")


def bing_murls(query):
    q = urllib.parse.quote(query)
    u = f"https://cn.bing.com/images/search?q={q}&form=HDRSC2&first=1"
    req = urllib.request.Request(u, headers=UA)
    with urllib.request.urlopen(req, timeout=15, context=CTX) as r:
        src = r.read().decode("utf-8", "replace")
    return [html_unescape(m) for m in re.findall(r"murl&quot;:&quot;(.*?)&quot;", src)]


RETRY = {
    3:  "黑糖珍珠鲜奶",
    4:  "冰美式 咖啡杯",
    5:  "咖啡 拿铁 拉花",
    6:  "卡布奇诺 咖啡拉花",
    7:  "玛奇朵 咖啡",
    11: "热可可 奶油",
    13: "提拉米苏 甜品",
    14: "抹茶千层 蛋糕",
    16: "巧克力曲奇 饼干",
    19: "三明治 早餐",
    20: "猫零食 冻干",
    23: "小鱼干 猫零食",
    28: "马克杯 咖啡杯",
}

manifest = []
for idx, q in RETRY.items():
    try:
        urls = bing_murls(q)
    except Exception as e:
        print(f"prod{idx} 搜索失败 {str(e)[:40]}")
        continue
    cand = 0
    for mu in urls[0:8]:
        if cand >= 3:
            break
        path = f"{BASE}/retry_{idx:02d}_{cand}.jpg"
        try:
            if fetch(mu, path):
                manifest.append((idx, cand, path))
                cand += 1
                print(f"prod{idx} cand{cand} ✓")
        except Exception:
            pass
        time.sleep(0.05)

with open(BASE + r"\retry_candidates.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f)
print(f"=== 完成 {len(manifest)} 张 ===")
