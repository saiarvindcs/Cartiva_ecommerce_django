from django.urls import path
from .views import dashboard, seller_dashboard
urlpatterns=[path('seller/',seller_dashboard),path('dashboard/',dashboard)]
