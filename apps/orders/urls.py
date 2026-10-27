from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet,OrderViewSet,checkout_view,seller_orders
router=DefaultRouter();router.register('cart',CartViewSet,basename='cart');router.register('orders',OrderViewSet,basename='order')
urlpatterns=[path('checkout/',checkout_view),path('seller-orders/',seller_orders),path('',include(router.urls))]
