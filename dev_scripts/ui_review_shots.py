# -*- coding: utf-8 -*-
"""全页面自检截图: 会员视角 + 店员视角"""
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8000"
OUT = r"C:\Users\lx\AppData\Local\Temp\opencode\ui_review"
import os
os.makedirs(OUT, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    # 会员视角
    page.goto(BASE + "/login/", timeout=15000)
    page.fill("input[name=username]", "linxin")
    page.fill("input[name=password]", "123456")
    page.click("button.btn-main")
    page.wait_for_load_state("networkidle")

    pages = ["/", "/cats/", "/menu/", "/reserve/", "/me/", "/orders/",
             "/redeem/", "/vote/", "/about/", "/search/?q=猫"]
    for path in pages:
        page.goto(BASE + path, timeout=15000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(500)
        name = path.replace("/", "_").replace("?", "_").replace("=", "-") or "_home"
        page.screenshot(path=OUT + f"\\m{name}.png", full_page=True)
        print("shot", path)

    # 店员视角
    page.goto(BASE + "/logout/", timeout=15000)
    login2 = "dianyuan"
    page.goto(BASE + "/login/", timeout=15000)
    page.fill("input[name=username]", login2)
    page.fill("input[name=password]", "Dy@123456")
    page.click("button.btn-main")
    page.wait_for_load_state("networkidle")
    for path in ["/", "/staff/orders/", "/staff/redemptions/"]:
        page.goto(BASE + path, timeout=15000)
        page.wait_for_timeout(500)
        name = path.replace("/", "_") or "_home"
        page.screenshot(path=OUT + f"\\s{name}.png", full_page=True)
        print("shot", path)

    # 管理员看板
    page.goto(BASE + "/logout/", timeout=15000)
    page.goto(BASE + "/login/", timeout=15000)
    page.fill("input[name=username]", "admin")
    page.fill("input[name=password]", "Admin@123")
    page.click("button.btn-main")
    page.wait_for_load_state("networkidle")
    page.goto(BASE + "/dashboard/", timeout=15000)
    page.wait_for_timeout(2000)
    page.screenshot(path=OUT + r"\a_dashboard.png", full_page=True)
    print("shot dashboard")

    browser.close()
print("=== 自检截图完成 ===")
