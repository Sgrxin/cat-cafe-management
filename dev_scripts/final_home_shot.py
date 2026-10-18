# -*- coding: utf-8 -*-
"""纯CSS版首页最终截图(无GSAP依赖)"""
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
    page.wait_for_timeout(1800)
    page.screenshot(path=OUT + r"\01-首页.png", full_page=False)
    browser.close()
print("done")
