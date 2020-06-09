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
        ws = Workspace.objects.create(display_name='Test', name='test')
        Membership.objects.create(user=self.user, workspace=ws, role=role)
        response = self.client.get('/api/workspace', format='json')
        workspace = response.json()
        assert response.status_code == 200
        assert workspace[0]['role'] == role

    def test_workspace_creator_as_owner(self):
        response = self.client.post('/api/workspace',
                                    {"display_name": "Test", "name": "test"},
                                    format='json')
        workspace = response.json()
        assert response.status_code == 201
        assert workspace['role'] == 'OWNER'
        assert workspace['is_default']

    def test_new_workspace_as_default(self):
        response = self.client.post('/api/workspace',
                                    {"display_name": "Test", "name": "test"},
                                    format='json')
        w1 = response.json()
        m = Membership.objects.filter(workspace=w1['id'], user=self.user).first()
        assert m.is_default

        response = self.client.post('/api/workspace',
                                    {"display_name": "Test", "name": "test-1"},
                                    format='json')
        w2 = response.json()
        m = Membership.objects.filter(workspace=w1['id'], user=self.user).first()
        assert not m.is_default

        m = Membership.objects.filter(workspace=w2['id'], user=self.user).first()
        assert m.is_default

    @data(
        (Membership.ADMIN, True),
        (Membership.OWNER, True),
        (Membership.MEMBER, False),
    )
    @unpack
    def test_only_admin_can_update_workspace(self, role, allow_update):
        ws = Workspace.objects.create(display_name='Test', name='s')
        Membership.objects.create(workspace=ws, user=self.user, role=role)
        response = self.client.patch(f'/api/workspace/{ws.id}',
                                     {"display_name": "Test 1"}, format='json')
        ws = response.json()
        if allow_update:
            assert response.status_code == 200
            assert ws['display_name'] == 'Test 1'
        else:
            assert response.status_code == 403
            assert ws['detail'] == 'You do not have permission to perform this action.'

    @data(
        ('display_name', 'New Name', False),
        ('description', 'WoW', False),
        ('location', 'Test', False),
        ('website', 'http://google.com', False),
        ('name', 'new-slug', False),
        ('is_default', False, True),
        ('role', Membership.OWNER, True),
    )
    @unpack
    def test_workspace_update(self, field, value, read_only):
        ws = Workspace.objects.create(display_name='Test', name='s')
        ms = Membership.objects.create(workspace=ws, user=self.user, role=Membership.ADMIN)

        response = self.client.patch(f'/api/workspace/{ws.id}',
                                     {field: value}, format='json')
        api_ws = response.json()
        assert response.status_code == 200

        if read_only:
            assert getattr(ms, field) == api_ws[field]
        else:
            assert api_ws[field] == value
