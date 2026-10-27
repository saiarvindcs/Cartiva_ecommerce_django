from django.contrib import admin
from .models import CartItem,Coupon,Order,OrderItem,Reservation,OrderAudit
for model in (CartItem,Coupon,Order,OrderItem,Reservation,OrderAudit):admin.site.register(model)
