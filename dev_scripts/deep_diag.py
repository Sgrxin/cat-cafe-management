# -*- coding: utf-8 -*-
"""深度诊断: GSAP状态 / 元素样式 / rAF是否活着"""
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8000"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    logs = []
    page.on("console", lambda m: logs.append(f"[{m.type}] {m.text[:150]}"))
    page.on("pageerror", lambda e: logs.append(f"[pageerror] {str(e)[:150]}"))

    page.goto(BASE + "/login/", timeout=15000)
    page.fill("input[name=username]", "linxin")
    page.fill("input[name=password]", "123456")
    page.get_by_role("button", name="登录").click()
    page.wait_for_load_state("networkidle")
    page.goto(BASE + "/", timeout=15000)
    page.wait_for_timeout(2500)

    diag = page.evaluate("""() => {
      const out = {};
      out.gsap = typeof gsap !== 'undefined' ? 'loaded' : 'MISSING';
      out.st = typeof ScrollTrigger !== 'undefined' ? 'loaded' : 'MISSING';
      const span = document.querySelector('.hero-line span');
      if (span) {
        const cs = getComputedStyle(span);
        out.spanTransform = cs.transform;
        out.spanOpacity = cs.opacity;
        out.spanText = span.textContent;
      }
      const hero = document.querySelector('.hero');
      out.heroH = hero ? hero.getBoundingClientRect().height : -1;
      // rAF活性检测
      out.rafTest = new Promise(res => {
        let n = 0; const t0 = performance.now();
        function tick(){ n++; if (performance.now() - t0 < 600) requestAnimationFrame(tick); else res(n); }
        requestAnimationFrame(tick);
      });
      return out;
    }""")
    raf = page.evaluate("() => new Promise(res => { let n=0,t0=performance.now(); (function t(){n++; if(performance.now()-t0<600) requestAnimationFrame(t); else res(n);})() })")
    print("gsap:", diag.get("gsap"), "| ScrollTrigger:", diag.get("st"))
    print("span transform:", diag.get("spanTransform"), "| opacity:", diag.get("spanOpacity"))
    print("hero高度:", diag.get("heroH"))
    print("600ms内rAF帧数:", raf)
    print("=== 控制台日志 ===")
    for l in logs[:12]:
        print(" ", l)
    browser.close()
