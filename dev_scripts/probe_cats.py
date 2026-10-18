# -*- coding: utf-8 -*-
"""猫咪页 IO 探针：为什么 revealed=0"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1600, "height": 950})
    pg.goto("http://127.0.0.1:8000/login/")
    pg.fill('form[method="post"] input[name="username"]', "admin")
    pg.fill('form[method="post"] input[name="password"]', "Admin@123")
    pg.click('form[method="post"] button.btn-main')
    pg.wait_for_load_state("networkidle")
    pg.goto("http://127.0.0.1:8000/cats/", wait_until="networkidle")
    pg.wait_for_timeout(1500)
    info = pg.evaluate("""() => ({
        rows: document.querySelectorAll('#pageBody .row').length,
        rowChildren: document.querySelectorAll('#pageBody .row > *').length,
        tagged: document.querySelectorAll('.reveal').length,
        rvRotate: document.querySelectorAll('.rv-rotate').length,
        revealed: document.querySelectorAll('.reveal.revealed').length,
        cleaned: document.querySelectorAll('.revealed:not(.reveal)').length,
        scrollY: window.scrollY,
        pageIn: document.getElementById('pageBody').className,
        firstCol: (document.querySelector('#pageBody .row > *')||{}).className
    })""")
    for k, v in info.items():
        print(f"  {k}: {v}")
    pg.evaluate("window.scrollTo(0, 600)")
    pg.wait_for_timeout(1500)
    info2 = pg.evaluate("""() => ({
        revealed: document.querySelectorAll('.reveal.revealed').length,
        cleaned: document.querySelectorAll('.revealed:not(.reveal)').length,
        stillHidden: document.querySelectorAll('.reveal:not(.revealed)').length,
        scrollY: window.scrollY
    })""")
    print("滚动600后:", info2)
    b.close()
