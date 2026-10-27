import logging
from celery import shared_task
from django.utils import timezone
from django.db import transaction
from django.db.models import F
from django.core.mail import send_mail
from django.conf import settings
from .models import Order, Reservation, OrderAudit
from apps.catalog.models import Variant


@shared_task(bind=True, max_retries=3)
def send_order_email(self, order_id):
    try:
        order = Order.objects.select_related('user').get(pk=order_id)
        if order.user.email:
            send_mail('Order received', f'Order #{order.pk} status: {order.status}',
                      settings.DEFAULT_FROM_EMAIL, [order.user.email], fail_silently=False)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task
def expire_reservations():
    order_ids = list(Reservation.objects.filter(
        expires_at__lte=timezone.now(), released=False, committed=False,
        order_item__order__status='pending'
    ).values_list('order_item__order_id', flat=True).distinct()[:300])
    for order_id in order_ids:
        with transaction.atomic():
            order = Order.objects.select_for_update().filter(pk=order_id).first()
            if not order or order.status != 'pending':
                continue
            reservations = list(Reservation.objects.select_for_update().filter(
                order_item__order=order, released=False, committed=False))
            if not reservations:
                continue
            # All reservations for a checkout have the same expiry window.
            if any(r.expires_at > timezone.now() for r in reservations):
                continue
            for r in reservations:
                Variant.objects.filter(pk=r.order_item.variant_id).update(reserved=F('reserved') - r.quantity)
                r.released = True
                r.save(update_fields=['released'])
            order.status = 'cancelled'
            order.save(update_fields=['status', 'updated_at'])
            OrderAudit.objects.create(order=order, from_status='pending', to_status='cancelled')


@shared_task
def abandoned_cart_reminders():
    # Requires user opt-in and an updated_at field; deliberately not implemented.
    return 0
