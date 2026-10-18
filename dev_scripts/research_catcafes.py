# -*- coding: utf-8 -*-
"""横向调研真实猫咖网站: 截图+设计token提取"""
from playwright.sync_api import sync_playwright
import json
import os

OUT = r"C:\Users\lx\AppData\Local\Temp\opencode\research"
os.makedirs(OUT, exist_ok=True)

SITES = [
    ("mofumofu_jp", "https://www.mofumofu-cafe.com/"),
    ("catcafe_nekokura", "https://catcafe.nekokura.com/"),
    ("mocha_jp", "https://www.mocha-cat.com/"),
]

EXTRACT = """() => {
  const out = {};
  const cs = getComputedStyle(document.body);
  out.bodyBg = cs.backgroundColor;
  out.bodyFont = cs.fontFamily.slice(0, 70);
  const colors = {};
  let n = 0;
  for (const el of document.querySelectorAll('*')) {
    if (n > 600) break;
    n++;
    const c = getComputedStyle(el);
    for (const k of ['backgroundColor', 'color']) {
      const v = c[k];
      if (v && v !== 'rgba(0, 0, 0, 0)') colors[v] = (colors[v] || 0) + 1;
    }
    const r = c.borderRadius;
    if (r && r !== '0px' && !(out.radii || []).includes(r)) (out.radii = out.radii || []).push(r);
  }
  out.topColors = Object.entries(colors).sort((a, b) => b[1] - a[1]).slice(0, 10).map(x => x[0]);
  const h = document.querySelector('h1,h2');
  if (h) { const hc = getComputedStyle(h); out.h1 = { text: h.innerText.slice(0, 16), font: hc.fontFamily.slice(0, 50), size: hc.fontSize }; }
  const imgs = document.querySelectorAll('img');
  out.imgCount = imgs.length;
  const bts = document.querySelector('.btn, button, [class*=button]');
  if (bts) { const bc = getComputedStyle(bts); out.btn = { bg: bc.backgroundColor, radius: bc.borderRadius }; }
  return out;
}"""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    results = {}
    for name, url in SITES:
        try:
            page.goto(url, timeout=25000)
            page.wait_for_timeout(4000)
            data = page.evaluate(EXTRACT)
            results[name] = data
            page.screenshot(path=os.path.join(OUT, name + ".png"), full_page=False)
            print(f"=== {name} ✓")
            print("  底色:", data["bodyBg"], "| 字体:", data["bodyFont"][:40])
            print("  高频色:", data["topColors"])
            print("  圆角:", (data.get("radii") or [])[:4])
            if data.get("h1"): print("  主标题:", data["h1"])
            if data.get("btn"): print("  按钮:", data["btn"])
        except Exception as e:
            print(f"{name} 失败: {str(e)[:60]}")
    browser.close()

with open(os.path.join(OUT, "tokens.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print("=== 调研完成 ===")
