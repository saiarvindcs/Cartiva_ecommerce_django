from rest_framework import generics,permissions,viewsets
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from .models import Address
from .serializers import RegisterSerializer,UserSerializer,AddressSerializer
class RegisterView(generics.CreateAPIView):
 serializer_class=RegisterSerializer
 permission_classes=[permissions.AllowAny]
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def me(request): return Response(UserSerializer(request.user).data)
class AddressViewSet(viewsets.ModelViewSet):
 serializer_class=AddressSerializer
 permission_classes=[permissions.IsAuthenticated]
 def get_queryset(self): return Address.objects.filter(user=self.request.user)
 def perform_create(self,serializer): serializer.save(user=self.request.user)

from rest_framework.views import APIView
from django.db import transaction

class BecomeSellerView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    @transaction.atomic
    def post(self, request):
        user = type(request.user).objects.select_for_update().get(pk=request.user.pk)
        if user.role == 'customer':
            user.role = 'seller'
            user.save(update_fields=['role'])
        return Response(UserSerializer(user).data)
