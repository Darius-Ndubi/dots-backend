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
        self.workspace = Workspace.objects.create(display_name='test', name='test')

        token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {0}'.format(token))

    def add_user_to_workspace(self, username, role, is_active):
        _user = self._user.copy()
        _user['email'] = f'{username}@foo.com'
        _user['username'] = username
        user = User.objects.create_user(**_user)
        Membership.objects.create(workspace=self.workspace, user=user, role=role, is_active=is_active)

    @data(
        Membership.ADMIN,
        Membership.OWNER,
        Membership.MEMBER
    )
    def test_workspace_users_list(self, role):
        # Test if API lists all users
        Membership.objects.create(workspace=self.workspace, user=self.user, role=role, is_active=True)
        users = [
            ('user1', Membership.OWNER, True),
            ('user2', Membership.ADMIN, True),
            ('user3', Membership.MEMBER, True),
            ('user4', Membership.OWNER, False),
            ('user5', Membership.ADMIN, False),
            ('user6', Membership.MEMBER, False),
        ]
        for u, r, a in users:
            self.add_user_to_workspace(u, r, is_active=a)

        response = self.client.get(f'/api/workspace/{self.workspace.id}/users', format='json')
        workspace = response.json()
        assert response.status_code == 200

        users = [('user', role, True)] + users
        for i, ru in enumerate(users):
            u, r, a = ru
            assert workspace[i]['role'] == r
            assert workspace[i]['email'] == f'{u}@foo.com'
            assert workspace[i]['username'] == u
            assert workspace[i]['is_active'] == a

    @data(
        Membership.ADMIN,
        Membership.OWNER,
        Membership.MEMBER
    )
    def test_no_active_users_access_on_workspace_users_list(self, role):
        Membership.objects.create(workspace=self.workspace, user=self.user, role=role, is_active=False)
        response = self.client.get(f'/api/workspace/{self.workspace.id}/users', format='json')
        assert response.status_code == 403

    def test_non_members_access_on_workspace_users_list(self):
        response = self.client.get(f'/api/workspace/{self.workspace.id}/users', format='json')
        assert response.status_code == 403
