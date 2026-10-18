# -*- coding: utf-8 -*-
"""v7 全局验证：粘性页脚 + 色板 + 导航毛玻璃"""
from playwright.sync_api import sync_playwright

OUT = r"C:\Users\lx\Desktop\agent\agent\毕设\截图"
errors = []

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1600, "height": 950})
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto("http://127.0.0.1:8000/login/")
    pg.fill('form[method="post"] input[name="username"]', "admin")
    pg.fill('form[method="post"] input[name="password"]', "Admin@123")
    pg.click('form[method="post"] button.btn-main')
    pg.wait_for_load_state("networkidle")

    # 1. 粘性页脚：短页(核销空表可能) vs 长页(订单管理) footer 底边都应 >= 视口底
    for path in ["/staff/redemptions/", "/staff/orders/", "/me/", "/"]:
        pg.goto(f"http://127.0.0.1:8000{path}", wait_until="networkidle")
        pg.wait_for_timeout(400)
        r = pg.evaluate("""() => {
            const f = document.querySelector('.footer').getBoundingClientRect();
            return {footerBottom: Math.round(f.bottom), vh: window.innerHeight,
                    docH: document.documentElement.scrollHeight};
        }""")
        pinned = r["footerBottom"] >= r["vh"] - 2
        print(f"[footer] {path}: bottom={r['footerBottom']} vh={r['vh']} pinned={pinned}")

    # 2. 色板生效抽查
    pg.goto("http://127.0.0.1:8000/", wait_until="networkidle")
    pal = pg.evaluate("""() => {
        const cs = getComputedStyle(document.body);
        const btn = document.querySelector('.btn-main');
        return {bg: cs.backgroundColor, ink: cs.color,
                btnBg: btn ? getComputedStyle(btn).backgroundColor : '-'};
    }""")
    print("[palette]", pal)

    # 3. 导航滚动奶白毛玻璃
    pg.evaluate("window.scrollTo(0, 300)")
    pg.wait_for_timeout(500)
    nav = pg.evaluate("""() => {
        const n = document.querySelector('.nav-warm');
        const s = getComputedStyle(n);
        return {scrolled: n.classList.contains('scrolled'),
                bg: s.backgroundColor, blur: s.backdropFilter};
    }""")
    print("[nav scrolled]", nav)
    pg.screenshot(path=OUT + r"\01-首页.png", clip={"x": 0, "y": 0, "width": 1600, "height": 950})

    # 4. 短页截图（核销页脚不顶上来）
    pg.goto("http://127.0.0.1:8000/staff/redemptions/", wait_until="networkidle")
    pg.wait_for_timeout(600)
    pg.screenshot(path=OUT + r"\16-店员兑换核销.png")

    b.close()
print("JS错误:", errors if errors else "无")
print("DONE")
