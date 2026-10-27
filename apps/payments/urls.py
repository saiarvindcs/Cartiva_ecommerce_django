from django.urls import path
from .views import create_payment, simulate_payment
urlpatterns = [path('intent/', create_payment), path('mock/simulate/', simulate_payment)]
