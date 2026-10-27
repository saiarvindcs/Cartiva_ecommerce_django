from django.db import models
from django.conf import settings
class Category(models.Model):
 name=models.CharField(max_length=100,unique=True)
 slug=models.SlugField(unique=True)
 def __str__(self): return self.name
class Product(models.Model):
 seller=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='products')
 category=models.ForeignKey(Category,on_delete=models.PROTECT,related_name='products')
 name=models.CharField(max_length=180,db_index=True)
 slug=models.SlugField(unique=True)
 description=models.TextField(blank=True)
 active=models.BooleanField(default=True,db_index=True)
 created_at=models.DateTimeField(auto_now_add=True)
 class Meta:
  indexes=[models.Index(fields=['category','active']),models.Index(fields=['created_at'])]
 def __str__(self): return self.name
class Variant(models.Model):
 product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='variants')
 sku=models.CharField(max_length=64,unique=True)
 size=models.CharField(max_length=32,blank=True)
 color=models.CharField(max_length=32,blank=True)
 price=models.DecimalField(max_digits=12,decimal_places=2)
 stock=models.PositiveIntegerField(default=0)
 reserved=models.PositiveIntegerField(default=0)
 active=models.BooleanField(default=True)
 class Meta:
  constraints=[models.CheckConstraint(condition=models.Q(stock__gte=models.F('reserved')),name='stock_covers_reserved')]
class ProductImage(models.Model):
 product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='images')
 image=models.ImageField(upload_to='products/')
 alt=models.CharField(max_length=160,blank=True)
