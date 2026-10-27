import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_customer_can_become_seller_and_create_product():
    User=get_user_model()
    user=User.objects.create_user(username='seller_test',password='StrongTest123!')
    client=APIClient()
    client.force_authenticate(user=user)
    response=client.post('/api/accounts/become-seller/')
    assert response.status_code==200
    user.refresh_from_db()
    assert user.role=='seller'
    from apps.catalog.models import Category
    cat=Category.objects.create(name='Test Category',slug='test-category')
    response=client.post('/api/catalog/products/',{'name':'Test Product','slug':'test-product','category':cat.pk,'description':'A product'})
    assert response.status_code==201,response.data

@pytest.mark.django_db
def test_customer_cannot_create_product():
    user=get_user_model().objects.create_user(username='buyer_test',password='StrongTest123!')
    client=APIClient()
    client.force_authenticate(user=user)
    response=client.post('/api/catalog/products/',{'name':'Bad','slug':'bad','category':1})
    assert response.status_code==403
