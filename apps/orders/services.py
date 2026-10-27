from datetime import timedelta
from decimal import Decimal
from django.db import transaction,IntegrityError
from django.db.models import F
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from apps.catalog.models import Variant
from apps.accounts.models import Address
from .models import CartItem,Order,OrderItem,Reservation,Coupon,OrderAudit
TRANSITIONS={'pending':{'paid','cancelled'},'paid':{'shipped','refunded'},'shipped':{'delivered','refunded'},'delivered':{'refunded'},'cancelled':set(),'refunded':set()}
def release_reservations(order,commit=False):
 for r in Reservation.objects.select_for_update().filter(order_item__order=order,released=False,committed=False):
  Variant.objects.filter(pk=r.order_item.variant_id).update(reserved=F('reserved')-r.quantity,**({'stock':F('stock')-r.quantity} if commit else {}))
  r.committed=commit;r.released=not commit;r.save(update_fields=['committed','released'])
@transaction.atomic
def transition(order_id,new_status,actor=None):
 order=Order.objects.select_for_update().get(pk=order_id)
 if order.status==new_status:return order
 if new_status not in TRANSITIONS.get(order.status,set()): raise ValidationError('Invalid order state transition')
 old=order.status
 if new_status=='paid':
  if not Reservation.objects.filter(order_item__order=order,committed=False,released=False,expires_at__gt=timezone.now()).count()==order.items.count(): raise ValidationError('Reservation expired; payment needs reconciliation')
  release_reservations(order,commit=True)
 elif new_status=='cancelled':release_reservations(order)
 order.status=new_status;order.save(update_fields=['status','updated_at'])
 OrderAudit.objects.create(order=order,from_status=old,to_status=new_status,actor=actor)
 return order
@transaction.atomic
def checkout(user,key,address_id,coupon_code=None):
 if not key or len(key)>100: raise ValidationError('Valid Idempotency-Key header required')
 # Serialize all checkouts for this account to prevent different-key double checkout.
 from django.contrib.auth import get_user_model
 get_user_model().objects.select_for_update().get(pk=user.pk)
 existing=Order.objects.filter(user=user,idempotency_key=key).first()
 if existing:return existing,False
 address=Address.objects.filter(user=user,pk=address_id).first()
 if not address:raise ValidationError('Invalid address')
 cart=list(CartItem.objects.select_for_update().filter(user=user).order_by('variant_id'))
 if not cart:raise ValidationError('Cart is empty')
 variants={v.id:v for v in Variant.objects.select_for_update().filter(id__in=[c.variant_id for c in cart]).order_by('id')}
 subtotal=Decimal('0.00')
 for item in cart:
  v=variants.get(item.variant_id)
  if not v or not v.active or not v.product.active or item.quantity<1 or v.stock-v.reserved<item.quantity:raise ValidationError(f'Insufficient stock for variant {item.variant_id}')
  subtotal+=v.price*item.quantity
 coupon=None;discount=Decimal('0.00')
 if coupon_code:
  coupon=Coupon.objects.select_for_update().filter(code__iexact=coupon_code,active=True,expires_at__gt=timezone.now()).first()
  if not coupon or coupon.used>=coupon.max_uses:raise ValidationError('Invalid or exhausted coupon')
  discount=(subtotal*Decimal(coupon.percent)/Decimal(100)).quantize(Decimal('0.01'))
 order=Order.objects.create(user=user,idempotency_key=key,subtotal=subtotal,discount=discount,total=subtotal-discount,address_snapshot={'full_name':address.full_name,'line1':address.line1,'line2':address.line2,'city':address.city,'region':address.region,'postal_code':address.postal_code,'country':address.country,'phone':address.phone},coupon=coupon)
 for item in cart:
  v=variants[item.variant_id]
  Variant.objects.filter(pk=v.pk).update(reserved=F('reserved')+item.quantity)
  line=OrderItem.objects.create(order=order,variant=v,product_name=v.product.name,sku=v.sku,unit_price=v.price,quantity=item.quantity)
  Reservation.objects.create(order_item=line,quantity=item.quantity,expires_at=timezone.now()+timedelta(minutes=15))
 if coupon:Coupon.objects.filter(pk=coupon.pk).update(used=F('used')+1)
 CartItem.objects.filter(pk__in=[c.pk for c in cart]).delete()
 from .tasks import send_order_email
 transaction.on_commit(lambda: _safe_send_order_email(order.pk))
 return order,True


def _safe_send_order_email(order_id):
    # Email broker outages must not turn a committed order into a checkout error.
    import logging
    from .tasks import send_order_email
    try:
        send_order_email.delay(order_id)
    except Exception:
        logging.getLogger(__name__).exception('Failed to enqueue order email for %s', order_id)
