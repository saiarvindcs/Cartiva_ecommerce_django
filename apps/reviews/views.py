from rest_framework import viewsets,permissions
from .models import Review
from .serializers import ReviewSerializer
class ReviewViewSet(viewsets.ModelViewSet):
 serializer_class=ReviewSerializer
 permission_classes=[permissions.IsAuthenticatedOrReadOnly]
 def get_queryset(self):
  qs=Review.objects.all()
  if self.request.method in permissions.SAFE_METHODS:return qs.filter(approved=True)
  return qs.filter(user=self.request.user)
 def perform_create(self,serializer):serializer.save(user=self.request.user, approved=True)
