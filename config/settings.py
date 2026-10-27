import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
BASE_DIR=Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR/'.env')
SECRET_KEY=os.getenv('DJANGO_SECRET_KEY','development-only-insecure-key')
DEBUG=os.getenv('DJANGO_DEBUG','0')=='1'
ALLOWED_HOSTS=os.getenv('DJANGO_ALLOWED_HOSTS','localhost,127.0.0.1').split(',')
INSTALLED_APPS=['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','rest_framework','rest_framework_simplejwt','django_filters','drf_spectacular','apps.accounts','apps.catalog','apps.orders','apps.payments','apps.reviews','apps.audit','apps.analytics','apps.storefront']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','whitenoise.middleware.WhiteNoiseMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF='config.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.debug','django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION='config.wsgi.application'
DATABASES={'default':{'ENGINE':'django.db.backends.postgresql','NAME':os.getenv('POSTGRES_DB','ecommerce'),'USER':os.getenv('POSTGRES_USER','ecommerce'),'PASSWORD':os.getenv('POSTGRES_PASSWORD','change-me'),'HOST':os.getenv('DATABASE_URL_HOST','localhost'),'PORT':'5432','CONN_MAX_AGE':60}}
AUTH_USER_MODEL='accounts.User'
AUTH_PASSWORD_VALIDATORS=[{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
REST_FRAMEWORK={'DEFAULT_AUTHENTICATION_CLASSES':['rest_framework_simplejwt.authentication.JWTAuthentication','rest_framework.authentication.SessionAuthentication'],'DEFAULT_PERMISSION_CLASSES':['rest_framework.permissions.IsAuthenticatedOrReadOnly'],'DEFAULT_PAGINATION_CLASS':'rest_framework.pagination.PageNumberPagination','PAGE_SIZE':12,'DEFAULT_FILTER_BACKENDS':['django_filters.rest_framework.DjangoFilterBackend','rest_framework.filters.SearchFilter','rest_framework.filters.OrderingFilter'],'DEFAULT_SCHEMA_CLASS':'drf_spectacular.openapi.AutoSchema','DEFAULT_THROTTLE_CLASSES':['rest_framework.throttling.AnonRateThrottle','rest_framework.throttling.UserRateThrottle'],'DEFAULT_THROTTLE_RATES':{'anon':'120/hour','user':'1200/hour'}}
SIMPLE_JWT={'ACCESS_TOKEN_LIFETIME':timedelta(minutes=30),'REFRESH_TOKEN_LIFETIME':timedelta(days=7)}
SPECTACULAR_SETTINGS={'TITLE':'Cartiva Commerce API','DESCRIPTION':'Modular commerce backend API','VERSION':'1.0.0'}
CACHES={'default':{'BACKEND':'django.core.cache.backends.redis.RedisCache','LOCATION':os.getenv('REDIS_URL','redis://localhost:6379/0')}}
CELERY_BROKER_URL=os.getenv('REDIS_URL','redis://localhost:6379/0')
CELERY_RESULT_BACKEND=CELERY_BROKER_URL
CELERY_TASK_ACKS_LATE=True
CELERY_TASK_REJECT_ON_WORKER_LOST=True
EMAIL_BACKEND=os.getenv('EMAIL_BACKEND','django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL='orders@example.invalid'
STATIC_URL='/static/'
STATIC_ROOT=BASE_DIR/'staticfiles'
STATICFILES_DIRS=[BASE_DIR/'static']
MEDIA_URL='/media/'
MEDIA_ROOT=BASE_DIR/'media'
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
TIME_ZONE='UTC'
USE_TZ=True
SECURE_SSL_REDIRECT=os.getenv('DJANGO_SECURE_SSL_REDIRECT','0')=='1'
SESSION_COOKIE_SECURE=not DEBUG
CSRF_COOKIE_SECURE=not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS='DENY'
MOCK_PAYMENTS_ENABLED=os.getenv('MOCK_PAYMENTS_ENABLED','0')=='1'
CSRF_TRUSTED_ORIGINS=[x for x in os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS','').split(',') if x]
SECURE_HSTS_SECONDS=int(os.getenv('DJANGO_SECURE_HSTS_SECONDS','0'))
SECURE_HSTS_INCLUDE_SUBDOMAINS=SECURE_HSTS_SECONDS>0
SECURE_HSTS_PRELOAD=False
