# -*- coding: utf-8 -*-
"""taste方法论: 提取参考网站的设计基因(色板/字体/圆角/阴影)"""
from playwright.sync_api import sync_playwright
import json

SITES = [
    ("nayuki", "https://www.nayuki.cn/"),
    ("sexytea", "https://www.sexytea.com/"),
    ("heytea", "https://www.heyttea.com/"),
]

JS_EXTRACT = """() => {
  const out = {colors: {}, fonts: {}, radii: []};
  const bodyCs = getComputedStyle(document.body);
  out.bodyBg = bodyCs.backgroundColor;
  out.bodyColor = bodyCs.color;
  out.bodyFont = bodyCs.fontFamily.slice(0, 80);
  // 收集全页高频颜色
  const colorCount = {};
  const all = document.querySelectorAll('*');
  let n = 0;
  for (const el of all) {
    if (n > 800) break;
    n++;
    const cs = getComputedStyle(el);
    for (const prop of ['backgroundColor', 'color']) {
      const v = cs[prop];
      if (v && v !== 'rgba(0, 0, 0, 0)' && v !== 'rgb(0, 0, 0)') {
        colorCount[v] = (colorCount[v] || 0) + 1;
      }
    }
    const br = cs.borderRadius;
    if (br && br !== '0px' && !out.radii.includes(br)) out.radii.push(br);
    const ff = cs.fontFamily;
    if (ff && !out.fonts.main) out.fonts.main = ff.slice(0, 60);
    // 主按钮
    const cls = (el.className || '').toString().toLowerCase();
    if ((cls.includes('btn') || cls.includes('button')) && !out.btnBg) {
      out.btnBg = cs.backgroundColor;
      out.btnColor = cs.color;
      out.btnRadius = cs.borderRadius;
    }
    // 大标题
    if (['H1','H2'].includes(el.tagName) && !out.h1) {
      out.h1 = {text: el.innerText.slice(0, 20), size: cs.fontSize, weight: cs.fontWeight, color: cs.color};
    }
  }
  out.topColors = Object.entries(colorCount).sort((a,b)=>b[1]-a[1]).slice(0,12);
  return out;
}"""

results = {}
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    for name, url in SITES:
        try:
            page.goto(url, timeout=25000)
            page.wait_for_timeout(3500)
            data = page.evaluate(JS_EXTRACT)
            results[name] = data
            print(f"=== {name} ===")
            print("  主按钮:", data.get("btnBg"), data.get("btnRadius"))
            print("  H1:", json.dumps(data.get("h1"), ensure_ascii=False)[:100])
            print("  高频色:", [c for c, _ in data.get("topColors", [])][:8])
        except Exception as e:
            print(f"{name} 失败: {str(e)[:60]}")
    browser.close()

with open(r"C:\Users\lx\AppData\Local\Temp\opencode\taste_tokens.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print("=== 提取完成 ===")
