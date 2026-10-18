# -*- coding: utf-8 -*-
"""390 复测 + 目检截图"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 390, "height": 844})
    pg.goto("http://127.0.0.1:8000/login/")
    pg.fill('form[method="post"] input[name="username"]', "admin")
    pg.fill('form[method="post"] input[name="password"]', "Admin@123")
    pg.click('form[method="post"] button.btn-main')
    pg.wait_for_load_state("networkidle")
    pg.goto("http://127.0.0.1:8000/", wait_until="networkidle")
    pg.wait_for_timeout(900)
    ovf = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    print("390溢出像素:", ovf)
    pg.screenshot(path=r"C:\Users\lx\Desktop\agent\agent\毕设\截图\20-手机端首页.png")
    b.close()
