# -*- coding: utf-8 -*-
"""给年糕(布偶猫)换无水印图：TheCatAPI 布偶图 + 备选 cataas"""
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
target = Path(r"C:\Users\lx\Desktop\agent\agent\毕设\media\cats\cat_15.jpg")
backup = target.with_suffix(".jpg.bak")

# 备份原图
if not backup.exists():
    backup.write_bytes(target.read_bytes())

ok = False
# 尝试 TheCatAPI 布偶品种图
try:
    req = urllib.request.Request(
        "https://api.thecatapi.com/v1/images/search?limit=8&has_breeds=true", headers=UA)
    import json
    data = json.load(urllib.request.urlopen(req, timeout=15))
    cands = [it for it in data if any(b.get("name") == "Ragdoll" for b in it.get("breeds", []))]
    print("候选布偶图:", len(cands))
    for it in cands[:3]:
        try:
            img = urllib.request.urlopen(urllib.request.Request(it["url"], headers=UA), timeout=15).read()
            if len(img) > 20000:
                target.write_bytes(img)
                ok = True
                print("已替换:", it["url"][:70], len(img), "bytes")
                break
        except Exception as e:
            print("下载失败:", e)
except Exception as e:
    print("TheCatAPI失败:", e)

if not ok:
    # 备选：cataas 随机图（不保证布偶但无水印）
    try:
        img = urllib.request.urlopen(
            urllib.request.Request("https://cataas.com/cat?width=800&height=1000", headers=UA), timeout=15).read()
        if len(img) > 15000:
            target.write_bytes(img)
            ok = True
            print("cataas 备选已用,", len(img), "bytes")
    except Exception as e:
        print("cataas失败:", e)

print("RESULT:", "OK" if ok else "KEEP-ORIGINAL(可回滚 .bak)")
