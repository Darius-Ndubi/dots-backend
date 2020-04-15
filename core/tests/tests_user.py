from ddt import ddt, data, unpack
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


def assert_user(user=None, response=None):
    assert response is not None
    assert user is not None

    api_user = response.json()
    assert response.status_code == 200
    assert api_user['username'] == user['username']
    assert api_user['email'] == user['email']
    assert api_user['first_name'] == user['first_name']
    assert api_user['last_name'] == user['last_name']
    assert api_user['full_name'] == f'{user["first_name"]} {user["last_name"]}'
    assert 'password' not in api_user


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
        assert_user(user=self.user, response=response)

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


@ddt
class UserRegistrationTests(APITestCase):
    user = {
        'username': 'user',
        'email': 'user@foo.com',
        'password': 'pass',
        'confirm_password': 'pass',
        'first_name': 'First',
        'last_name': 'Last'
    }

    def test_new_user_registration(self):
        response = self.client.post('/api/user/register', self.user, format='json')
        json_response = response.json()

        assert response.status_code == 201
        assert 'refresh' in json_response
        assert 'access' in json_response

        self.client.credentials(HTTP_AUTHORIZATION='Bearer {0}'.format(json_response['access']))
        response = self.client.get('/api/user', format='json')
        assert_user(user=self.user, response=response)

    @data(
        'username',
        'email',
        'password',
        'confirm_password',
        'first_name',
        'last_name'
    )
    def test_missing_field(self, field):
        user = self.user.copy()
        user.pop(field)
        response = self.client.post('/api/user/register', user, format='json')

        assert response.status_code == 400
        assert response.json() == {field: ['This field is required.']}

    def test_different_passwords(self):
        user = self.user.copy()
        user['confirm_password'] = 'Not Same Password'
        response = self.client.post('/api/user/register', user, format='json')

        assert response.status_code == 400
        assert response.json() == {'confirm_password': ['Passwords do not match.']}

    @data(
        ('user@foo.com', 'user1', {'email': ['Email already in use.']}),
        ('User@Foo.com', 'user1', {'email': ['Email already in use.']}),
        ('user@foo.com', 'user', {'username': ['Username already in use.']}),
        ('user@foo.com', 'UsEr', {'username': ['Username already in use.']}),
    )
    @unpack
    def test_existing_email_username(self, email, username, error):
        response = self.client.post('/api/user/register', self.user, format='json')

        assert response.status_code == 201

        user = self.user.copy()
        user['username'] = username
        user['email'] = email
        response = self.client.post('/api/user/register', user, format='json')

        assert response.status_code == 400
        assert response.json() == error

    def test_invalid_email(self):
        user = self.user.copy()
        user['email'] = 'Woooh'
        response = self.client.post('/api/user/register', user, format='json')

        assert response.status_code == 400
        assert response.json() == {'email': ['Enter a valid email address.']}
