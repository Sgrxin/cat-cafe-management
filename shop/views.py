"""前台视图（v2）：新增猫咪详情/搜索/公告/评价/签到/门店信息"""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import (
    UserProfile, Cat, Product, Seat, Reservation, Order, OrderItem,
    PointsLog, Gift, Redemption, VoteEvent, Vote,
    Announcement, Review, CheckInLog,
)
from .notify import send_order_email, sync_review_to_notion


def get_prof(user):
    """获取用户资料，不存在则自动创建会员档案"""
    prof, _ = UserProfile.objects.get_or_create(user=user, defaults={"role": "member"})
    return prof


def staff_required(view):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        prof = getattr(request.user, "userprofile", None)
        if request.user.is_superuser or (prof and prof.role in ("staff", "admin")):
            return view(request, *args, **kwargs)
        messages.error(request, "该页面仅限店员/管理员访问")
        return redirect("home")
    wrapper.__name__ = view.__name__
    return wrapper


# ==================== 基础页面 ====================

def home(request):
    cats = Cat.objects.filter(status="on").order_by("-reference_price")[:4]
    products = Product.objects.filter(is_available=True)[:8]
    announcements = Announcement.objects.filter(is_active=True)[:2]
    reviews = Review.objects.all()[:3]
    votes = (Vote.objects.values("cat__name", "cat__photo")
             .annotate(n=Count("id")).order_by("-n")[:3])
    today = timezone.localdate()

    # 首页预约模块：大厅/包厢各取4个工位，统计今日已确认预约数判断状态
    def zone_seats(zone):
        return (Seat.objects.filter(zone=zone, is_active=True)
                .annotate(today_n=Count("reservation", filter=Q(
                    reservation__date=today,
                    reservation__status__in=["pending", "confirmed"]))))

    hall_seats = zone_seats("hall")[:4]
    room_seats = zone_seats("room")[:4]

    user_upcoming = None
    if request.user.is_authenticated:
        user_upcoming = (Reservation.objects.filter(
            user=request.user, status="confirmed",
            date__gte=today).order_by("date", "start_time").first())

    # 店员工作台数据
    staff_pending_redeem = Redemption.objects.filter(status="pending").count()
    staff_today_orders = Order.objects.filter(created_at__date=today).count()

    return render(request, "shop/home.html", {
        "cats": cats, "products": products, "announcements": announcements,
        "reviews": reviews, "top_votes": votes,
        "hall_seats": hall_seats, "room_seats": room_seats,
        "user_upcoming": user_upcoming,
        "staff_pending_redeem": staff_pending_redeem,
        "staff_today_orders": staff_today_orders,
        "today": today,
    })


@staff_required
def staff_orders(request):
    """店员：全部订单管理"""
    orders = (Order.objects.select_related("user")
              .prefetch_related("items__product").order_by("-created_at")[:50])
    return render(request, "shop/staff_orders.html", {"orders": orders})


@staff_required
def staff_order_done(request, order_id):
    o = get_object_or_404(Order, id=order_id)
    if o.status == "paid":
        o.status = "finished"
        o.save()
        messages.success(request, f"订单 {o.order_no} 已核销完成")
    return redirect("staff_orders")


@staff_required
def staff_redemptions(request):
    """店员：兑换核销"""
    redemptions = (Redemption.objects.select_related("user", "gift")
                   .order_by("status", "-created_at")[:50])
    return render(request, "shop/staff_redemptions.html", {"redemptions": redemptions})


@staff_required
def staff_redemption_done(request, rid):
    r = get_object_or_404(Redemption, id=rid)
    if r.status == "pending":
        r.status = "done"
        r.save()
        messages.success(request, f"{r.user.username} 的「{r.gift.name}」已核销发放")
    return redirect("staff_redemptions")


def cat_list(request):
    qs = Cat.objects.filter(status="on")
    breed = request.GET.get("breed", "")
    max_price = request.GET.get("max_price", "")
    if breed:
        qs = qs.filter(breed=breed)
    if max_price.isdigit():
        qs = qs.filter(reference_price__lte=max_price)
    breeds = Cat.objects.filter(status="on").values_list("breed", flat=True).distinct()
    return render(request, "shop/cats.html", {
        "cats": qs, "breeds": breeds, "sel_breed": breed, "sel_price": max_price,
    })


def cat_detail(request, cat_id):
    cat = get_object_or_404(Cat, id=cat_id)
    age_months = None
    if cat.birth_date:
        delta = timezone.localdate() - cat.birth_date
        age_months = delta.days // 30
    related = Cat.objects.filter(breed=cat.breed, status="on").exclude(id=cat.id)[:3]
    votes = Vote.objects.filter(cat=cat).count()
    return render(request, "shop/cat_detail.html", {
        "cat": cat, "age_months": age_months, "related": related, "vote_count": votes,
    })


def menu(request):
    cat = request.GET.get("category", "")
    qs = Product.objects.filter(is_available=True)
    if cat:
        qs = qs.filter(category=cat)
    return render(request, "shop/menu.html", {"products": qs, "sel_cat": cat})


def search(request):
    """全局搜索：猫咪 + 商品"""
    q = request.GET.get("q", "").strip()
    cats = Product_result = None
    cats = Cat.objects.filter(status="on").filter(
        Q(name__icontains=q) | Q(breed__icontains=q) | Q(personality__icontains=q)) if q else []
    products = Product.objects.filter(is_available=True).filter(
        Q(name__icontains=q) | Q(description__icontains=q)) if q else []
    return render(request, "shop/search.html", {
        "q": q, "cats": cats, "products": products,
    })


def about(request):
    reviews = Review.objects.all()[:10]
    avg = Review.objects.aggregate(a=Sum("stars"), n=Count("id"))
    avg_stars = round(avg["a"] / avg["n"], 1) if avg["n"] else 5.0
    cats_count = Cat.objects.filter(status="on").count()
    return render(request, "shop/about.html", {
        "reviews": reviews, "avg_stars": avg_stars, "cats_count": cats_count,
    })


@login_required(login_url="login")
def review_post(request):
    if request.method == "POST":
        stars = int(request.POST.get("stars", 5))
        content = request.POST.get("content", "").strip()
        if 1 <= stars <= 5 and content:
            Review.objects.create(user=request.user, stars=stars, content=content)
            sync_review_to_notion(request.user.username, stars, content)
            messages.success(request, "评价成功，感谢反馈！")
        else:
            messages.error(request, "评价内容不能为空")
    return redirect("about")


def user_login(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        user = authenticate(request,
                            username=request.POST.get("username", ""),
                            password=request.POST.get("password", ""))
        if user:
            login(request, user)
            messages.success(request, f"欢迎回来，{user.username}！")
            return redirect(request.GET.get("next", "home"))
        messages.error(request, "用户名或密码错误")
    return render(request, "shop/login.html")


def user_register(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")
        phone = request.POST.get("phone", "").strip()
        if not username or not password:
            messages.error(request, "用户名和密码不能为空")
        elif len(password) < 6:
            messages.error(request, "密码至少6位")
        elif password != password2:
            messages.error(request, "两次密码不一致")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "用户名已存在")
        else:
            user = User.objects.create_user(username=username, password=password)
            UserProfile.objects.create(user=user, role="member", phone=phone)
            login(request, user)
            messages.success(request, "注册成功，已自动成为会员！")
            return redirect("home")
    return render(request, "shop/register.html")


def user_logout(request):
    logout(request)
    return redirect("home")


# ==================== 工位预约 ====================

@login_required(login_url="login")
def reserve(request):
    if request.method == "POST":
        try:
            seat = Seat.objects.get(id=request.POST.get("seat"), is_active=True)
            r_date = timezone.localdate().fromisoformat(request.POST.get("date", ""))
        except Exception:
            messages.error(request, "请填写完整的预约信息")
            return redirect("reserve")
        start = request.POST.get("start", "")
        end = request.POST.get("end", "")
        conflict = Reservation.objects.filter(
            seat=seat, date=r_date, status__in=["pending", "confirmed"],
        ).filter(Q(start_time__lt=end) & Q(end_time__gt=start)).exists()
        if start >= end:
            messages.error(request, "结束时间必须晚于开始时间")
        elif conflict:
            messages.error(request, "该工位在这个时间段已被预约，请换时段或换工位")
        else:
            Reservation.objects.create(
                user=request.user, seat=seat, date=r_date,
                start_time=start, end_time=end, status="confirmed",
                note=request.POST.get("note", "")[:200])
            messages.success(request, "预约成功！到店出示会员名即可入座")
            return redirect("reserve")
    seats = (Seat.objects.filter(is_active=True)
             .annotate(today_n=Count("reservation", filter=Q(
                 reservation__date=timezone.localdate(),
                 reservation__status__in=["pending", "confirmed"]))))
    my = Reservation.objects.filter(user=request.user).order_by("-created_at")[:10]
    return render(request, "shop/reserve.html", {
        "seats": seats, "my_reservations": my,
        "today": timezone.localdate().isoformat(),
    })


# ==================== 订单 ====================

@login_required(login_url="login")
def order_create(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)
    if product.stock < 1:
        messages.error(request, f"「{product.name}」库存不足")
        return redirect("menu")
    prof = get_prof(request.user)
    order = Order.objects.create(
        order_no=timezone.localtime().strftime("CAT%Y%m%d%H%M%S") + str(request.user.id),
        user=request.user, order_type="dine", status="paid",
        total_amount=product.price, paid_at=timezone.now())
    OrderItem.objects.create(order=order, product=product, quantity=1, unit_price=product.price)
    product.stock -= 1
    product.save()
    pts = int(product.price)
    prof.points += pts
    prof.vote_tickets += 1
    prof.save()
    PointsLog.objects.create(user=request.user, delta=pts, reason="consume")
    if request.user.email:
        send_order_email(request.user.email, order.order_no, product.name, product.price)
    messages.success(request, f"点单成功！已支付 ¥{product.price}，获得 {pts} 积分 + 1 张投票券")
    return redirect("my_orders")


@login_required(login_url="login")
def my_orders(request):
    orders = (Order.objects.filter(user=request.user)
              .prefetch_related("items__product").order_by("-created_at"))
    return render(request, "shop/my_orders.html", {"orders": orders})


# ==================== 会员中心 / 签到 / 积分兑换 ====================

@login_required(login_url="login")
def checkin(request):
    """每日签到 +5 积分（每天一次）"""
    prof = get_prof(request.user)
    today = timezone.localdate()
    already = CheckInLog.objects.filter(user=request.user, created_at__date=today).exists()
    if already:
        messages.info(request, "今天已经签到过啦，明天再来～")
    else:
        CheckInLog.objects.create(user=request.user)
        prof.points += 5
        prof.save()
        PointsLog.objects.create(user=request.user, delta=5, reason="admin")
        messages.success(request, "签到成功，积分 +5！")
    return redirect("me")


@login_required(login_url="login")
def member_center(request):
    prof = get_prof(request.user)
    orders = Order.objects.filter(user=request.user).order_by("-created_at")[:5]
    reservations = Reservation.objects.filter(user=request.user).order_by("-created_at")[:5]
    redemptions = Redemption.objects.filter(user=request.user).order_by("-created_at")[:5]
    logs = PointsLog.objects.filter(user=request.user).order_by("-created_at")[:5]
    checked = CheckInLog.objects.filter(
        user=request.user, created_at__date=timezone.localdate()).exists()
    checkin_days = CheckInLog.objects.filter(user=request.user).count()
    return render(request, "shop/me.html", {
        "prof": prof, "orders": orders, "reservations": reservations,
        "redemptions": redemptions, "logs": logs,
        "checked": checked, "checkin_days": checkin_days,
    })


@login_required(login_url="login")
def redeem_list(request):
    prof = get_prof(request.user)
    gifts = Gift.objects.filter(is_active=True)
    items = []
    for g in gifts:
        short = max(0, g.points_required - prof.points)
        items.append({"gift": g, "short": short, "affordable": short == 0 and g.stock > 0})
    return render(request, "shop/redeem.html", {
        "items": items, "points": prof.points,
    })


@login_required(login_url="login")
def redeem_do(request, gift_id):
    gift = get_object_or_404(Gift, id=gift_id, is_active=True)
    prof = get_prof(request.user)
    if prof.points < gift.points_required:
        messages.error(request, f"积分不足，还差 {gift.points_required - prof.points} 分")
    elif gift.stock < 1:
        messages.error(request, "该礼品已被兑完")
    else:
        prof.points -= gift.points_required
        gift.stock -= 1
        prof.save()
        gift.save()
        Redemption.objects.create(user=request.user, gift=gift)
        PointsLog.objects.create(user=request.user, delta=-gift.points_required, reason="redeem")
        messages.success(request, f"兑换成功：「{gift.name}」到店领取时出示会员名")
    return redirect("redeem")


# ==================== 互动投票 ====================

@login_required(login_url="login")
def vote_page(request):
    event = VoteEvent.objects.filter(is_active=True).first()
    votes = (Vote.objects.filter(event=event)
             .values("cat__name", "cat__breed")
             .annotate(n=Count("id")).order_by("-n"))
    my_cat_ids = list(Vote.objects.filter(event=event, user=request.user)
                      .values_list("cat_id", flat=True))
    cats = Cat.objects.filter(status="on")
    for c in cats:
        c.my_vote = c.id in my_cat_ids
        c.votes = next((v["n"] for v in votes if v["cat__name"] == c.name), 0)
    return render(request, "shop/vote.html", {
        "event": event, "cats": cats,
        "tickets": get_prof(request.user).vote_tickets,
        "ranked": votes,
    })


@login_required(login_url="login")
def vote_do(request, cat_id):
    event = VoteEvent.objects.filter(is_active=True).first()
    if not event:
        messages.error(request, "当前没有进行中的投票活动")
        return redirect("vote")
    prof = get_prof(request.user)
    if prof.vote_tickets < 1:
        messages.error(request, "投票券不足：每完成1笔消费赠送1张投票券")
        return redirect("vote")
    if Vote.objects.filter(event=event, user=request.user, cat_id=cat_id).exists():
        messages.error(request, "你已经给这只猫投过票啦，换只猫试试")
        return redirect("vote")
    prof.vote_tickets -= 1
    prof.save()
    Vote.objects.create(event=event, user=request.user, cat_id=cat_id)
    messages.success(request, "投票成功，感谢为猫王打Call！")
    return redirect("vote")


# ==================== 数据看板 ====================

@staff_required
def dashboard(request):
    return render(request, "shop/dashboard.html")


@staff_required
def dashboard_data(request, name):
    if name == "sales":
        start = timezone.localdate() - timezone.timedelta(days=13)
        qs = (Order.objects.filter(status__in=["paid", "finished"], paid_at__gte=start)
              .annotate(d=TruncDate("paid_at"))
              .values("d").annotate(total=Sum("total_amount")).order_by("d"))
        labels = [(start + timezone.timedelta(days=i)).isoformat() for i in range(14)]
        data = {v["d"].isoformat(): float(v["total"] or 0) for v in qs}
        return JsonResponse({"labels": labels, "values": [data.get(l, 0) for l in labels]})
    if name == "top_products":
        qs = (OrderItem.objects.values("product__name")
              .annotate(n=Sum("quantity")).order_by("-n")[:8])
        return JsonResponse({"labels": [v["product__name"] for v in qs],
                             "values": [v["n"] for v in qs]})
    if name == "cat_votes":
        qs = (Vote.objects.values("cat__name").annotate(n=Count("id")).order_by("-n"))
        return JsonResponse({"labels": [v["cat__name"] for v in qs],
                             "values": [v["n"] for v in qs]})
    if name == "seat_usage":
        qs = (Reservation.objects.values("seat__name")
              .annotate(n=Count("id")).order_by("-n")[:10])
        return JsonResponse({"labels": [v["seat__name"] for v in qs],
                             "values": [v["n"] for v in qs]})
    return JsonResponse({"error": "unknown"}, status=400)
