from django.db import models
from django.conf import settings
class Review(models.Model):
 user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
 product=models.ForeignKey('catalog.Product',on_delete=models.CASCADE,related_name='reviews')
 rating=models.PositiveSmallIntegerField()
 text=models.TextField(blank=True)
 approved=models.BooleanField(default=False)
 created_at=models.DateTimeField(auto_now_add=True)
 class Meta:
  constraints=[models.UniqueConstraint(fields=['user','product'],name='one_review_per_product'),models.CheckConstraint(condition=models.Q(rating__gte=1,rating__lte=5),name='valid_review_rating')]
