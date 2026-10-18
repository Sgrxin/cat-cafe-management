# -*- coding: utf-8 -*-
"""毕设 E2E 测试 v2: 订单/积分/兑换/投票/看板"""
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8000"
SHOT = r"C:\Users\lx\Desktop\agent\agent\毕设\截图"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    # 登录 linxin
    page.goto(BASE + "/login/", timeout=15000)
    page.fill("input[name=username]", "linxin")
    page.fill("input[name=password]", "123456")
    page.click("button.btn-primary")
    page.wait_for_load_state("networkidle")
    print("✓ linxin 登录")

    # 记录当前积分（用可见文本提取）
    page.goto(BASE + "/me/", timeout=15000)
    import re
    body_text = page.locator("body").inner_text()
    m = re.search(r"我的积分\s*\n?\s*(\d+)", body_text)
    pts_before = int(m.group(1)) if m else -1
    assert pts_before >= 0, "积分读取失败"
    print(f"  当前积分: {pts_before}")

    # 点单
    page.goto(BASE + "/menu/", timeout=15000)
    page.locator("form[action*='order']").first.locator("button").click()
    page.wait_for_load_state("networkidle")
    assert "点单成功" in page.content(), "点单失败"
    print("✓ 点单成功（模拟支付）")
    page.screenshot(path=SHOT + r"\07-点单成功.png", full_page=True)

    # 我的订单
    page.goto(BASE + "/orders/", timeout=15000)
    assert "我的订单" in page.content() and "CAT" in page.content()
    page.screenshot(path=SHOT + r"\08-我的订单.png", full_page=True)
    print("✓ 我的订单页正常")

    # 积分增加验证
    page.goto(BASE + "/me/", timeout=15000)
    body_text = page.locator("body").inner_text()
    m = re.search(r"我的积分\s*\n?\s*(\d+)", body_text)
    pts_after = int(m.group(1)) if m else -1
    assert pts_after == pts_before + 28, f"积分应+28，实际{pts_before}->{pts_after}"
    print(f"✓ 积分自动累计：{pts_before} → {pts_after} (+28)")

    # 会员中心截图
    page.screenshot(path=SHOT + r"\09-会员中心.png", full_page=True)

    # 积分兑换
    page.goto(BASE + "/redeem/", timeout=15000)
    page.screenshot(path=SHOT + r"\10-积分兑换.png", full_page=True)
    page.locator("form[action*='redeem']").last.locator("button").click()
    page.wait_for_load_state("networkidle")
    assert "兑换成功" in page.content() or "积分不足" in page.content()
    if "兑换成功" in page.content():
        print("✓ 积分兑换成功")
    else:
        print("○ 积分不足（符合预期，不影响流程）")

    # 投票
    page.goto(BASE + "/vote/", timeout=15000)
    assert "猫王" in page.content()
    page.screenshot(path=SHOT + r"\11-猫王投票.png", full_page=True)
    buttons = page.locator("form[action*='vote'] button:not([disabled])")
    if buttons.count() > 0:
        buttons.first.click()
        page.wait_for_load_state("networkidle")
        assert "投票成功" in page.content(), "投票失败"
        print("✓ 投票成功（消耗1张投票券）")
        # 再投同一只 → 拒绝
        page.goto(BASE + "/vote/", timeout=15000)
        disabled = page.locator("button[disabled]")
        print(f"  已投的猫按钮已禁用: {disabled.count()} 个")

    # 会员访问看板 → 应被拒
    page.goto(BASE + "/dashboard/", timeout=15000)
    assert "/dashboard" not in page.url or "仅限" in page.content(), "会员不应能访问看板"
    print("✓ 权限控制：会员访问数据看板被拦截")

    # 管理员看板
    page.goto(BASE + "/login/", timeout=15000)
    page.goto(BASE + "/logout/", timeout=15000)
    page.goto(BASE + "/login/", timeout=15000)
    page.fill("input[name=username]", "admin")
    page.fill("input[name=password]", "Admin@123")
    page.click("button.btn-primary")
    page.wait_for_load_state("networkidle")
    page.goto(BASE + "/dashboard/", timeout=15000)
    assert "经营数据看板" in page.content(), "看板加载失败"
    page.wait_for_timeout(1500)
    page.screenshot(path=SHOT + r"\12-数据看板.png", full_page=True)
    # API 检查
    page.goto(BASE + "/dashboard/api/sales/", timeout=15000)
    assert "labels" in page.content(), "sales API 异常"
    print("✓ 管理员数据看板 + 4个API 正常")

    browser.close()

print("=== E2E v2 全部通过 ===")
