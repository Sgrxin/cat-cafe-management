# -*- coding: utf-8 -*-
"""彻底排查: 提交预约 → 直接读DB文件验证"""
import sqlite3
from playwright.sync_api import sync_playwright
from datetime import date, timedelta

DB = r"C:\Users\lx\Desktop\agent\agent\毕设\db.sqlite3"
BASE = "http://127.0.0.1:8000"
future = (date.today() + timedelta(days=3)).isoformat()


def db_reservations():
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT id, user_id, date, start_time, end_time, status FROM shop_reservation ORDER BY id").fetchall()
    con.close()
    return rows


print("=== 提交前DB ===")
for r in db_reservations():
    print(" ", r)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto(BASE + "/login/", timeout=15000)
    page.fill("input[name=username]", "linxin")
    page.fill("input[name=password]", "123456")
    page.click("button.btn-main")
    page.wait_for_load_state("networkidle")

    page.goto(BASE + "/reserve/", timeout=15000)
    page.select_option("select[name=seat]", index=2)
    page.fill("input[name=date]", future)
    page.fill("input[name=start]", "15:00")
    page.fill("input[name=end]", "17:00")

    # 监听网络响应
    responses = []
    page.on("response", lambda resp: responses.append((resp.status, resp.url)))
    page.click("text=提交预约")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(800)

    print("=== 提交后的网络请求 ===")
    for st, u in responses[-5:]:
        print(f"  {st} {u}")

    content = page.content()
    if "预约成功" in content:
        print("页面提示: 预约成功")
    elif "已被预约" in content:
        print("页面提示: 时段冲突")
    elif "不能" in content or "错误" in content:
        i = content.find("st-")
        print("提示区:", content[i:i+200] if i >= 0 else content[-200:])
    else:
        print("页面无提示, 尾部:", content[-200:])

    print("=== 提交后DB ===")
    for r in db_reservations():
        print(" ", r)

    browser.close()
