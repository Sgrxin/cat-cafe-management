# -*- coding: utf-8 -*-
"""未来预约提交+结果验证（页面提示+数据库双确认）"""
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

    page.goto(BASE + "/reserve/", timeout=15000)
    page.select_option("select[name=seat]", label="大厅03号（大厅区 · 2人 · ¥25/时）")
    page.fill("input[name=date]", future)
    page.fill("input[name=start]", "15:00")
    page.fill("input[name=end]", "17:00")
    page.click("text=提交预约")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(500)
    content = page.content()
    if "预约成功" in content:
        print("✓ 预约成功提示出现")
    elif "已被预约" in content:
        print("✗ 冲突提示")
    else:
        # 打印提示区域内容
        import re
        m = re.search(r"st-(?:ok|warn|)[^>]*>([^<]{0,80})", content)
        print("提示区:", m.group(1) if m else content[-300:])
    browser.close()
