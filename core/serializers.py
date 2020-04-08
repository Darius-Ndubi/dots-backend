from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField('get_full_name')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'last_login', 'full_name')
        read_only_fields = ('username', 'last_login', 'full_name')

    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'

