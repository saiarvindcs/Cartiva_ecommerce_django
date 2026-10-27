from django.urls import include,path
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet,CategoryViewSet,VariantViewSet,ProductImageViewSet
router=DefaultRouter();router.register('products',ProductViewSet,basename='product');router.register('categories',CategoryViewSet);router.register('variants',VariantViewSet,basename='variant');router.register('images',ProductImageViewSet,basename='image')
urlpatterns=[path('',include(router.urls))]
