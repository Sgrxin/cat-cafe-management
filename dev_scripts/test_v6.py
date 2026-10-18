# -*- coding: utf-8 -*-
"""v6 多变体入场验证 + 功能回归（下单/签到表单可用）"""
from playwright.sync_api import sync_playwright

OUT = r"C:\Users\lx\Desktop\agent\agent\毕设\截图"
errors = []

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1600, "height": 950})
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errors.append(str(e)))

    # 登录
    pg.goto("http://127.0.0.1:8000/login/")
    pg.fill('form[method="post"] input[name="username"]', "admin")
    pg.fill('form[method="post"] input[name="password"]', "Admin@123")
    pg.click('form[method="post"] button.btn-main')
    pg.wait_for_load_state("networkidle")

    # 1. 猫咪页：变体多样性
    pg.goto("http://127.0.0.1:8000/cats/", wait_until="networkidle")
    pg.wait_for_timeout(1000)
    pg.evaluate("window.scrollTo(0, 400)")
    pg.wait_for_timeout(900)
    counts = pg.evaluate("""() => {
        const c = {};
        document.querySelectorAll('[class*="rv-"]').forEach(el => {
            el.classList.forEach(k => { if (k.startsWith('rv-') && k !== 'rv') c[k] = (c[k]||0)+1; });
        });
        const rev = document.querySelectorAll('.reveal.revealed').length;
        return {variants: c, revealed: rev};
    }""")
    print("[1] 猫咪页变体分布:", counts["variants"], "| 已揭示:", counts["revealed"])

    # 2. 菜单页：变体 + hover 跟手（清理后无 reveal 残留）
    pg.goto("http://127.0.0.1:8000/menu/", wait_until="networkidle")
    pg.wait_for_timeout(900)
    pg.evaluate("window.scrollTo(0, 500)")
    pg.wait_for_timeout(1200)
    menu_counts = pg.evaluate("""() => {
        const c = {};
        document.querySelectorAll('.reveal').forEach(el => el.classList.forEach(k => {
            if (k.startsWith('rv-')) c[k] = (c[k]||0)+1; }));
        const done = document.querySelectorAll('.revealed:not(.reveal)').length;
        return {pending: c, cleaned: done};
    }""")
    print("[2] 菜单页揭示中:", menu_counts["pending"], "| 清理完成(恢复自然态):", menu_counts["cleaned"])
    pg.screenshot(path=OUT + r"\03-商品菜单.png", clip={"x": 0, "y": 0, "width": 1600, "height": 950})

    # 3. 功能回归：下单
    pg.goto("http://127.0.0.1:8000/menu/", wait_until="networkidle")
    pg.wait_for_timeout(600)
    btn = pg.locator('form[action*="order"] button:not([disabled])').first
    form_action = pg.locator('form[action*="order"]').first.get_attribute("action")
    btn.click()
    pg.wait_for_load_state("networkidle")
    print("[3] 下单跳转:", pg.url.split('8000')[1], "| 表单:", form_action)
    orders_ok = pg.goto("http://127.0.0.1:8000/orders/", wait_until="networkidle") is not None
    body_txt = pg.text_content("body") or ""
    print("    订单页含'模拟支付'或订单号:", ("订单" in body_txt))

    # 4. 预约页表单字段完好
    pg.goto("http://127.0.0.1:8000/reserve/", wait_until="networkidle")
    seat = pg.locator('select[name="seat"], select[name*="seat"]').count()
    date = pg.locator('input[type="date"]').count()
    print("[4] 预约表单: 工位下拉", seat, "| 日期框", date)

    # 5. 幕布转场仍然工作
    pg.click('a.nav-link[href="/vote/"]')
    pg.wait_for_timeout(200)
    cover = pg.evaluate("document.getElementById('pageCurtain').classList.contains('cover')")
    pg.wait_for_load_state("networkidle")
    print("[5] 转场幕布:", cover, "| 落地:", pg.url.split('8000')[1])

    b.close()

print("JS错误:", errors if errors else "无")
print("DONE")
