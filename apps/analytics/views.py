from django.db.models import Sum,Count,F
from django.db.models.functions import TruncDate
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from apps.orders.models import Order,OrderItem
from apps.catalog.models import Variant
@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard(request):
 paid=Order.objects.filter(status__in=['paid','shipped','delivered'])
 daily=list(paid.annotate(day=TruncDate('created_at')).values('day').annotate(revenue=Sum('total'),orders=Count('id')).order_by('-day')[:30])
 top=list(OrderItem.objects.filter(order__status__in=['paid','shipped','delivered']).values('product_name').annotate(units=Sum('quantity')).order_by('-units')[:10])
 low=list(Variant.objects.filter(stock__lte=F('reserved')+5).values('sku','stock','reserved')[:30])
 return Response({'daily_sales':daily,'top_products':top,'low_stock':low})


from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from decimal import Decimal
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def seller_dashboard(request):
 if not request.user.is_seller(): raise PermissionDenied('Seller access required')
 items=OrderItem.objects.filter(variant__product__seller=request.user,order__status__in=['paid','shipped','delivered'])
 units=items.aggregate(total=Sum('quantity'))['total'] or 0
 revenue=sum((item.unit_price*item.quantity for item in items),Decimal('0.00'))
 orders=items.values('order_id').distinct().count()
 from apps.catalog.models import Product
 products=Product.objects.filter(seller=request.user).count()
 return Response({'revenue':str(revenue),'orders':orders,'units_sold':units,'products':products})
