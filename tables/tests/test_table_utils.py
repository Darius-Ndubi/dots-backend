from rest_framework.test import (APIClient, APITestCase)

from django.contrib.auth import (get_user_model, )
from tables.utils import (get_feature, )

SAMPLE_TABLE_DATA = dict(
    metadata=dict(
        longitude_field='longitude',
        latitude_field='latitude',
        tool_tip_field='test'
    ),
    table_uuid='4567890-rtyuio-tyui',
    data=[
        dict(latitude=23.45, longitude=45.78, test='Test Label'),
        dict(latitude=3.45, longitude=55.78, test='Test Label 1'),
        dict(latitude=-23.45, longitude=-45.78, test='Test Label 2')
    ]
)

GEO_JSON_DATA = dict(
    type='FeatureCollection',
    features=[
        dict(
            type='Feature',
            geometry=dict(
                coordinates=[45.78, 23.45],
                type='Point'
            ),
            properties=dict(title='Test Label', icon='rocket')
        ),
        dict(
            type='Feature',
            geometry=dict(
                coordinates=[55.78, 3.45],
                type='Point'
            ),
            properties=dict(title='Test Label 1', icon='rocket')
        ),
        dict(
            type='Feature',
            geometry=dict(
                coordinates=[-45.78, -23.45],
                type='Point'
            ),
            properties=dict(title='Test Label 2', icon='rocket')
        )
    ]
)


class TableUtilsTestCase(APITestCase):
    """
    Test table utils
    """

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='test',
            email='test@test.com',
            password='567389'
        )

    def test_geo_json_get_feature(self):
        data = get_feature(
            SAMPLE_TABLE_DATA['data'][0],
            'longitude',
            'latitude',
            None,
            'test'
        )

        self.assertIsNotNone(data)
        self.assertEqual(data, GEO_JSON_DATA['features'][0])

