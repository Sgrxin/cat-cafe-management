# -*- coding: utf-8 -*-
"""精确点击提交按钮 + DB验证"""
import sqlite3
from playwright.sync_api import sync_playwright
from datetime import date, timedelta

DB = r"C:\Users\lx\Desktop\agent\agent\毕设\db.sqlite3"
BASE = "http://127.0.0.1:8000"
future = (date.today() + timedelta(days=3)).isoformat()


def db_count():
    con = sqlite3.connect(DB)
    n = con.execute("SELECT COUNT(*) FROM shop_reservation").fetchone()[0]
    con.close()
    return n


print("提交前预约数:", db_count())

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto(BASE + "/login/", timeout=15000)
    page.fill("input[name=username]", "linxin")
    page.fill("input[name=password]", "123456")
    page.get_by_role("button", name="登录").click()
    page.wait_for_load_state("networkidle")

    page.goto(BASE + "/reserve/", timeout=15000)
    page.select_option("select[name=seat]", index=2)
    page.fill("input[name=date]", future)
    page.fill("input[name=start]", "15:00")
    page.fill("input[name=end]", "17:00")
    page.get_by_role("button", name="提交预约").click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(500)
    c = page.content()
    print("页面反馈:", "预约成功" if "预约成功" in c else ("已被预约" if "已被预约" in c else "无提示"))
    browser.close()

print("提交后预约数:", db_count())
