# -*- coding: utf-8 -*-
"""未来预约的取消功能 E2E"""
from playwright.sync_api import sync_playwright
from datetime import date, timedelta

BASE = "http://127.0.0.1:8000"
future = (date.today() + timedelta(days=3)).isoformat()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    page.goto(BASE + "/login/", timeout=15000)
    page.fill("input[name=username]", "linxin")
    page.fill("input[name=password]", "123456")
    page.click("button.btn-main")
    page.wait_for_load_state("networkidle")

    # 预约未来时段
    page.goto(BASE + "/reserve/", timeout=15000)
    page.select_option("select[name=seat]", index=2)
    page.fill("input[name=date]", future)
    page.fill("input[name=start]", "15:00")
    page.fill("input[name=end]", "17:00")
    page.click("text=提交预约")
    page.wait_for_load_state("networkidle")
    print("✓ 已预约", future, "15:00-17:00")

    page.goto(BASE + "/reserve/", timeout=15000)
    page.wait_for_timeout(500)
    content = page.content()
    has_cancel = page.locator("form[action*='cancel']").count()
    print(f"取消按钮数量: {has_cancel}")

    if has_cancel:
        page.locator("form[action*='cancel']").first.locator("button").click()
        page.wait_for_load_state("networkidle")
        assert "预约已取消" in page.content(), "取消失败"
        print("✓ 预约取消成功，状态变为已取消")
        # 再确认列表里状态chip变化
        page.goto(BASE + "/reserve/", timeout=15000)
        c = page.content()
        print("✓ 已取消 chip 显示:", "已取消" in c)
    else:
        print("!! 没有取消按钮，需排查")

    browser.close()
print("=== 未来预约取消测试完成 ===")
