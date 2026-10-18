# -*- coding: utf-8 -*-
"""有头模式复测：真实浏览器合成路径下是否还有黑块"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=False, args=["--use-angle=default"])
    pg = b.new_page(viewport={"width": 1600, "height": 950})
    pg.goto("http://127.0.0.1:8000/login/")
    pg.fill('form[method="post"] input[name="username"]', "admin")
    pg.fill('form[method="post"] input[name="password"]', "Admin@123")
    pg.click('form[method="post"] button.btn-main')
    pg.wait_for_load_state("networkidle")
    pg.goto("http://127.0.0.1:8000/staff/redemptions/", wait_until="networkidle")
    pg.wait_for_timeout(1500)
    pg.screenshot(path=r"C:\Users\lx\Desktop\agent\agent\毕设\截图\16-店员兑换核销.png")
    print("有头模式截图完成")
    pg.goto("http://127.0.0.1:8000/", wait_until="networkidle")
    pg.wait_for_timeout(1200)
    pg.screenshot(path=r"C:\Users\lx\Desktop\agent\agent\毕设\截图\01-首页.png")
    print("首页截图完成")
    b.close()
