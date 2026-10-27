"""PostgreSQL concurrency test: one SKU, two buyers, only one reservation succeeds."""
import threading
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
import pytest
from django.db import close_old_connections
from django.contrib.auth import get_user_model
from apps.accounts.models import Address
from apps.catalog.models import Category,Product,Variant
from apps.orders.models import CartItem,Order
from apps.orders.services import checkout
@pytest.mark.django_db(transaction=True)
def test_last_item_cannot_be_oversold(monkeypatch):
 from apps.orders import tasks
 monkeypatch.setattr(tasks.send_order_email,'delay',lambda *a:None)
 User=get_user_model();seller=User.objects.create_user(username='seller2',password='StrongPass123!',role='seller')
 c=Category.objects.create(name='Accessories',slug='accessories');p=Product.objects.create(seller=seller,category=c,name='Keyboard',slug='keyboard')
 v=Variant.objects.create(product=p,sku='K1',price=Decimal('500.00'),stock=1)
 buyers=[]
 for i in range(2):
  u=User.objects.create_user(username=f'buyer{i}',password='StrongPass123!')
  a=Address.objects.create(user=u,full_name='Buyer',line1='Main',city='Pune',region='MH',postal_code='411001',phone='1234567890')
  CartItem.objects.create(user=u,variant=v,quantity=1);buyers.append((u,a))
 barrier=threading.Barrier(2)
 def run(pair):
  close_old_connections();barrier.wait()
  try:checkout(pair[0],'key',pair[1].id);return 'success'
  except Exception:return 'failed'
  finally:close_old_connections()
 with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(run,buyers))
 v.refresh_from_db()
 assert results.count('success')==1
 assert v.reserved==1 and v.stock==1 and Order.objects.count()==1
