from django.contrib.auth import get_user_model

from rest_framework import serializers

from core.models import Workspace


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField('get_full_name')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'last_login', 'full_name', 'title')
        read_only_fields = ('username', 'last_login', 'full_name')

    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'


class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': ['Passwords do not match.']})
        if User.objects.filter(username__iexact=data['username']).exists():
            raise serializers.ValidationError({'username': ['Username already in use.']})
        if User.objects.filter(email__iexact=data['email']).exists():
            raise serializers.ValidationError({'email': ['Email already in use.']})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        return User.objects.create_user(**validated_data)


class WorkspaceSerializer(serializers.ModelSerializer):
    is_default = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = '__all__'

    def _membership(self, ws):
        return ws.membership.filter(user=self.context['request'].user).first()

    def get_is_default(self, ws):
        return self._membership(ws).is_default

    def get_role(self, ws):
        return self._membership(ws).role


class WorkspaceUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField('get_full_name')

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'last_login', 'full_name', 'is_active')
        read_only_fields = ('id', 'username', 'email', 'last_login', 'full_name')

    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'
