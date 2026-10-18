# -*- coding: utf-8 -*-
"""ScrollTrigger 状态诊断"""
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8000"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    logs = []
    page.on("console", lambda m: logs.append(f"[{m.type}] {m.text[:120]}"))
    page.on("pageerror", lambda e: logs.append(f"[pageerror] {str(e)[:150]}"))

    page.goto(BASE + "/login/", timeout=15000)
    page.fill("input[name=username]", "linxin")
    page.fill("input[name=password]", "123456")
    page.get_by_role("button", name="登录").click()
    page.wait_for_load_state("networkidle")
    page.goto(BASE + "/", timeout=15000)
    page.wait_for_timeout(3000)

    diag = page.evaluate("""() => {
      const out = {};
      out.stCount = (typeof ScrollTrigger !== 'undefined') ? ScrollTrigger.getAll().length : -1;
      const rev = document.querySelector('.reveal');
      if (rev) {
        const cs = getComputedStyle(rev);
        out.revealOpacity = cs.opacity;
        out.revealTransform = cs.transform.slice(0, 40);
        out.revealText = rev.textContent.trim().slice(0, 20);
        const r = rev.getBoundingClientRect();
        out.revealTop = Math.round(r.top);
      }
      out.scrollY = window.scrollY;
      out.vh = window.innerHeight;
      return out;
    }""")
    print("ScrollTrigger 实例数:", diag.get("stCount"))
    print("第一个.reveal: opacity=", diag.get("revealOpacity"),
          "| transform=", diag.get("revealTransform"),
          "| top=", diag.get("revealTop"), "px (视口高", diag.get("vh"), ")")
    print("内容:", diag.get("revealText"))
    print("=== 控制台 ===")
    for l in logs[:10]:
        print(" ", l)
    browser.close()
