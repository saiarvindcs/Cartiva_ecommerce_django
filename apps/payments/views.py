"""Development-only payment simulator. NEVER expose to the public internet."""
import uuid
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.orders.models import Order, Reservation
from apps.orders.services import transition
from .models import Payment


def _allowed(request):
    # DEBUG alone is insufficient: require an explicit feature flag and authenticated user.
    return settings.DEBUG and settings.MOCK_PAYMENTS_ENABLED and request.user.is_authenticated


def _valid_reservations(order):
    reservations = list(Reservation.objects.filter(order_item__order=order))
    return bool(reservations) and len(reservations) == order.items.count() and all(
        not r.released and not r.committed and r.expires_at > timezone.now()
        for r in reservations
    )


@extend_schema(request=inline_serializer(name='CreateMockPaymentRequest', fields={
    'order_id': serializers.IntegerField(min_value=1),
}), responses={201: inline_serializer(name='MockPaymentIntentResponse', fields={'payment_id': serializers.CharField(), 'order_id': serializers.IntegerField(), 'amount': serializers.CharField(), 'currency': serializers.CharField(), 'status': serializers.CharField()})})
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment(request):
    if not _allowed(request):
        return Response({'detail': 'Mock payments are available only in explicitly enabled development mode'}, status=403)
    serializer = inline_serializer(name='CreateMockPaymentInput', fields={
        'order_id': serializers.IntegerField(min_value=1),
    })
    serializer = type(serializer)(data=request.data)
    serializer.is_valid(raise_exception=True)
    with transaction.atomic():
        order = Order.objects.select_for_update().filter(
            pk=serializer.validated_data['order_id'], user=request.user, status='pending'
        ).first()
        if not order:
            return Response({'detail': 'Pending order not found for this account'}, status=404)
        if not _valid_reservations(order):
            return Response({'detail': 'Reservation expired'}, status=409)
        payment, created = Payment.objects.get_or_create(order=order, defaults={
            'provider': 'mock', 'external_id': 'mock_' + uuid.uuid4().hex
        })
        if payment.provider != 'mock':
            return Response({'detail': 'Another provider is attached'}, status=409)
        return Response({'payment_id': payment.external_id, 'order_id': order.pk,
                         'amount': str(order.total), 'currency': 'INR',
                         'status': payment.status}, status=201 if created else 200)


@extend_schema(request=inline_serializer(name='SimulateMockPaymentRequest', fields={
    'payment_id': serializers.CharField(),
    'outcome': serializers.ChoiceField(choices=['success', 'failure']),
}), responses={200: inline_serializer(name='MockPaymentSimulationResponse', fields={'payment_id': serializers.CharField(), 'status': serializers.CharField(), 'order_status': serializers.CharField()})})
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def simulate_payment(request):
    if not _allowed(request):
        return Response({'detail': 'Mock payments are available only in explicitly enabled development mode'}, status=403)
    serializer = inline_serializer(name='SimulateMockPaymentInput', fields={
        'payment_id': serializers.CharField(),
        'outcome': serializers.ChoiceField(choices=['success', 'failure']),
    })
    serializer = type(serializer)(data=request.data)
    serializer.is_valid(raise_exception=True)
    with transaction.atomic():
        # Consistent lock order: order first, then payment, then reservations.
        candidate = Payment.objects.filter(external_id=serializer.validated_data['payment_id'],
                                           provider='mock', order__user=request.user).values('order_id').first()
        if not candidate:
            return Response({'detail': 'Payment not found'}, status=404)
        order = Order.objects.select_for_update().get(pk=candidate['order_id'])
        payment = Payment.objects.select_for_update().get(order=order)
        if payment.status in ('succeeded', 'failed'):
            return Response({'payment_id': payment.external_id, 'status': payment.status,
                             'order_status': order.status})
        if order.status != 'pending' or not _valid_reservations(order):
            return Response({'detail': 'Order is no longer payable; no charge was made'}, status=409)
        if serializer.validated_data['outcome'] == 'success':
            transition(order.pk, 'paid', actor=request.user)
            payment.status = 'succeeded'
        else:
            payment.status = 'failed'
        payment.save(update_fields=['status'])
        order.refresh_from_db()
        return Response({'payment_id': payment.external_id, 'status': payment.status,
                         'order_status': order.status})
