# -*- coding: utf-8 -*-
"""最终视觉确认: 首页(等待动画完成) + 移动端"""
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8000"
OUT = r"C:\Users\lx\Desktop\agent\agent\毕设\截图"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto(BASE + "/login/", timeout=15000)
    page.fill("input[name=username]", "linxin")
    page.fill("input[name=password]", "123456")
    page.get_by_role("button", name="登录").click()
    page.wait_for_load_state("networkidle")
    page.goto(BASE + "/", timeout=15000)
    page.wait_for_timeout(4000)  # 等入场动画播完
    page.screenshot(path=OUT + r"\01-首页.png", full_page=False)
    visible = page.locator(".hero .hero-title").is_visible()
    print("hero标题可见:", visible, "| 截图已更新(桌面)")

    m = browser.new_page(viewport={"width": 390, "height": 844})
    m.goto(BASE + "/", timeout=15000)
    m.wait_for_timeout(3500)
    m.screenshot(path=OUT + r"\01-首页手机端.png", full_page=False)
    print("手机端截图完成")

    browser.close()
