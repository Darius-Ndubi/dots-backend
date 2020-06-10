from rest_framework.test import (APIClient, APITestCase, )

from django.contrib.auth import get_user_model
from django.urls import reverse

from ..models import MapLayer
from tables.models import Table
from core.models import (Workspace, Membership,)

layer = dict(
    name='Test Layer',
    layer_type='point'
)


class LayerViewTestCase(APITestCase):
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

        self.member: Membership = Membership.objects.create(
            user=self.user,
            workspace=self.workspace,
            is_active=True
        )

        self.table: Table = Table.objects.create(
            name='Test Table',
            source='kobo',
            workspace=self.workspace
        )

    def test_post_layer(self) -> None:
        self.client.force_authenticate(self.user)
        layer_data = layer.copy()
        layer_data['table'] = self.table.id
        response = self.client.post(
            reverse('maplayer-list'),
            layer_data,
            type='json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.get('name'), 'Test Layer')

    def test_get_layers(self) -> None:
        self.client.force_authenticate(self.user)

        MapLayer.objects.create(name='Layer 1', layer_type='point', table=self.table)
        MapLayer.objects.create(name='Layer 2', layer_type='point', table=self.table)

        response = self.client.get(reverse('maplayer-list'))

        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

    def test_get_layer_detail(self) -> None:
        self.client.force_authenticate(self.user)
        layer1 = MapLayer.objects.create(name='Layer Detail', layer_type='point', table=self.table)

        response = self.client.get(
            reverse(
                'maplayer-detail',
                kwargs=dict(layer_uuid=layer1.layer_uuid)
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('id'), layer1.id)

    def test_put_layer(self) -> None:
        self.client.force_authenticate(self.user)
        layer2 = MapLayer.objects.create(name='Layer Detail', layer_type='point', table=self.table)
        updated_layer = dict(name='Updated Detail', layer_type='polygon', table=self.table.id)

        response = self.client.put(
            reverse(
                'maplayer-detail',
                kwargs=dict(layer_uuid=layer2.layer_uuid)
            ),
            updated_layer,
            type='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('layer_type'), 'polygon')
        self.assertEqual(response.data.get('name'), 'Updated Detail')

    def test_delete_layer(self) -> None:
        self.client.force_authenticate(self.user)
        layer3 = MapLayer.objects.create(name='Layer Detail', layer_type='point', table=self.table)

        response = self.client.delete(
            reverse(
                'maplayer-detail',
                kwargs=dict(layer_uuid=layer3.layer_uuid)
            ),
        )

        self.assertEqual(response.status_code, 204)
        self.assertRaises(
            MapLayer.DoesNotExist,
            MapLayer.objects.get,
            id=layer3.id
        )

    def get_layers_by_table(self) -> None:
        self.client.force_authenticate(self.user)
        table2 = Table.objects.create(name='Test Table 2', source='kobo', workspace=self.workspace)

        MapLayer.objects.create(name='Table Layer 1', layer_type='point', table=self.table)
        MapLayer.objects.create(name='Table Layer 2', layer_type='point', table=self.table)
        MapLayer.objects.create(name='Table Layer 3', layer_type='point', table=table2)

        response = self.client.get(
            f'/api/maplayer/?table__table_uuid={self.table.table_uuid}'
        )

        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

        # test that all records belongs to the current table
        for data in response.data:
            self.assertEqual(data.get('table'), self.table.id)

    def get_layer_unauthenticated(self) -> None:
        response = self.client.get('maplayer-list')
        self.assertEqual(response.status_code, 403)

    def get_layer_with_no_active_workspace(self) -> None:
        # deactivate membership
        self.member.is_active = False
        self.member.save()

        self.client.force_authenticate(self.user)

        MapLayer.objects.create(name='Table Layer 2', layer_type='point', table=self.table)

        response = self.client.get('maplayer-list')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
