# -*- coding: utf-8 -*-
"""演示数据种子脚本 v2(丰富版): python seed_data.py"""
import os
import django
from datetime import date, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from shop.models import (
    UserProfile, Cat, Product, Seat, Reservation, Order, OrderItem,
    PointsLog, Gift, VoteEvent, Vote,
)

# ---------- 管理员 ----------
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@catcafe.local", "Admin@123")
    print("[+] admin / Admin@123")

# ---------- 会员 ----------
members = []
for name, phone in [("linxin", "13800000001"),
                    ("wenshengquan", "13800000002"),
                    ("lvchaohang", "13800000003")]:
    u, created = User.objects.get_or_create(username=name, defaults={"email": name + "@catcafe.local"})
    if created:
        u.set_password("123456")
        u.save()
    UserProfile.objects.get_or_create(user=u, defaults={
        "role": "member", "phone": phone, "balance": 200, "points": 300, "vote_tickets": 3})
    members.append(u)
print(f"[+] 会员 {UserProfile.objects.count()} 人")

# ---------- 猫咪档案（22只，全部性格温顺亲人，身价从亲民到名贵） ----------
# (名字, 品种, 性别, 毛色, 参考身价, 性格描述)
CATS = [
    ("橘座",   "橘猫(中华田园)", "m", "橘白",   300,  "干饭王，性格稳如老狗，随便撸不生气"),
    ("煤球",   "玄猫(中华田园)", "m", "纯黑",   200,  "高冷绅士，熟悉后是个粘人精"),
    ("奶牛",   "奶牛猫",         "m", "黑白",   150,  "猫中哈士奇，整活担当，亲人爱蹭人"),
    ("三花妹", "三花猫",         "f", "三花",   400,  "温柔姐姐，最会照顾小猫"),
    ("狸奴",   "狸花猫",         "m", "棕虎斑", 100,  "中华神捕，皮实聪明，会握手"),
    ("大白",   "田园白猫",       "f", "纯白",   350,  "乖乖女， blue眼睛，安静陪坐型"),
    ("布丁",   "英短蓝猫",       "m", "蓝灰",   1800, "圆脸干饭王，摸摸就呼噜"),
    ("蓝胖",   "英短蓝猫",       "m", "蓝灰",   2000, "五短身材，趴手心一绝"),
    ("汤圆",   "英短蓝白",       "f", "蓝白",   2200, "软糯小汤圆，爱踩奶"),
    ("金币",   "英短金渐层",     "f", "金色",   3500, "富家千金，毛量惊人"),
    ("银耳",   "英短银渐层",     "f", "银白",   2800, "仙女本仙，拍照最上镜"),
    ("墨墨",   "美短标斑",       "m", "银虎斑", 1500, "运动健将，逗猫棒杀手"),
    ("起司",   "美短起司",       "m", "红虎斑", 1600, "表情包制造机，脾气超好"),
    ("雪球",   "布偶猫",         "f", "海豹双色", 8800, "粘人小仙女，抱抱就睡"),
    ("年糕",   "布偶猫",         "f", "蓝双色", 9800, "仙气飘飘，随便抱随便亲"),
    ("阿咪",   "暹罗猫",         "m", "重点色", 1500, "话痨社交王，会串门问候每位客人"),
    ("将军",   "缅因猫",         "m", "棕虎斑", 9800, "10斤温柔巨人，气场全开脾气超好"),
    ("珍珠",   "金吉拉",         "f", "银白",   5200, "贵族小姐，毛茸茸抱枕本体"),
    ("加菲",   "异国短毛猫",     "m", "红白",   6800, "憨憨本憨，睡觉大赛冠军"),
    ("糯米",   "英短银点",       "f", "银点",   8800, "钻石眼小公主，气质拉满"),
    ("短腿",   "曼基康矮脚猫",   "m", "蓝白",   7800, "小短腿飞奔，逗趣可爱"),
    ("土豆",   "斯芬克斯无毛猫", "m", "肉色",   9800, "暖手宝本猫，怕冷爱贴人"),
]
Cat.objects.all().delete()
for name, breed, gender, color, price, personality in CATS:
    Cat.objects.create(
        name=name, breed=breed, gender=gender, color=color,
        birth_date=date(2024, 1, 1) + timedelta(days=len(name) * 11),
        personality=personality, reference_price=price,
        vaccine_due_date=date.today() + timedelta(days=45),
        health_notes="已绝育、已接种三针疫苗，定期驱虫，性格温顺亲人，适合新手互动",
        status="on")
print(f"[+] 猫咪 {Cat.objects.count()} 只(品种{Cat.objects.values('breed').distinct().count()}种)")

# ---------- 工位（大厅12 + 包间8） ----------
Seat.objects.all().delete()
for i in range(1, 13):
    Seat.objects.create(
        name=f"大厅{i:02d}号", zone="hall",
        capacity=4 if i % 3 == 0 else 2,
        price_per_hour=[20, 25, 28, 30, 32, 35][i % 6])
ROOMS = [("樱花房", 4, 68), ("星空房", 4, 78), ("森林房", 6, 88), ("云朵房", 4, 78),
         ("奶油房", 6, 98), ("喵喵房", 8, 108), ("暖阳房", 4, 88), ("月光房", 8, 128)]
for name, cap, price in ROOMS:
    Seat.objects.create(name=name, zone="room", capacity=cap, price_per_hour=price)
print(f"[+] 工位 {Seat.objects.count()} 个（大厅{Seat.objects.filter(zone='hall').count()} + 包间{Seat.objects.filter(zone='room').count()}）")

# ---------- 商品菜单（31项：饮品/甜品小吃/猫粮猫用/周边） ----------
Product.objects.all().delete()
MENU = [
    # 饮品
    ("招牌猫爪拿铁", "drink", 28), ("猫爪奶茶(珍珠)", "drink", 16), ("黑糖鹿丸奶茶", "drink", 18),
    ("经典美式", "drink", 18), ("澳白", "drink", 26), ("卡布奇诺", "drink", 24),
    ("焦糖玛奇朵", "drink", 27), ("抹茶拿铁", "drink", 25), ("蜜桃乌龙茶", "drink", 17),
    ("柠檬气泡水", "drink", 15), ("热可可", "drink", 20),
    # 甜品小吃
    ("巴斯克蛋糕", "dessert", 30), ("提拉米苏", "dessert", 32), ("抹茶千层", "dessert", 28),
    ("葡式蛋挞(2只)", "dessert", 12), ("黄油曲奇", "dessert", 15), ("黄金薯条", "dessert", 12),
    ("鸡米花", "dessert", 14), ("金枪鱼三明治", "dessert", 22),
    # 猫粮猫用（喂猫区）
    ("宠物冻干鸡肉(喂猫装)", "catfood", 20), ("猫条3支装(喂猫)", "catfood", 15),
    ("猫粮试吃装", "catfood", 10), ("香酥小鱼干", "catfood", 12),
    ("猫薄荷玩具", "catfood", 8), ("主食罐头", "catfood", 25),
    # 周边
    ("猫爪钥匙扣", "goods", 25), ("猫咖帆布袋", "goods", 39), ("猫爪马克杯", "goods", 45),
    ("猫咪贴纸包", "goods", 8), ("猫咖明信片", "goods", 6),
]
CATEGORY_CN = {"drink": "饮品", "dessert": "甜品小吃", "catfood": "猫粮猫用", "goods": "周边文创"}
for name, cat, price in MENU:
    Product.objects.create(name=name, category=cat, price=price,
                           description=CATEGORY_CN[cat])
print(f"[+] 商品 {Product.objects.count()} 项（饮品{Product.objects.filter(category='drink').count()} 甜品小吃{Product.objects.filter(category='dessert').count()} 猫粮猫用{Product.objects.filter(category='catfood').count()} 周边{Product.objects.filter(category='goods').count()}）")

# ---------- 会员下单示例 ----------
Order.objects.all().delete()
if members:
    o = Order.objects.create(order_no="CAT20261016001", user=members[0],
                             order_type="dine", status="paid", total_amount=58,
                             paid_at=timezone.now())
    p1 = Product.objects.get(name="招牌猫爪拿铁")
    p2 = Product.objects.get(name="巴斯克蛋糕")
    OrderItem.objects.create(order=o, product=p1, quantity=1, unit_price=p1.price)
    OrderItem.objects.create(order=o, product=p2, quantity=1, unit_price=p2.price)
    PointsLog.objects.get_or_create(user=members[0], delta=58, reason="consume")
    Reservation.objects.get_or_create(
        user=members[0], seat=Seat.objects.filter(zone="room").first(),
        defaults={"date": date.today() + timedelta(days=1),
                  "start_time": "14:00", "end_time": "16:00", "status": "confirmed"})
    print("[+] 示例订单+预约已建")

# ---------- 积分兑换礼品 ----------
for name, pts in [("猫咪马克杯", 300), ("撸猫体验券", 150), ("猫条一包", 80), ("猫咖帆布袋", 500)]:
    Gift.objects.get_or_create(name=name, defaults={"points_required": pts, "stock": 10})
print(f"[+] 兑换礼品 {Gift.objects.count()} 个")

# ---------- 猫王投票 ----------
if not VoteEvent.objects.exists():
    ev = VoteEvent.objects.create(title="2026年度猫王评选", is_active=True)
    Vote.objects.get_or_create(event=ev, user=members[1], cat=Cat.objects.get(name="橘座"))
    Vote.objects.get_or_create(event=ev, user=members[2], cat=Cat.objects.get(name="将军"))
    print("[+] 投票活动「2026年度猫王评选」+ 2票")

print("=== 演示数据 v2 就绪 ===")
