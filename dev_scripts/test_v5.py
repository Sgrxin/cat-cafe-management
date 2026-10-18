# -*- coding: utf-8 -*-
"""v5 高级感系统验证：转场幕布/进度条/毛玻璃导航/滚动渐显/入场动画"""
from playwright.sync_api import sync_playwright

OUT = r"C:\Users\lx\Desktop\agent\agent\毕设\截图"
errors = []

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1600, "height": 950})
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errors.append(str(e)))

    # 1. 首页开屏 -> 进入 -> page-in
    pg.goto("http://127.0.0.1:8000/", wait_until="networkidle")
    pg.click("#enterBtn")
    pg.wait_for_timeout(1800)
    print("[1] 开屏进入后 hero 可见:", pg.is_visible(".hero-photo"))

    # 2. 点击导航"猫咪" -> 抓转场幕布中间帧
    pg.click('a[href="/cats/"]')
    pg.wait_for_timeout(200)
    curtain_covering = pg.evaluate("document.getElementById('pageCurtain').classList.contains('cover')")
    pg.screenshot(path=OUT + r"\19-页面转场幕布.png")
    pg.wait_for_load_state("networkidle")
    pg.wait_for_timeout(1400)
    print("[2] 幕布触发:", curtain_covering, "| 落地页:", pg.url.split('8000')[1])
    print("    页面标题:", pg.title())

    # 3. 滚动 -> 进度条 + 导航毛玻璃 + reveal
    pg.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
    pg.wait_for_timeout(700)
    bar_w = pg.evaluate("document.getElementById('scrollProgress').style.width")
    nav_glass = pg.evaluate("document.querySelector('.nav-warm').classList.contains('scrolled')")
    revealed = pg.evaluate("document.querySelectorAll('.reveal.revealed').length")
    total_rv = pg.evaluate("document.querySelectorAll('.reveal').length")
    print(f"[3] 进度条宽度: {bar_w} | 导航毛玻璃: {nav_glass} | 渐显 {revealed}/{total_rv}")
    pg.screenshot(path=OUT + r"\02-猫咪档案.png")

    # 4. 再跳菜单页验证玻璃卡片
    pg.click('a.nav-link[href="/menu/"]')
    pg.wait_for_load_state("networkidle")
    pg.wait_for_timeout(1500)
    glass = pg.evaluate("getComputedStyle(document.querySelector('.menu-board')).backdropFilter || 'none'")
    card_glass = pg.evaluate("getComputedStyle(document.querySelector('.card')).backdropFilter || 'none'")
    print("[4] 菜单页 玻璃卡片 backdropFilter:", card_glass, "| 幕布重置:", pg.evaluate("!document.getElementById('pageCurtain').classList.contains('cover')"))
    pg.screenshot(path=OUT + r"\03-商品菜单.png", clip={"x": 0, "y": 0, "width": 1600, "height": 950})

    b.close()

print("JS错误:", errors if errors else "无")
print("DONE")
