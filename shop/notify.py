# -*- coding: utf-8 -*-
"""外部服务通知钩子：Gmail 邮件 / Notion 同步
全部通过环境变量开启，未配置时静默跳过，不影响主流程。"""
import json
import os
import urllib.request


def _email_confirmed():
    return bool(os.environ.get("EMAIL_HOST_USER") and os.environ.get("EMAIL_HOST_PASSWORD"))


def send_order_email(to_email, order_no, product_name, amount):
    """点单成功后发送确认邮件（Gmail SMTP）。未配置凭证时跳过。"""
    if not to_email or not _email_confirmed():
        return False
    from django.conf import settings
    from django.core.mail import send_mail
    try:
        send_mail(
            subject=f"【喵屋猫咖】点单成功 {order_no}",
            message=f"您已成功点单：{product_name}（¥{amount}）。\n到店出示订单号 {order_no} 取餐。",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[to_email],
            fail_silently=True,
        )
        return True
    except Exception:
        return False


def sync_review_to_notion(username, stars, content):
    """把评价同步到 Notion 数据库。未配置令牌时跳过。"""
    token = os.environ.get("NOTION_TOKEN", "")
    db_id = os.environ.get("NOTION_REVIEW_DB", "")
    if not (token and db_id):
        return False
    payload = json.dumps({
        "parent": {"database_id": db_id},
        "properties": {
            "用户": {"title": [{"text": {"content": username}}]},
            "评分": {"number": stars},
            "内容": {"rich_text": [{"text": {"content": content[:300]}}]},
        },
    }).encode()
    req = urllib.request.Request(
        "https://api.notion.com/v1/pages", data=payload,
        headers={"Authorization": f"Bearer {token}",
                 "Notion-Version": "2022-06-28",
                 "Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception:
        return False
