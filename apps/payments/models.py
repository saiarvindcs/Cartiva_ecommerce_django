from django.db import models
class Payment(models.Model):
 order=models.OneToOneField('orders.Order',on_delete=models.PROTECT,related_name='payment')
 provider=models.CharField(max_length=20,default='mock')
 external_id=models.CharField(max_length=180,unique=True)
 status=models.CharField(max_length=24,default='initiated')
 created_at=models.DateTimeField(auto_now_add=True)
class WebhookEvent(models.Model):
 provider=models.CharField(max_length=20)
 event_id=models.CharField(max_length=180)
 received_at=models.DateTimeField(auto_now_add=True)
 class Meta: constraints=[models.UniqueConstraint(fields=['provider','event_id'],name='unique_webhook_event')]
