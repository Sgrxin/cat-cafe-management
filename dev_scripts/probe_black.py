# -*- coding: utf-8 -*-
"""黑块探针：黑区(800,80)与棕方块(60,80)处是什么元素"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1600, "height": 950})
    pg.goto("http://127.0.0.1:8000/login/")
    pg.fill('form[method="post"] input[name="username"]', "admin")
    pg.fill('form[method="post"] input[name="password"]', "Admin@123")
    pg.click('form[method="post"] button.btn-main')
    pg.wait_for_load_state("networkidle")
    pg.goto("http://127.0.0.1:8000/staff/redemptions/", wait_until="networkidle")
    pg.wait_for_timeout(1500)
    info = pg.evaluate("""() => {
        function at(x, y) {
            const el = document.elementFromPoint(x, y);
            if (!el) return null;
            const cs = getComputedStyle(el);
            const r = el.getBoundingClientRect();
            return {tag: el.tagName, id: el.id, cls: (el.className||'').toString().slice(0,60),
                    bg: cs.backgroundColor, pos: cs.position, z: cs.zIndex,
                    rect: [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)]};
        }
        const c = document.getElementById('bgScene');
        return {
            blackZone: at(800, 75),
            brownSq: at(60, 80),
            below: at(800, 400),
            canvas: c ? {w: c.width, h: c.height, style: c.getAttribute('style')} : null,
            bodyChildren: Array.from(document.body.children).map(e =>
                e.tagName + '#' + (e.id||'') + '.' + (e.className||'').toString().split(' ')[0])
        };
    }""")
    for k, v in info.items():
        print(k, "=>", v)
    b.close()
