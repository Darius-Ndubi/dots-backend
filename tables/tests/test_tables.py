from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from django.contrib.auth import get_user_model
from django.urls import reverse

from tables.models import Table


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

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='test',
            email='test@test.com',
            password='567389'
        )

    def test_post_table(self):
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

    def test_retrieve_table(self):
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

    def test_update_Table(self):
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

    def test_list_table(self):
        """
        Test Table List
        """
        self.client.force_authenticate(self.user)

        Table.objects.create(**self.table.copy())

        response = self.client.get(reverse('table-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

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
