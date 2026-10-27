from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User,Address
class RegisterSerializer(serializers.ModelSerializer):
 password=serializers.CharField(write_only=True,validators=[validate_password])
 class Meta:
  model=User
  fields=['id','username','email','password','first_name','last_name']
 def create(self,validated_data): return User.objects.create_user(**validated_data)
class UserSerializer(serializers.ModelSerializer):
 class Meta:
  model=User
  fields=['id','username','email','first_name','last_name','role']
  read_only_fields=['role']
class AddressSerializer(serializers.ModelSerializer):
 class Meta:
  model=Address
  exclude=['user']
