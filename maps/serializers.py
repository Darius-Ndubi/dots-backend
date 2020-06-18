from rest_framework import serializers

from .models import (MapLayer, AdminBoundary, )
from .utils import (connect_to_mongo, )


class MapLayerSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    layer_uuid = serializers.ReadOnlyField()

    class Meta:
        model = MapLayer
        fields = '__all__'


class MapLayerDetailSerializer(serializers.ModelSerializer):
    geo_data = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MapLayer
        fields = '__all__'

    def get_geo_data(self, obj: MapLayer):
        mongo_client = connect_to_mongo()
        connection = mongo_client['dots_layer_data']
        data = connection.find_one({'layer_uuid': str(obj.layer_uuid)}, {'geo_data': 1})
        if data:
            return data.get('geo_data', None)
        return None


class AdminBoundarySerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminBoundary
        fields = '__all__'
