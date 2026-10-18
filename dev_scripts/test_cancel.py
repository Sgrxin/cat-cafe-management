# -*- coding: utf-8 -*-
"""预约取消 E2E 测试"""
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8000"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto(BASE + "/login/", timeout=15000)
    page.fill("input[name=username]", "linxin")
    page.fill("input[name=password]", "123456")
    page.click("button.btn-main")
    page.wait_for_load_state("networkidle")

    # 统计确认状态预约数
    page.goto(BASE + "/reserve/", timeout=15000)
    before = page.locator(".chip-ok").count()
    print("当前已确认预约:", before, "条")

    # 取消第一条
    forms = page.locator("form[action*='cancel']")
    if forms.count() > 0:
        forms.first.locator("button").click()
        page.wait_for_load_state("networkidle")
        assert "预约已取消" in page.content(), "取消失败"
        after = page.locator(".chip-ok").count()
        print(f"✓ 取消成功：已确认 {before} → {after} 条")
    else:
        print("○ 没有可取消的预约")

    # 帆布袋图片验证
    page.goto(BASE + "/menu/", timeout=15000)
    page.wait_for_timeout(800)
    imgs = page.locator("img").all()
    broken = sum(1 for i in imgs if i.evaluate("e => e.naturalWidth") == 0)
    print(f"菜单页图片 {len(imgs)} 张, 破图 {broken} 张")

    browser.close()
print("=== 取消功能测试完成 ===")
