"""
猫咖门店管理系统 - 数据模型
模块：会员/猫咪档案/商品菜单/工位预约/订单/积分/互动投票
"""
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """用户扩展：角色 + 会员钱包"""
    ROLE_CHOICES = [
        ("member", "会员"),
        ("staff", "店员"),
        ("admin", "管理员"),
    ]
    user = models.OneToOneField(User, verbose_name="关联用户", on_delete=models.CASCADE)
    role = models.CharField("角色", max_length=10, choices=ROLE_CHOICES, default="member")
    phone = models.CharField("手机号", max_length=11, blank=True)
    birthday = models.DateField("生日", null=True, blank=True)
    balance = models.DecimalField("储值余额", max_digits=10, decimal_places=2, default=0)
    points = models.IntegerField("积分", default=0)
    vote_tickets = models.IntegerField("投票券", default=0)
    joined_at = models.DateTimeField("入会时间", auto_now_add=True)

    class Meta:
        verbose_name = "用户资料"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username}({self.get_role_display()})"

    @property
    def level(self):
        """会员等级：按当前积分自动升级"""
        if self.points >= 800:
            return "钻石铲屎官"
        if self.points >= 300:
            return "金牌猫奴"
        if self.points >= 100:
            return "银牌猫奴"
        return "萌新铲屎官"

    @property
    def level_icon(self):
        return {
            "钻石铲屎官": "bi-gem",
            "金牌猫奴": "bi-trophy",
            "银牌猫奴": "bi-medal",
            "萌新铲屎官": "bi-heart",
        }.get(self.level, "bi-heart")


class Announcement(models.Model):
    """门店公告"""
    title = models.CharField("公告标题", max_length=100)
    content = models.TextField("公告内容")
    created_at = models.DateTimeField("发布时间", auto_now_add=True)
    is_active = models.BooleanField("显示中", default=True)

    class Meta:
        verbose_name = "门店公告"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Review(models.Model):
    """门店评价"""
    user = models.ForeignKey(User, verbose_name="评价用户", on_delete=models.CASCADE)
    stars = models.IntegerField("评分", choices=[(i, "⭐" * i) for i in range(1, 6)])
    content = models.TextField("评价内容")
    created_at = models.DateTimeField("评价时间", auto_now_add=True)

    class Meta:
        verbose_name = "门店评价"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} {self.stars}星"


class CheckInLog(models.Model):
    """每日签到（+5积分）"""
    user = models.ForeignKey(User, verbose_name="用户", on_delete=models.CASCADE)
    created_at = models.DateTimeField("签到时间", auto_now_add=True)

    class Meta:
        verbose_name = "签到记录"
        verbose_name_plural = verbose_name


class Cat(models.Model):
    """猫咪档案"""
    STATUS_CHOICES = [
        ("on", "在岗营业"),
        ("rest", "休息中"),
        ("retired", "已退休"),
    ]
    GENDER_CHOICES = [("m", "弟弟"), ("f", "妹妹")]
    name = models.CharField("名字", max_length=30)
    breed = models.CharField("品种", max_length=30)
    gender = models.CharField("性别", max_length=1, choices=GENDER_CHOICES)
    birth_date = models.DateField("出生日期", null=True, blank=True)
    color = models.CharField("毛色", max_length=30, blank=True)
    personality = models.CharField("性格", max_length=100, blank=True)
    reference_price = models.DecimalField(
        "参考身价", max_digits=10, decimal_places=2, default=0,
        help_text="品种参考身价，顾客可按预算选择互动的猫")
    photo = models.ImageField("照片", upload_to="cats/", blank=True)
    health_notes = models.TextField("健康备注", blank=True)
    vaccine_due_date = models.DateField("疫苗到期日", null=True, blank=True)
    status = models.CharField("状态", max_length=10, choices=STATUS_CHOICES, default="on")
    joined_at = models.DateTimeField("入职时间", auto_now_add=True)

    class Meta:
        verbose_name = "猫咪档案"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Product(models.Model):
    """商品菜单"""
    CATEGORY_CHOICES = [
        ("drink", "饮品"),
        ("dessert", "甜品"),
        ("snack", "猫零食"),
        ("goods", "周边"),
    ]
    name = models.CharField("名称", max_length=50)
    category = models.CharField("分类", max_length=10, choices=CATEGORY_CHOICES)
    price = models.DecimalField("售价", max_digits=8, decimal_places=2)
    stock = models.IntegerField("库存", default=99)
    description = models.TextField("描述", blank=True)
    photo = models.ImageField("图片", upload_to="products/", blank=True)
    is_available = models.BooleanField("上架中", default=True)

    class Meta:
        verbose_name = "商品菜单"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name} ¥{self.price}"


class Seat(models.Model):
    """猫咖工位"""
    ZONE_CHOICES = [
        ("window", "窗边区"),
        ("bar", "吧台区"),
        ("hall", "大厅区"),
        ("room", "猫屋包间"),
    ]
    name = models.CharField("工位名", max_length=30)
    zone = models.CharField("区域", max_length=10, choices=ZONE_CHOICES)
    capacity = models.IntegerField("容纳人数", default=2)
    price_per_hour = models.DecimalField("小时单价", max_digits=8, decimal_places=2, default=30)
    photo = models.ImageField("环境参考图", upload_to="seats/", blank=True)
    is_active = models.BooleanField("启用中", default=True)

    class Meta:
        verbose_name = "工位"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Reservation(models.Model):
    """工位预约"""
    STATUS_CHOICES = [
        ("pending", "待确认"),
        ("confirmed", "已确认"),
        ("finished", "已完成"),
        ("canceled", "已取消"),
    ]
    user = models.ForeignKey(User, verbose_name="预约用户", on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, verbose_name="工位", on_delete=models.CASCADE)
    date = models.DateField("预约日期")
    start_time = models.TimeField("开始时间")
    end_time = models.TimeField("结束时间")
    status = models.CharField("状态", max_length=10, choices=STATUS_CHOICES, default="pending")
    note = models.CharField("备注", max_length=200, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "工位预约"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username} {self.seat} {self.date}"


class Order(models.Model):
    """订单：到店点单 / 预约关联"""
    TYPE_CHOICES = [("dine", "到店消费"), ("reserve", "预约消费")]
    STATUS_CHOICES = [
        ("unpaid", "待支付"),
        ("paid", "已支付"),
        ("finished", "已完成"),
        ("canceled", "已取消"),
    ]
    order_no = models.CharField("订单号", max_length=32, unique=True)
    user = models.ForeignKey(User, verbose_name="下单用户", on_delete=models.CASCADE, null=True, blank=True)
    order_type = models.CharField("订单类型", max_length=10, choices=TYPE_CHOICES, default="dine")
    status = models.CharField("状态", max_length=10, choices=STATUS_CHOICES, default="unpaid")
    total_amount = models.DecimalField("订单金额", max_digits=10, decimal_places=2, default=0)
    reservation = models.ForeignKey(Reservation, verbose_name="关联预约", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField("下单时间", auto_now_add=True)
    paid_at = models.DateTimeField("支付时间", null=True, blank=True)

    class Meta:
        verbose_name = "订单"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.order_no


class OrderItem(models.Model):
    """订单明细"""
    order = models.ForeignKey(Order, verbose_name="订单", on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, verbose_name="商品", on_delete=models.CASCADE)
    quantity = models.IntegerField("数量", default=1)
    unit_price = models.DecimalField("成交单价", max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = "订单明细"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.order.order_no} x {self.product.name}"


class PointsLog(models.Model):
    """积分流水"""
    REASON_CHOICES = [
        ("consume", "消费获得"),
        ("redeem", "积分兑换"),
        ("refund", "退款扣回"),
        ("admin", "管理员调整"),
    ]
    user = models.ForeignKey(User, verbose_name="用户", on_delete=models.CASCADE)
    delta = models.IntegerField("积分变动")
    reason = models.CharField("原因", max_length=10, choices=REASON_CHOICES)
    created_at = models.DateTimeField("时间", auto_now_add=True)

    class Meta:
        verbose_name = "积分流水"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username} {self.delta:+d}"


class Gift(models.Model):
    """积分兑换礼品"""
    name = models.CharField("礼品名", max_length=50)
    points_required = models.IntegerField("所需积分")
    stock = models.IntegerField("库存", default=10)
    is_active = models.BooleanField("上架中", default=True)

    class Meta:
        verbose_name = "兑换礼品"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Redemption(models.Model):
    """兑换记录"""
    STATUS_CHOICES = [("pending", "待发放"), ("done", "已发放")]
    user = models.ForeignKey(User, verbose_name="用户", on_delete=models.CASCADE)
    gift = models.ForeignKey(Gift, verbose_name="礼品", on_delete=models.CASCADE)
    status = models.CharField("状态", max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField("兑换时间", auto_now_add=True)

    class Meta:
        verbose_name = "兑换记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username} 兑换 {self.gift.name}"


class VoteEvent(models.Model):
    """投票活动（选猫王）"""
    title = models.CharField("活动标题", max_length=100)
    is_active = models.BooleanField("进行中", default=True)
    start_at = models.DateTimeField("开始时间", null=True, blank=True)
    end_at = models.DateTimeField("结束时间", null=True, blank=True)

    class Meta:
        verbose_name = "投票活动"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Vote(models.Model):
    """投票记录（消耗投票券）"""
    event = models.ForeignKey(VoteEvent, verbose_name="活动", on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name="投票用户", on_delete=models.CASCADE)
    cat = models.ForeignKey(Cat, verbose_name="投给的猫", on_delete=models.CASCADE)
    created_at = models.DateTimeField("投票时间", auto_now_add=True)

    class Meta:
        verbose_name = "投票记录"
        verbose_name_plural = verbose_name
        unique_together = [("event", "user", "cat")]

    def __str__(self):
        return f"{self.user.username} → {self.cat.name}"
