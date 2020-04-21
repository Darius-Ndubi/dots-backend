from ddt import ddt, data, unpack
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from core.models import Membership, Workspace

User = get_user_model()


@ddt
class WorkspaceTests(APITestCase):
    _user = {
        'username': 'user',
        'email': 'user@foo.com',
        'password': 'pass',
        'first_name': 'First',
        'last_name': 'Last'
    }

    def setUp(self):
        self.user = User.objects.create_user(**self._user)

        token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {0}'.format(token))

    @data(
        Membership.ADMIN,
        Membership.OWNER,
        Membership.MEMBER
    )
    def test_workspace_roles(self, role):
        ws = Workspace.objects.create(name='Test', slug='test')
        Membership.objects.create(user=self.user, workspace=ws, role=role)
        response = self.client.get('/api/workspace', format='json')
        workspace = response.json()
        assert response.status_code == 200
        assert workspace[0]['role'] == role
