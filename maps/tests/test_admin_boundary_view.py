from rest_framework.test import (APIClient, APITestCase, )

from django.contrib.auth import get_user_model
from django.urls import reverse

from ..models import AdminBoundary
from core.models import (Workspace, )

admin_boundary_obj = dict(
    name='Test Admin',
)


class AdminBoundaryViewTestCase(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user: get_user_model() = get_user_model().objects.create(
            username='test',
            email='test.hikaya.io',
            password='TestUser'
        )

        self.workspace: Workspace = Workspace.objects.create(
            display_name='Test Workspace',
            name='TestSlug'

        )

    def test_post_admin_boundary(self) -> None:
        self.client.force_authenticate(self.user)
        admin_data = admin_boundary_obj.copy()
        admin_data['workspace'] = self.workspace.id
        response = self.client.post(
            reverse('adminboundary-list'),
            admin_data,
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.get('name'), 'Test Admin')

    def test_get_admin_boundaries(self) -> None:
        self.client.force_authenticate(self.user)

        AdminBoundary.objects.create(name='Boundary 1', workspace=self.workspace)
        AdminBoundary.objects.create(name='Boundary 2', workspace=self.workspace)

        response = self.client.get(reverse('adminboundary-list'))

        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

    def test_get_admin_boundary_detail(self) -> None:
        self.client.force_authenticate(self.user)
        admin_boundary = AdminBoundary.objects.create(name='Admin Detail', workspace=self.workspace)

        response = self.client.get(
            reverse(
                'adminboundary-detail',
                kwargs=dict(boundary_uuid=admin_boundary.boundary_uuid)
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('id'), admin_boundary.id)

    def test_put_admin_boundary(self) -> None:
        self.client.force_authenticate(self.user)
        admin_boundary = AdminBoundary.objects.create(name='Admin Detail', workspace=self.workspace)
        updated_admin_boundary = dict(name='Updated Detail', workspace=self.workspace.id)

        response = self.client.put(
            reverse(
                'adminboundary-detail',
                kwargs=dict(boundary_uuid=admin_boundary.boundary_uuid)
            ),
            updated_admin_boundary,
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('name'), 'Updated Detail')

    def test_delete_admin_boundary(self) -> None:
        self.client.force_authenticate(self.user)
        admin_boundary = AdminBoundary.objects.create(name='Admin Detail', workspace=self.workspace)

        response = self.client.delete(
            reverse(
                'adminboundary-detail',
                kwargs=dict(boundary_uuid=admin_boundary.boundary_uuid)
            ),
        )

        self.assertEqual(response.status_code, 204)
        self.assertRaises(
            AdminBoundary.DoesNotExist,
            AdminBoundary.objects.get,
            id=admin_boundary.id
        )

    def get_admin_boundary_by_workspace(self) -> None:
        self.client.force_authenticate(self.user)
        workspace2 = Workspace.objects.create(name='Test Table 2', display_name='test')

        AdminBoundary.objects.create(name='Admin Bound 1', workspace=self.workspace)
        AdminBoundary.objects.create(name='Admin Bound 2', workspace=workspace2)
        AdminBoundary.objects.create(name='Admin Bound 3', workspace=workspace2)

        response = self.client.get(
            f'/api/adminboundary/?workspace__id={workspace2.id}'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        # test that all records belongs to the passed workspace
        for data in response.data:
            self.assertEqual(data.get('workspace'), workspace2.id)

    def get_admin_boundary_unauthenticated(self) -> None:
        response = self.client.get('adminboundary-list')
        self.assertEqual(response.status_code, 403)
