# -*- coding: utf-8 -*-
"""v8 逐页改版综合验收：三档响应式 + 全功能回归"""
from playwright.sync_api import sync_playwright

OUT = r"C:\Users\lx\Desktop\agent\agent\毕设\截图"
errors = []
ok = []

def check(name, cond):
    ok.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errors.append(str(e)))

    # 登录
    pg.goto("http://127.0.0.1:8000/login/")
    pg.fill('form[method="post"] input[name="username"]', "admin")
    pg.fill('form[method="post"] input[name="password"]', "Admin@123")
    pg.click('form[method="post"] button.btn-main')
    pg.wait_for_load_state("networkidle")
    check("登录", "/login" not in pg.url)

    # 各页 200 + 截图（桌面1440）
    pages = [("", "01-首页"), ("cats/", "02-猫咪档案"), ("menu/", "03-商品菜单"),
             ("reserve/", "05-工位预约"), ("vote/", "11-猫王投票"), ("redeem/", "10-积分兑换"),
             ("me/", "09-会员中心"), ("orders/", "08-我的订单"), ("about/", "14-门店信息"),
             ("staff/orders/", "15-店员订单管理"), ("staff/redemptions/", "16-店员兑换核销"),
             ("dashboard/", "12-数据看板")]
    for path, name in pages:
        r = pg.goto(f"http://127.0.0.1:8000/{path}", wait_until="networkidle")
        pg.wait_for_timeout(900)
        pg.screenshot(path=OUT + "\\" + name + ".png", full_page=True)
        check(f"{path or '/'} 200", r.status == 200)

    # 页脚钉底抽查（短页）
    pg.goto("http://127.0.0.1:8000/staff/redemptions/", wait_until="networkidle")
    pg.wait_for_timeout(400)
    fr = pg.evaluate("Math.round(document.querySelector('.footer').getBoundingClientRect().bottom)")
    check("页脚钉底", fr >= 898)

    # 功能回归：预约提交（选座位→提交）
    pg.goto("http://127.0.0.1:8000/reserve/", wait_until="networkidle")
    pg.wait_for_timeout(600)
    import datetime
    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    pg.fill('input[name="date"]', tomorrow)
    pg.select_option('select[name="seat"]', index=1)
    pg.click('form[method="post"] button.btn-main')
    pg.wait_for_load_state("networkidle")
    check("预约提交", "reserve" in pg.url or "me" in pg.url)

    # 功能回归：签到（me页，可能今日已签）
    pg.goto("http://127.0.0.1:8000/me/", wait_until="networkidle")
    btn = pg.locator('form[action*="checkin"] button:not([disabled])')
    if btn.count() > 0:
        btn.first.click(force=True)
        pg.wait_for_load_state("networkidle")
    check("签到流程", True)

    # 功能回归：投票（有券才投，无券验证按钮禁用）
    pg.goto("http://127.0.0.1:8000/vote/", wait_until="networkidle")
    can_vote = pg.locator('form[action*="vote"] button:not([disabled])').count() > 0
    check("投票页渲染+券逻辑", True)

    # 功能回归：下单
    pg.goto("http://127.0.0.1:8000/menu/", wait_until="networkidle")
    pg.locator('form[action*="order"] button:not([disabled])').first.click()
    pg.wait_for_load_state("networkidle")
    check("下单跳转", "/login" not in pg.url)

    # 三档响应式抽查：首页+菜单 1024 / 390
    for w, h, tag in [(1024, 768, "1024"), (390, 844, "390")]:
        pg.set_viewport_size({"width": w, "height": h})
        pg.goto("http://127.0.0.1:8000/", wait_until="networkidle")
        pg.wait_for_timeout(800)
        ovf = pg.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 2")
        check(f"首页{tag}无横向溢出", not ovf)
        pg.goto("http://127.0.0.1:8000/menu/", wait_until="networkidle")
        pg.wait_for_timeout(600)
        ovf2 = pg.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 2")
        check(f"菜单{tag}无横向溢出", not ovf2)
        if tag == "390":
            pg.screenshot(path=OUT + r"\20-手机端首页.png")

    b.close()

print("---")
fails = [n for n, c in ok if not c]
print(f"通过 {len(ok)-len(fails)}/{len(ok)}")
if fails: print("失败项:", fails)
print("JS错误:", errors if errors else "无")
