# -*- coding: utf-8 -*-
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.utils import timezone
from shop.models import Reservation

print("服务器 localdate:", timezone.localdate())
for r in Reservation.objects.all().order_by("date"):
    print(f"id={r.id} {r.user.username} {r.date} {r.start_time}-{r.end_time} {r.seat.name} [{r.status}]")
