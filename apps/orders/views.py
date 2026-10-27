
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets,permissions,status,exceptions
from rest_framework.decorators import action,api_view,permission_classes
from rest_framework.response import Response
from django.db import transaction
from .models import CartItem,Order
from .serializers import CartItemSerializer,OrderSerializer,CheckoutSerializer
from .services import checkout,transition
class CartViewSet(viewsets.ModelViewSet):
 serializer_class=CartItemSerializer;permission_classes=[permissions.IsAuthenticated]
 def get_queryset(self):return CartItem.objects.filter(user=self.request.user).select_related('variant')
 def perform_create(self,serializer):
  if CartItem.objects.filter(user=self.request.user,variant=serializer.validated_data['variant']).exists():raise exceptions.ValidationError('Already in cart; update quantity instead')
  serializer.save(user=self.request.user)
class OrderViewSet(viewsets.ReadOnlyModelViewSet):
 serializer_class=OrderSerializer;permission_classes=[permissions.IsAuthenticated]
 def get_queryset(self):
  qs=Order.objects.prefetch_related('items')
  return qs if self.request.user.is_staff else (qs.filter(user=self.request.user) | qs.filter(items__variant__product__seller=self.request.user)).distinct() if self.request.user.is_seller() else qs.filter(user=self.request.user)
 @action(detail=True,methods=['post'])
 def cancel(self,request,pk=None):
  order=self.get_object()
  if order.user_id != request.user.id and not request.user.is_staff: raise exceptions.PermissionDenied()
  return Response(OrderSerializer(transition(order.pk,'cancelled',request.user)).data)
 @action(detail=True,methods=['post'])
 def ship(self,request,pk=None):
  order=self.get_object()
  if not request.user.is_staff and (not request.user.is_seller() or not all(i.variant.product.seller_id==request.user.id for i in order.items.all())):raise exceptions.PermissionDenied()
  return Response(OrderSerializer(transition(order.pk,'shipped',request.user)).data)
 @action(detail=True,methods=['post'])
 def deliver(self,request,pk=None):
  if not request.user.is_staff:raise exceptions.PermissionDenied()
  return Response(OrderSerializer(transition(self.get_object().pk,'delivered',request.user)).data)
@extend_schema(
    request=CheckoutSerializer,
    parameters=[
        OpenApiParameter(
            name="Idempotency-Key",
            type=str,
            location=OpenApiParameter.HEADER,
            required=True,
            description="Unique UUID for each new checkout attempt",
        )
    ],
    responses={201: OrderSerializer},
)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def checkout_view(request):
 serializer=CheckoutSerializer(data=request.data);serializer.is_valid(raise_exception=True)
 order,created=checkout(request.user,request.headers.get('Idempotency-Key'),**serializer.validated_data)
 return Response(OrderSerializer(order).data,status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def seller_orders(request):
 if not request.user.is_seller():
  raise exceptions.PermissionDenied('Seller account required')
 qs=Order.objects.filter(items__variant__product__seller=request.user).distinct().order_by('-created_at')
 return Response(OrderSerializer(qs[:100],many=True).data)
