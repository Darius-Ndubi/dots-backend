from rest_framework import serializers

from .models import (Layer,)


class LayerSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    layer_uuid = serializers.ReadOnlyField()

    class Meta:
        model = Layer
        fields = '__all__'
