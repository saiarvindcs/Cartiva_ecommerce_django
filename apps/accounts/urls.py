from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import RegisterView,me,AddressViewSet,BecomeSellerView
router=DefaultRouter();router.register('addresses',AddressViewSet,basename='address')
urlpatterns=[path('register/',RegisterView.as_view()),path('me/',me),path('become-seller/',BecomeSellerView.as_view(),name='become-seller'),path('',include(router.urls))]
