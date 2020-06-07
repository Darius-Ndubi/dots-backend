from rest_framework import serializers

from .models import (MapLayer, )


class MapLayerSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    layer_uuid = serializers.ReadOnlyField()

    class Meta:
        model = MapLayer
        fields = '__all__'
