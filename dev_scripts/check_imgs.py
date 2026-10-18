# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://127.0.0.1:8000/cats/", timeout=15000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)
    page.screenshot(path=r"C:\Users\lx\AppData\Local\Temp\opencode\cats_img.png", full_page=False)
    page.goto("http://127.0.0.1:8000/reserve/", timeout=15000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)
    page.screenshot(path=r"C:\Users\lx\AppData\Local\Temp\opencode\reserve_img.png", full_page=False)
    # 检查图片是否真实加载(非破图)
    imgs = page.locator("img").all()
    broken = 0
    total = 0
    for img in imgs:
        total += 1
        natural = img.evaluate("e => e.naturalWidth")
        if natural == 0:
            broken += 1
    print(f"reserve页图片: {total}张, 破图{broken}张")
    browser.close()
