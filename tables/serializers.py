from rest_framework import serializers

from .models import Table
from .utils import connect_to_mongo


class TableSerializer(serializers.ModelSerializer):
    table_uuid = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField()

    class Meta:
        model = Table
        fields = '__all__'


class TableDetailSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Table
        fields = '__all__'

    def get_data(self, obj):
        mongo_client = connect_to_mongo()
        connection = mongo_client[obj.name.replace(' ', '_')]
        data = connection.find_one({'table_uuid': str(obj.table_uuid)})
        # temporarily delete _id property
        if data is not None:
            del data['_id']
        return data



