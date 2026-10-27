import os
from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
app=Celery('ecommerce')
app.config_from_object('django.conf:settings',namespace='CELERY')
app.autodiscover_tasks()
app.conf.beat_schedule={'expire-reservations':{'task':'apps.orders.tasks.expire_reservations','schedule':60.0},'abandoned-carts':{'task':'apps.orders.tasks.abandoned_cart_reminders','schedule':3600.0}}
