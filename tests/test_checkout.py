import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.accounts.models import Address
from apps.catalog.models import Category,Product,Variant
from apps.orders.models import CartItem,Order
from apps.orders.services import checkout,transition
@pytest.mark.django_db(transaction=True)
def test_checkout_reserves_and_is_idempotent(monkeypatch):
 from apps.orders import tasks
 monkeypatch.setattr(tasks.send_order_email,'delay',lambda *args:None)
 User=get_user_model();user=User.objects.create_user(username='buyer',password='StrongPass123!');seller=User.objects.create_user(username='seller',password='StrongPass123!',role='seller')
 a=Address.objects.create(user=user,full_name='Buyer',line1='Road',city='Pune',region='MH',postal_code='411001',phone='1234567890')
 c=Category.objects.create(name='Tech',slug='tech');p=Product.objects.create(seller=seller,category=c,name='Mouse',slug='mouse')
 v=Variant.objects.create(product=p,sku='M1',price=Decimal('999.00'),stock=1)
 CartItem.objects.create(user=user,variant=v,quantity=1)
 order,created=checkout(user,'unique-key',a.id)
 assert created and order.total==Decimal('999.00')
 v.refresh_from_db();assert v.reserved==1 and v.stock==1
 again,created=checkout(user,'unique-key',a.id)
 assert not created and again.id==order.id
 transition(order.id,'paid');v.refresh_from_db()
 assert v.stock==0 and v.reserved==0
 assert Order.objects.count()==1
@pytest.mark.django_db
def test_anonymous_cannot_access_cart():
 assert APIClient().get('/api/orders/cart/').status_code in (401,403)
