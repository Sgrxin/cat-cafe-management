# -*- coding: utf-8 -*-
"""遍历pageBody子块找390溢出源"""
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
    r = pg.evaluate("""() => {
        const sw = () => document.documentElement.scrollWidth;
        const base = sw();
        const out = [];
        const kids = Array.from(document.getElementById('pageBody').children);
        kids.forEach(k => {
            const d = k.style.display, v = k.style.visibility;
            k.style.display = 'none';
            const after = sw();
            k.style.display = d;
            out.push({tag: k.tagName + '.' + (k.className||'').toString().split(' ')[0].slice(0,24),
                      hidesTo: after, fixes: after === 390});
        });
        return {base, out};
    }""")
    print("base:", r["base"])
    for o in r["out"]:
        mark = " <== 修复" if o["fixes"] else ""
        print(f"  {o['tag']}: hide->{o['hidesTo']}{mark}")
    b.close()
