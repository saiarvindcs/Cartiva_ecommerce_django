from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
 ROLE_CHOICES=[('customer','Customer'),('seller','Seller'),('admin','Admin')]
 role=models.CharField(max_length=12,choices=ROLE_CHOICES,default='customer')
 def is_seller(self): return self.role in ('seller','admin') or self.is_staff
class Address(models.Model):
 user=models.ForeignKey('accounts.User',on_delete=models.CASCADE,related_name='addresses')
 full_name=models.CharField(max_length=120)
 line1=models.CharField(max_length=200)
 line2=models.CharField(max_length=200,blank=True)
 city=models.CharField(max_length=80)
 region=models.CharField(max_length=80)
 postal_code=models.CharField(max_length=16)
 country=models.CharField(max_length=2,default='IN')
 phone=models.CharField(max_length=24)
