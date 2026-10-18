# -*- coding: utf-8 -*-
"""预约页截图（绿色标题条版）"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1600, "height": 950})
    pg.goto("http://127.0.0.1:8000/login/")
    pg.fill('form[method="post"] input[name="username"]', "admin")
    pg.fill('form[method="post"] input[name="password"]', "Admin@123")
    pg.click('form[method="post"] button.btn-main')
    pg.wait_for_load_state("networkidle")
    pg.goto("http://127.0.0.1:8000/reserve/", wait_until="networkidle")
    pg.wait_for_timeout(600)
    pg.screenshot(path=r"C:\Users\lx\Desktop\agent\agent\毕设\截图\05-工位预约.png")
    print("reserve截好")
    b.close()
