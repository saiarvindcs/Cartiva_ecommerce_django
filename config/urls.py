from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from drf_spectacular.views import SpectacularAPIView,SpectacularSwaggerView
urlpatterns=[path('admin/',admin.site.urls),path('api/auth/token/',TokenObtainPairView.as_view()),path('api/auth/refresh/',TokenRefreshView.as_view()),path('api/schema/',SpectacularAPIView.as_view(),name='schema'),path('api/docs/',SpectacularSwaggerView.as_view(url_name='schema')),path('api/accounts/',include('apps.accounts.urls')),path('api/catalog/',include('apps.catalog.urls')),path('api/orders/',include('apps.orders.urls')),path('api/payments/',include('apps.payments.urls')),path('api/reviews/',include('apps.reviews.urls')),path('api/analytics/',include('apps.analytics.urls')),path('',include('apps.storefront.urls'))]
if settings.DEBUG: urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
