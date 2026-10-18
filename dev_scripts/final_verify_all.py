# -*- coding: utf-8 -*-
"""最终视觉验收: 全页面截图(登录会员视角)"""
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8000"
OUT = r"C:\Users\lx\Desktop\agent\agent\毕设\截图"

PAGES = [
    ("/", "01-首页", True),
    ("/cats/", "02-猫咪档案", True),
    ("/menu/", "03-商品菜单", False),
    ("/reserve/", "05-工位预约", False),
    ("/me/", "09-会员中心", False),
    ("/redeem/", "10-积分兑换", False),
    ("/vote/", "11-猫王投票", False),
    ("/orders/", "08-我的订单", False),
    ("/about/", "14-门店信息", True),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto(BASE + "/login/", timeout=15000)
    page.fill("input[name=username]", "linxin")
    page.fill("input[name=password]", "123456")
    page.get_by_role("button", name="登录").click()
    page.wait_for_load_state("networkidle")

    all_ok = True
    for path, name, full in PAGES:
        page.goto(BASE + path, timeout=15000)
        page.wait_for_timeout(1400)
        broken = sum(1 for img in page.locator("img").all() if img.evaluate("e => e.naturalWidth") == 0)
        status = "✓" if broken == 0 else f"✗ 破图{broken}"
        print(f"{path} → {status}")
        page.screenshot(path=OUT + "\\" + name + ".png", full_page=full)
        if broken:
            all_ok = False

    # 店员视角
    page.goto(BASE + "/logout/", timeout=15000)
    page.goto(BASE + "/login/", timeout=15000)
    page.fill("input[name=username]", "dianyuan")
    page.fill("input[name=password]", "Dy@123456")
    page.get_by_role("button", name="登录").click()
    page.wait_for_load_state("networkidle")
    page.goto(BASE + "/staff/orders/", timeout=15000)
    page.wait_for_timeout(1200)
    page.screenshot(path=OUT + r"\15-店员订单管理.png", full_page=False)
    page.goto(BASE + "/staff/redemptions/", timeout=15000)
    page.wait_for_timeout(800)
    page.screenshot(path=OUT + r"\16-店员兑换核销.png", full_page=False)
    print("店员页截图 ✓")

    # 管理员看板
    page.goto(BASE + "/logout/", timeout=15000)
    page.goto(BASE + "/login/", timeout=15000)
    page.fill("input[name=username]", "admin")
    page.fill("input[name=password]", "Admin@123")
    page.get_by_role("button", name="登录").click()
    page.wait_for_load_state("networkidle")
    page.goto(BASE + "/dashboard/", timeout=15000)
    page.wait_for_timeout(2500)
    page.screenshot(path=OUT + r"\17-经营数据看板.png", full_page=False)
    print("看板截图 ✓")

    browser.close()
print("=== 全站最终视觉验收完成 ===" + ("" if all_ok else "（有破图需处理）"))
