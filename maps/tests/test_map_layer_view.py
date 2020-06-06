from rest_framework.test import (APIClient, APITestCase, )

from django.contrib.auth import get_user_model
from django.urls import reverse

from ..models import MapLayer
from tables.models import Table
from core.models import Workspace

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
            name='Test Workspace',
            slug='TestSlug'

        )

        self.table: Table = Table.objects.create(
            name='Test Table',
            source='kobo',
            workspace=self.workspace
        )

    def test_post_layer(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(
            reverse('map-layer-list'),
            layer.update(dict(table=self.table)),
            type='json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.get('name'), 'Test Layer')

    def test_get_layers(self):
        self.client.force_authenticate(self.user)

        MapLayer.objects.create(name='Layer 1', layer_type='point', table=self.table)
        MapLayer.objects.create(name='Layer 2', layer_type='point', table=self.table)

        response = self.client.get(reverse('map-layer-list'))

        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

    def test_get_layer_detail(self):
        self.client.force_authenticate(self.user)
        layer1 = MapLayer.objects.create(name='Layer Detail', layer_type='point', table=self.table)

        response = self.client.get(
            reverse(
                'map-layer-detail',
                kwargs=dict(layer_uuid=layer1.layer_uuid)
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('id'), layer1.id)

    def test_put_layer(self):
        self.client.force_authenticate(self.user)
        layer2 = MapLayer.objects.create(name='Layer Detail', layer_type='point', table=self.table)
        updated_layer = dict(name='Updated Detail', layer_type='polygon', table=self.table)

        response = self.client.put(
            reverse(
                'map-layer-detail',
                kwargs=dict(layer_uuid=layer2.layer_uuid)
            ),
            updated_layer,
            type='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('layer_type'), 'polygon')
        self.assertEqual(response.data.get('name'), 'Updated Detail')

    def test_delete_layer(self):
        self.client.force_authenticate(self.user)
        layer3 = MapLayer.objects.create(name='Layer Detail', layer_type='point', table=self.table)

        response = self.client.delete(
            reverse(
                'map-layer-detail',
                kwargs=dict(layer_uuid=layer3.layer_uuid)
            ),
        )

        self.assertEqual(response.status_code, 204)
        self.assertRaises(
            MapLayer.DoesNotExist,
            MapLayer.objects.get,
            layer3.id
        )

    def get_layers_by_table(self):
        pass

    def get_layer_unauthenticated(self):
        response = self.client.get('map-layer-list')
        self.assertEqual(response.status_code, 403)

    def get_layer_with_no_active_workspace(self):
        pass
