# -*- coding: utf-8 -*-
"""复测领奖台图片"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1600, "height": 950})
    pg.goto("http://127.0.0.1:8000/login/")
    pg.fill('form[method="post"] input[name="username"]', "admin")
    pg.fill('form[method="post"] input[name="password"]', "Admin@123")
    pg.click('form[method="post"] button.btn-main')
    pg.wait_for_load_state("networkidle")
    pg.goto("http://127.0.0.1:8000/vote/", wait_until="networkidle")
    pg.wait_for_timeout(500)
    print("领奖台图可见:", pg.is_visible(".podium-slot img"))
    pg.screenshot(path=r"C:\Users\lx\Desktop\agent\agent\毕设\截图\11-猫王投票.png", clip={"x":0,"y":0,"width":1600,"height":900})
    b.close()
print("DONE")
