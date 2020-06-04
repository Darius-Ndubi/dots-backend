from rest_framework.test import (APIClient, APITestCase,)

from django.contrib.auth import get_user_model


class LayerViewTestCase(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            username='test',
            email='test.hikaya.io',
            password='TestUser'
        )

    def test_post_layer(self):
        pass

    def test_get_layers(self):
        pass

    def test_get_layer_detail(self):
        pass

    def test_put_layer(self):
        pass

    def test_delete_layer(self):
        pass

    def get_layers_by_table(self):
        pass

    def get_layer_unauthenticated(self):
        pass

    def get_layer_with_no_active_workspace(self):
        pass
