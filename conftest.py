import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user(db):
    def make_user(username='testuser', password='testpass123', is_staff=False):
        return User.objects.create_user(
            username=username,
            password=password,
            is_staff=is_staff
        )
    return make_user

@pytest.fixture
def auth_client(api_client, create_user):
    user = create_user()
    response = api_client.post('/api/auth/login/', {
        'username': 'testuser',
        'password': 'testpass123'
    })
    token = response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client, user

@pytest.fixture
def admin_client(api_client, create_user):
    admin = create_user(username='admin', password='adminpass123', is_staff=True)
    response = api_client.post('/api/auth/login/', {
        'username': 'admin',
        'password': 'adminpass123'
    })
    token = response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client,admin