from rest_framework import serializers
from .models import Review
from apps.orders.models import OrderItem
class ReviewSerializer(serializers.ModelSerializer):
 class Meta:
  model=Review
  fields=['id','product','rating','text','approved','created_at']
  read_only_fields=['approved','created_at']
 def validate_rating(self,value):
  if not 1 <= value <= 5: raise serializers.ValidationError('Rating must be between 1 and 5')
  return value
 def validate(self,data):
  user=self.context['request'].user
  product=data.get('product',getattr(self.instance,'product',None))
  if not OrderItem.objects.filter(order__user=user,order__status__in=['paid','shipped','delivered'],variant__product=product).exists():raise serializers.ValidationError('Verified purchase required')
  if self.instance and 'product' in data and data['product']!=self.instance.product:raise serializers.ValidationError('Cannot change reviewed product')
  return data
