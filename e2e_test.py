# -*- coding: utf-8 -*-
"""毕设系统 E2E 测试 + 论文截图采集"""
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8000"
SHOT = r"C:\Users\lx\Desktop\agent\agent\毕设\截图"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    # 1. 首页
    page.goto(BASE + "/", timeout=15000)
    page.wait_for_load_state("networkidle")
    assert "喵屋猫咖" in page.content(), "首页异常"
    page.screenshot(path=SHOT + r"\01-首页.png", full_page=True)
    print("✓ 首页正常，截图已存")

    # 2. 猫咪档案
    page.goto(BASE + "/cats/", timeout=15000)
    assert "布偶" in page.content() and "橘猫" in page.content()
    page.screenshot(path=SHOT + r"\02-猫咪档案.png", full_page=True)
    print("✓ 猫咪档案正常（含品种筛选）")

    # 3. 菜单
    page.goto(BASE + "/menu/", timeout=15000)
    assert "猫爪拿铁" in page.content() and "冻干" in page.content()
    page.screenshot(path=SHOT + r"\03-商品菜单.png", full_page=True)
    print("✓ 商品菜单正常")

    # 4. 未登录访问预约 → 跳登录
    page.goto(BASE + "/reserve/", timeout=15000)
    assert "/login/" in page.url, "未登录应跳转登录"
    print("✓ 权限控制：未登录访问预约 → 跳转登录页")
    page.screenshot(path=SHOT + r"\04-登录页.png", full_page=True)

    # 5. 登录 linxin
    page.fill("input[name=username]", "linxin")
    page.fill("input[name=password]", "123456")
    page.click("button.btn-primary")
    page.wait_for_load_state("networkidle")
    assert "预约工位" in page.content() or "欢迎回来" in page.content(), "登录失败"
    print("✓ linxin 登录成功，自动跳回预约页")

    # 6. 提交预约
    page.select_option("select[name=seat]", index=1)
    page.fill("input[name=start]", "10:00")
    page.fill("input[name=end]", "12:00")
    page.click("text=提交预约")
    page.wait_for_load_state("networkidle")
    assert "预约成功" in page.content(), "预约失败"
    page.screenshot(path=SHOT + r"\05-预约成功.png", full_page=True)
    print("✓ 预约成功")

    # 7. 再提交同一时段 → 冲突
    page.goto(BASE + "/reserve/", timeout=15000)
    page.select_option("select[name=seat]", index=1)
    page.fill("input[name=start]", "11:00")
    page.fill("input[name=end]", "13:00")
    page.click("text=提交预约")
    page.wait_for_load_state("networkidle")
    assert "已被预约" in page.content(), "冲突检测未生效"
    page.screenshot(path=SHOT + r"\06-预约冲突提示.png", full_page=True)
    print("✓ 时间冲突检测生效（11:00-13:00 与 10:00-12:00 重叠被拒）")

    browser.close()

print("=== E2E 全部通过，截图已存毕设/截图文件夹 ===")
