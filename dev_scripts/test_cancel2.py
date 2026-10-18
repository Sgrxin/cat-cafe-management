# -*- coding: utf-8 -*-
"""取消功能精确验证"""
import sqlite3
from playwright.sync_api import sync_playwright

DB = r"C:\Users\lx\Desktop\agent\agent\毕设\db.sqlite3"
BASE = "http://127.0.0.1:8000"


def db_count():
    con = sqlite3.connect(DB)
    n = con.execute("SELECT COUNT(*) FROM shop_reservation").fetchone()[0]
    con.close()
    return n


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto(BASE + "/login/", timeout=15000)
    page.fill("input[name=username]", "linxin")
    page.fill("input[name=password]", "123456")
    page.get_by_role("button", name="登录").click()
    page.wait_for_load_state("networkidle")

    page.goto(BASE + "/reserve/", timeout=15000)
    page.wait_for_timeout(500)
    before = db_count()
    cancel_forms = page.locator("form[action*='cancel']").count()
    print("取消表单数:", cancel_forms)
    if cancel_forms > 0:
        page.locator("form[action*='cancel']").first.locator("button").click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(500)
        after = db_count()
        print(f"取消执行: 预约数 {before} → {after}")
        assert after == before - 1, "取消后预约数应减1"
        print("✓ 预约取消功能验证通过")
    else:
        print("○ 无可取消预约")

    browser.close()
print("=== 完成 ===")
