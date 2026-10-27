from django.db import models
class AuditLog(models.Model):
 actor=models.ForeignKey('accounts.User',null=True,on_delete=models.SET_NULL)
 action=models.CharField(max_length=120)
 object_type=models.CharField(max_length=80)
 object_id=models.CharField(max_length=80)
 details=models.JSONField(default=dict)
 created_at=models.DateTimeField(auto_now_add=True)
