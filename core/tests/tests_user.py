from ddt import ddt, data, unpack
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken


@ddt
class UserTests(APITestCase):
    user = {
        'username': 'user',
        'email': 'user@foo.com',
        'password': 'pass',
        'first_name': 'First',
        'last_name': 'Last'
    }

    def setUp(self):
        user = User.objects.create_user(**self.user)

        token = AccessToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {0}'.format(token))

    def test_user_get(self):
        response = self.client.get('/api/user', format='json')
        api_user = response.json()

        assert response.status_code == 200
        assert api_user['username'] == self.user['username']
        assert api_user['email'] == self.user['email']
        assert api_user['first_name'] == self.user['first_name']
        assert api_user['last_name'] == self.user['last_name']
        assert api_user['full_name'] == f'{self.user["first_name"]} {self.user["last_name"]}'
        assert 'password' not in api_user

    @data(
        ('email', 'user1@foo.com'),
        ('first_name', 'First1'),
        ('last_name', 'First1'),
    )
    @unpack
    def test_user_update(self, field, value):
        response = self.client.patch('/api/user', {field: value}, format='json')
        api_user = response.json()

        assert response.status_code == 200
        assert api_user[field] == value

    @data(
        ('username', 'user2'),
    )
    @unpack
    def test_user_update_read_only_fields(self, field, value):
        response = self.client.patch('/api/user', {field: value}, format='json')
        api_user = response.json()

        assert response.status_code == 200
        assert api_user[field] == self.user[field]
