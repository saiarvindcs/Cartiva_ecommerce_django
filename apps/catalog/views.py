from rest_framework import viewsets,permissions,exceptions
from django.db.models import Q
from django.core.cache import cache
from .models import Product,Category,Variant,ProductImage
from .serializers import ProductSerializer,CategorySerializer,VariantSerializer,ProductImageSerializer
class SellerWritePermission(permissions.BasePermission):
 def has_permission(self,request,view): return request.method in permissions.SAFE_METHODS or bool(request.user.is_authenticated and request.user.is_seller())
 def has_object_permission(self,request,view,obj):
  return request.method in permissions.SAFE_METHODS or request.user.is_staff or getattr(obj,'seller_id',getattr(getattr(obj,'product',None),'seller_id',None))==request.user.id
class CategoryViewSet(viewsets.ModelViewSet):
 queryset=Category.objects.all();serializer_class=CategorySerializer
 def get_permissions(self):
  return [permissions.AllowAny()] if self.action in ('list','retrieve') else [permissions.IsAdminUser()]
class ProductViewSet(viewsets.ModelViewSet):
 serializer_class=ProductSerializer;permission_classes=[SellerWritePermission]
 search_fields=['name','description','variants__sku']
 filterset_fields=['category','active']
 ordering_fields=['name','created_at']
 def get_queryset(self):
  qs=Product.objects.select_related('category','seller').prefetch_related('variants','images')
  if self.request.method in permissions.SAFE_METHODS: qs=qs.filter(active=True)
  elif not self.request.user.is_staff: qs=qs.filter(seller=self.request.user)
  return qs.distinct()
 def perform_create(self,serializer): serializer.save(seller=self.request.user)
class VariantViewSet(viewsets.ModelViewSet):
 serializer_class=VariantSerializer;permission_classes=[SellerWritePermission]
 def get_queryset(self):
  qs=Variant.objects.select_related('product')
  if self.request.method in permissions.SAFE_METHODS: return qs.filter(active=True,product__active=True)
  return qs if self.request.user.is_staff else qs.filter(product__seller=self.request.user)
 def perform_create(self,serializer):
  product=Product.objects.filter(pk=self.request.data.get('product')).first()
  if product is None: raise exceptions.ValidationError({'product': 'Invalid product'})
  if not self.request.user.is_staff and product.seller_id!=self.request.user.id: raise exceptions.PermissionDenied()
  serializer.save(product=product)
class ProductImageViewSet(viewsets.ModelViewSet):
 serializer_class=ProductImageSerializer;permission_classes=[SellerWritePermission]
 def get_queryset(self):
  qs=ProductImage.objects.select_related('product')
  return qs.filter(product__active=True) if self.request.method in permissions.SAFE_METHODS else (qs if self.request.user.is_staff else qs.filter(product__seller=self.request.user))
 def perform_create(self,serializer):
  product=Product.objects.filter(pk=self.request.data.get('product')).first()
  if product is None: raise exceptions.ValidationError({'product': 'Invalid product'})
  if not self.request.user.is_staff and product.seller_id!=self.request.user.id: raise exceptions.PermissionDenied()
  serializer.save(product=product)
