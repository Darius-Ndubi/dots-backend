from rest_framework import serializers
from .models import Table


class TableSerializer(serializers.HyperlinkedModelSerializer):
    table_uuid = serializers.ReadOnlyField()
    owner = serializers.ReadOnlyField()
    url = serializers.HyperlinkedIdentityField(
        view_name='table-detail',
        lookup_field='table_uuid'
    )

    class Meta:
        model = Table
        fields = '__all__'
