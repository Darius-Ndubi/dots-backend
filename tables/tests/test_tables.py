from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from django.contrib.auth import get_user_model
from django.urls import reverse

from tables.models import Table
from core.models import (Workspace,)


class TableViewTestCase(APITestCase):
    """
    Table View Test
    """

    file = {
        'filename': 'data',
        'filetype': 'text/csv',
        'value': 'YSxiLGMKMSwyLDMKNCw1LDYK'
    }

    table = {
        'name': 'Test Table',
        'source': 'csv',
        'unique_column': '',
    }

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='test',
            email='test@test.com',
            password='567389'
        )

        self.workspace: Workspace = Workspace.objects.create(
            display_name='Test Name',
            name='Test'
        )

    def test_post_table(self) -> None:
        """
        Test Table Post
        """
        self.client.force_authenticate(self.user)
        data = self.table.copy()
        data['data'] = self.file
        response = self.client.post(
            reverse('table-list'),
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_table(self) -> None:
        """
        Test Table Retrieve
        """
        self.client.force_authenticate(self.user)

        data = self.table.copy()
        data['data'] = self.file
        post_request = self.client.post(
            reverse('table-list'),
            data,
            format='json'
        )

        response = self.client.get(
            reverse(
                'table-detail',
                kwargs={'table_uuid': post_request.data['table_uuid']}
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Table')
        self.assertIsNotNone(response.data.get('data'))

    def test_update_Table(self) -> None:
        """
        Test Table Update
        """
        self.client.force_authenticate(self.user)

        table = Table.objects.create(**self.table.copy())

        response = self.client.put(
            reverse(
                'table-detail',
                kwargs={'table_uuid': table.table_uuid}
            ),
            {'name': 'Test Table Edited', 'source': 'csv'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Table Edited')

    def test_list_table(self) -> None:
        """
        Test Table List
        """
        self.client.force_authenticate(self.user)

        Table.objects.create(**self.table.copy())

        response = self.client.get(reverse('table-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_list_table_by_workspace_id(self) -> None:
        """
        Test Table List when workspace id is passed
        """
        self.client.force_authenticate(self.user)
        # create first table
        Table.objects.create(name='Test Table 1', source='kobo')

        # create second table and tie it to Workspace
        table_data = self.table.copy()
        table_data.update(dict(workspace=self.workspace))
        Table.objects.create(**table_data)

        response = self.client.get(f'/api/tables/?workspace__id={self.workspace.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_table_by_workspace_name(self) -> None:
        """
        Test Table List with workspace name
        """
        self.client.force_authenticate(self.user)
        # create first table
        Table.objects.create(name='Test Table 2', source='kobo')

        # create second table and tie it to Workspace
        table_data = self.table.copy()
        table_data.update(dict(workspace=self.workspace))
        Table.objects.create(**table_data)

        response = self.client.get(f'/api/tables/?workspace__name={self.workspace.name}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0].get('name'), 'Test Table')

    def test_delete_table(self):
        """
        Test Table Delete
        """
        self.client.force_authenticate(self.user)

        table = Table.objects.create(**self.table.copy())

        response = self.client.delete(
            reverse(
                'table-detail',
                kwargs={'table_uuid': table.table_uuid}
            )
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertRaises(
            Table.DoesNotExist,
            Table.objects.get,
            table_uuid=table.table_uuid
        )
