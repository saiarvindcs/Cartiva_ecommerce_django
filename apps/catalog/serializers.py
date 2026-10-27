from rest_framework import serializers
from .models import Category,Product,Variant,ProductImage
class CategorySerializer(serializers.ModelSerializer):
 class Meta:
  model=Category
  fields='__all__'
class VariantSerializer(serializers.ModelSerializer):
 class Meta:
  model=Variant
  fields=['id','product','sku','size','color','price','stock','reserved','active']
  read_only_fields=['reserved']
class ProductImageSerializer(serializers.ModelSerializer):
 class Meta:
  model=ProductImage
  fields=['id','product','image','alt']
class ProductSerializer(serializers.ModelSerializer):
 variants=VariantSerializer(many=True,read_only=True)
 images=ProductImageSerializer(many=True,read_only=True)
 class Meta:
  model=Product
  fields=['id','seller','category','name','slug','description','active','created_at','variants','images']
  read_only_fields=['seller','created_at']
