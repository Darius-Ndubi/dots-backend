from rest_framework import serializers

from .models import (MapLayer, )


class MapLayerSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    layer_uuid = serializers.ReadOnlyField()

    class Meta:
        model = MapLayer
        fields = '__all__'


class MapLayerDetailSerializer(serializers.ModelSerializer):
    geodata = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MapLayer
        fields = '__all__'

    def get_data(self, obj):
        mongo_client = connect_to_mongo()
        connection = mongo_client[obj.name.replace(' ', '_')]
        data = connection.find_one({'table_uuid': str(obj.table_uuid)})
        # temporarily delete _id property
        if data is not None:
            del data['_id']
        return data