# -*- coding: utf-8 -*-
"""转场动画层自检：轻渐出转场 + 开屏淡出 + 滚动系统 + 功能抽测"""
import sys, time
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8000"
console_errors, page_errors, results = [], [], []

def check(name, ok, detail=""):
    results.append(bool(ok))
    print(("PASS  " if ok else "FAIL  ") + name + (("  | " + str(detail)) if detail else ""))

with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context()
    page = ctx.new_page()
    page.on("console", lambda m: console_errors.append(f"{page.url} :: {m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: page_errors.append(f"{page.url} :: {e}"))

    # ---- 登录 ----
    page.goto(BASE + "/login/", wait_until="load")
    page.fill('form[method="post"] input[name="username"]', "admin")
    page.fill('form[method="post"] input[name="password"]', "Admin@123")
    page.click('form[method="post"] button.btn-main')
    page.wait_for_load_state("load")
    check("登录 admin/Admin@123", "/login" not in page.url, page.url)

    # ---- 开屏流程（先清 sessionStorage，走真实用户路径）----
    page.evaluate("sessionStorage.clear()")
    page.goto(BASE + "/", wait_until="load")
    page.wait_for_timeout(250)
    splash_visible = page.evaluate(
        "(function(){var s=document.getElementById('splash');"
        "return !!s && getComputedStyle(s).display!=='none' && parseFloat(getComputedStyle(s).opacity)>0.9;})()")
    check("清 storage 后 #splash 可见", splash_visible)
    page.click("#enterBtn")
    page.wait_for_timeout(500)  # transition .55s 进行中，display:none 在 580ms
    mid_op = page.evaluate("parseFloat(getComputedStyle(document.getElementById('splash')).opacity)")
    check("splash 淡出进行中(500ms opacity<0.5)", mid_op < 0.5, f"opacity={mid_op:.2f}")
    page.wait_for_timeout(700)  # 累计 1200ms
    st = page.evaluate(
        "(function(){var s=document.getElementById('splash');return {"
        "hidden:getComputedStyle(s).display==='none',"
        "entered:document.body.classList.contains('entered'),"
        "pe:getComputedStyle(s).pointerEvents};})()")
    check("splash 隐藏且 body.entered", st["hidden"] and st["entered"], str(st))
    hero_op = 0.0
    for _ in range(30):
        hero_op = page.evaluate("parseFloat(getComputedStyle(document.querySelector('.hero-kicker')).opacity)")
        if hero_op > 0.95:
            break
        page.wait_for_timeout(100)
    check("hero 出现(.hero-kicker opacity→1)", hero_op > 0.95, f"opacity={hero_op:.2f}")

    # ---- 导航轻渐出转场：/ -> /cats/ ----
    page.wait_for_timeout(1500)  # 等 page-in 清理完，测纯转场
    t0 = time.monotonic()
    page.click('.nav-warm .nav-link:text-is("猫咪")')
    has_out = page.evaluate("document.body.classList.contains('nav-out')")
    body_op = page.evaluate("parseFloat(getComputedStyle(document.getElementById('pageBody')).opacity)")
    moved = True
    try:
        page.wait_for_url("**/cats/", timeout=2500)
    except Exception:
        moved = False
    ms = (time.monotonic() - t0) * 1000
    check("点击导航后 body 获得 nav-out", has_out, f"pageBody opacity={body_op:.2f}")
    check("转场触发跳转且未被提前打断(>=150ms)", moved and ms >= 150, f"click→URL变更 {ms:.0f}ms")
    check("跳转及时(<1500ms)", moved and ms < 1500, f"{ms:.0f}ms")
    page.wait_for_load_state("load")
    kids = page.evaluate("document.getElementById('pageBody').children.length")
    check("落地 /cats/ 正常渲染", kids > 0 and "/cats" in page.url, f"children={kids} url={page.url}")

    # ---- 滚动系统 ----
    page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight/3)")
    page.wait_for_timeout(400)
    w = page.evaluate("parseFloat(document.getElementById('scrollProgress').style.width)")
    scrolled = page.evaluate("document.querySelector('.nav-warm').classList.contains('scrolled')")
    check("进度条宽度更新", w > 0, f"width={w:.1f}%")
    check("导航获得 scrolled", scrolled)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(400)
    scrolled2 = page.evaluate("document.querySelector('.nav-warm').classList.contains('scrolled')")
    check("回顶后 scrolled 移除", not scrolled2)

    # ---- 功能抽测：/menu/ 点单 ----
    page.goto(BASE + "/menu/", wait_until="load")
    page.wait_for_timeout(300)
    cnt = page.locator('#pageBody form button.btn-main:not([disabled])').count()
    check("/menu/ 存在未禁用点单按钮", cnt > 0, f"count={cnt}")
    if cnt > 0:
        page.locator('#pageBody form button.btn-main:not([disabled])').first.click()
        moved2 = True
        try:
            page.wait_for_url(lambda u: "/menu" not in u, timeout=3000)
        except Exception:
            moved2 = False
        page.wait_for_load_state("load")
        check("点单跳转订单页", moved2 and "/menu" not in page.url, page.url)

    # ---- 功能抽测：/reserve/ 表单 ----
    page.goto(BASE + "/reserve/", wait_until="load")
    n = page.evaluate(
        "document.querySelectorAll('#pageBody form input, #pageBody form select,"
        " #pageBody form textarea, #pageBody form button').length")
    check("/reserve/ 表单字段存在", n >= 3, f"控件数={n}")

    browser.close()

print("-" * 50)
print(f"console error: {len(console_errors)}")
for e in console_errors:
    print("   " + e)
print(f"pageerror: {len(page_errors)}")
for e in page_errors:
    print("   " + e)
ok = all(results) and not console_errors and not page_errors
print("RESULT:", "ALL GREEN" if ok else "HAS FAILURES")
sys.exit(0 if ok else 1)
