from django.test import TestCase
from django.contrib.auth.models import User

from .models import Cat, Product, UserProfile, get_prof


class PageTests(TestCase):
    """前台页面可用性"""

    def test_home(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "喵屋猫咖")

    def test_cats(self):
        Cat.objects.create(name="布丁", breed="英短蓝猫", gender="m")
        r = self.client.get("/cats/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "布丁")

    def test_menu(self):
        Product.objects.create(name="招牌猫爪拿铁", category="drink", price=28)
        r = self.client.get("/menu/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "招牌猫爪拿铁")

    def test_cat_detail(self):
        c = Cat.objects.create(name="布丁", breed="英短蓝猫", gender="m")
        r = self.client.get(f"/cats/{c.id}/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "健康档案")


class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_creates_member(self):
        r = self.client.post("/register/", {
            "username": "test01", "password": "test123456",
            "password2": "test123456", "phone": "13800000000",
        })
        self.assertRedirects(r, "/", fetch_redirect_response=False)
        prof = UserProfile.objects.get(user__username="test01")
        self.assertEqual(prof.role, "member")

    def test_reserve_requires_login(self):
        r = self.client.get("/reserve/")
        self.assertEqual(r.status_code, 302)


class OrderTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("u1", password="pass123456")
        get_prof(self.user)
        self.cat = Product.objects.create(
            name="招牌猫爪拿铁", category="drink", price=28)
        self.client.login(username="u1", password="pass123456")

    def test_order_creates_points_and_ticket(self):
        prof_before = UserProfile.objects.get(user=self.user)
        points_before = prof_before.points
        tickets_before = prof_before.vote_tickets
        r = self.client.post(f"/menu/order/{self.cat.id}/")
        self.assertEqual(r.status_code, 302)
        prof = UserProfile.objects.get(user=self.user)
        self.assertEqual(prof.points, points_before + 28)
        self.assertEqual(prof.vote_tickets, tickets_before + 1)
        order = self.user.order_set.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.total_amount, 28)
