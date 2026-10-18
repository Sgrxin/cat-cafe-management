# -*- coding: utf-8 -*-
"""列出所有真实超宽元素（排除hidden容器后代）"""
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
    wide = pg.evaluate("""() => {
        const vw = document.documentElement.clientWidth;
        const inHidden = (el) => {
            let n = el;
            while (n && n !== document.body) {
                const o = getComputedStyle(n).overflowX;
                if (o === 'hidden' || o === 'clip') return true;
                const pos = getComputedStyle(n).position;
                if (pos === 'fixed') return true;
                n = n.parentElement;
            }
            return false;
        };
        const out = [];
        document.querySelectorAll('body *').forEach(el => {
            if (inHidden(el)) return;
            const r = el.getBoundingClientRect();
            if (r.right > vw + 2) {
                out.push({sel: el.tagName + (el.id ? '#'+el.id : '') + '.' +
                          (el.className||'').toString().trim().split(/\s+/).slice(0,2).join('.'),
                          left: Math.round(r.left), right: Math.round(r.right)});
            }
        });
        return out;
    }""")
    for w in wide[:20]:
        print(w)
    b.close()
