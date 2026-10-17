from django.contrib import admin
from .models import (
    UserProfile, Cat, Product, Seat, Reservation,
    Order, OrderItem, PointsLog, Gift, Redemption, VoteEvent, Vote,
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "phone", "balance", "points", "vote_tickets", "joined_at")
    search_fields = ("user__username", "phone")
    list_filter = ("role",)


@admin.register(Cat)
class CatAdmin(admin.ModelAdmin):
    list_display = ("name", "breed", "gender", "reference_price", "birth_date", "vaccine_due_date", "status")
    list_filter = ("status", "gender", "breed")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "is_available")
    list_filter = ("category", "is_available")


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("name", "zone", "capacity", "price_per_hour", "is_active")
    list_filter = ("zone", "is_active")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("user", "seat", "date", "start_time", "end_time", "status", "created_at")
    list_filter = ("status", "date")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_no", "user", "order_type", "status", "total_amount", "created_at")
    list_filter = ("status", "order_type")
    inlines = [OrderItemInline]


@admin.register(PointsLog)
class PointsLogAdmin(admin.ModelAdmin):
    list_display = ("user", "delta", "reason", "created_at")
    list_filter = ("reason",)


@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    list_display = ("name", "points_required", "stock", "is_active")


@admin.register(Redemption)
class RedemptionAdmin(admin.ModelAdmin):
    list_display = ("user", "gift", "status", "created_at")


@admin.register(VoteEvent)
class VoteEventAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "start_at", "end_at")


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("event", "user", "cat", "created_at")
