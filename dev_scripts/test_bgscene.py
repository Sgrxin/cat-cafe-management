# -*- coding: utf-8 -*-
"""WebGL 背景场景验证 + 截图"""
from playwright.sync_api import sync_playwright

OUT = r"C:\Users\lx\Desktop\agent\agent\毕设\截图"
errors = []

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1600, "height": 950})
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errors.append(str(e)))

    pg.goto("http://127.0.0.1:8000/", wait_until="networkidle")
    pg.wait_for_timeout(1200)
    state = pg.evaluate("""() => {
        const c = document.getElementById('bgScene');
        return {
            canvasVisible: c && c.style.display !== 'none',
            w: c ? c.width : 0, h: c ? c.height : 0,
            gl: !!(c && (c.getContext('webgl') || c.getContext('experimental-webgl')))
        };
    }""")
    print("[1] 背景场景:", state)
    pg.click("#enterBtn")
    pg.wait_for_timeout(1500)
    pg.screenshot(path=OUT + r"\01-首页.png", clip={"x": 0, "y": 0, "width": 1600, "height": 950})

    pg.goto("http://127.0.0.1:8000/menu/", wait_until="networkidle")
    pg.wait_for_timeout(1400)
    pg.screenshot(path=OUT + r"\03-商品菜单.png", clip={"x": 0, "y": 0, "width": 1600, "height": 950})

    # 点单回归
    pg.locator('form[action*="order"] button:not([disabled])').first.click()
    pg.wait_for_load_state("networkidle")
    print("[2] 下单回归:", pg.url.split("8000")[1])

    b.close()
print("JS错误:", errors if errors else "无")
print("DONE")
