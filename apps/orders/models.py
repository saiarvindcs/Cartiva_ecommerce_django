from django.db import models
from django.conf import settings
from django.utils import timezone
class CartItem(models.Model):
 user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='cart_items')
 variant=models.ForeignKey('catalog.Variant',on_delete=models.CASCADE)
 quantity=models.PositiveIntegerField(default=1)
 class Meta: constraints=[models.UniqueConstraint(fields=['user','variant'],name='unique_cart_variant')]
class Coupon(models.Model):
 code=models.CharField(max_length=40,unique=True)
 percent=models.PositiveSmallIntegerField()
 max_uses=models.PositiveIntegerField(default=100)
 used=models.PositiveIntegerField(default=0)
 expires_at=models.DateTimeField()
 active=models.BooleanField(default=True)
 class Meta: constraints=[models.CheckConstraint(condition=models.Q(percent__lte=100),name='coupon_percent_max')]
class Order(models.Model):
 STATES=[('pending','Pending'),('paid','Paid'),('shipped','Shipped'),('delivered','Delivered'),('cancelled','Cancelled'),('refunded','Refunded')]
 user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='orders')
 idempotency_key=models.CharField(max_length=100)
 status=models.CharField(max_length=16,choices=STATES,default='pending',db_index=True)
 subtotal=models.DecimalField(max_digits=12,decimal_places=2)
 discount=models.DecimalField(max_digits=12,decimal_places=2,default=0)
 total=models.DecimalField(max_digits=12,decimal_places=2)
 address_snapshot=models.JSONField()
 coupon=models.ForeignKey(Coupon,null=True,blank=True,on_delete=models.SET_NULL)
 created_at=models.DateTimeField(auto_now_add=True)
 updated_at=models.DateTimeField(auto_now=True)
 class Meta:
  constraints=[models.UniqueConstraint(fields=['user','idempotency_key'],name='unique_checkout_retry')]
class OrderItem(models.Model):
 order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items')
 variant=models.ForeignKey('catalog.Variant',on_delete=models.PROTECT)
 product_name=models.CharField(max_length=180)
 sku=models.CharField(max_length=64)
 unit_price=models.DecimalField(max_digits=12,decimal_places=2)
 quantity=models.PositiveIntegerField()
class Reservation(models.Model):
 order_item=models.OneToOneField(OrderItem,on_delete=models.CASCADE,related_name='reservation')
 quantity=models.PositiveIntegerField()
 expires_at=models.DateTimeField(db_index=True)
 released=models.BooleanField(default=False)
 committed=models.BooleanField(default=False)
class OrderAudit(models.Model):
 order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='audit_events')
 from_status=models.CharField(max_length=16)
 to_status=models.CharField(max_length=16)
 actor=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,on_delete=models.SET_NULL)
 at=models.DateTimeField(auto_now_add=True)
