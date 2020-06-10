from django.contrib.auth import get_user_model, user_logged_in

from rest_framework import serializers, exceptions
from rest_framework.validators import UniqueTogetherValidator
from rest_framework_simplejwt import serializers as jwt_serializers

from core.models import Workspace, Membership, WorkspaceInvitation, PasswordResetToken
from core.util.emails import send_password_reset_email
from core.util.key_generation import create_invitation_key, create_password_reset_key

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

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
    invitation_key = serializers.CharField(required=False)

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
        validated_data['is_active'] = False
        invitation_key = validated_data.pop('invitation_key', None)

        user = User.objects.create_user(**validated_data)

        invitation = WorkspaceInvitation.objects.filter(key=invitation_key).first()
        if invitation:
            Membership.objects.filter(user=user).update(is_default=False)
            Membership.objects.create(
                is_default=True,
                workspace=invitation.workspace,
                user=user
            )
            invitation.delete()
        return user


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
    full_name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    last_login = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = ('id', 'username', 'email', 'last_login', 'full_name', 'is_active', 'role')
        read_only_fields = ('id', 'username', 'email', 'last_login', 'full_name')

    def get_full_name(self, m):
        return f'{m.user.first_name} {m.user.last_name}'

    def get_username(self, m):
        return m.user.username

    def get_email(self, m):
        return m.user.email

    def get_last_login(self, m):
        return m.user.last_login


class TokenObtainPairSerializer(jwt_serializers.TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
        except exceptions.AuthenticationFailed as e:
            if self.user and not self.user.is_active:
                raise serializers.ValidationError({
                    'not_verified': 'Email is not verified'
                })
            raise e

        user_logged_in.send(
            sender=self.__class__,
            user=self.user,
            is_new=not self.user.last_login)
        return data


class WorkspaceInvitationReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceInvitation
        exclude = ('key', 'workspace')


class WorkspaceInvitationSerializer(serializers.ModelSerializer):
    key = serializers.CharField(required=False)

    class Meta:
        model = WorkspaceInvitation
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=WorkspaceInvitation.objects.all(),
                fields=['email', 'workspace'],
                message='This email is already invited.'
            )
        ]

    def validate(self, data):
        data['key'] = create_invitation_key(
            data['workspace'],
            data['email']
        )
        return super().validate(data)


class PasswordUpdateSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, data):
        current_password = data['current_password']
        new_password = data['new_password']
        confirm_new_password = data['confirm_new_password']

        user = self.context['request'].user
        if not user.check_password(current_password):
            raise serializers.ValidationError({
                'current_password': "Current password isn't correct."
            })

        if confirm_new_password != new_password:
            raise serializers.ValidationError("New passwords don't match.")

        if current_password == new_password:
            raise serializers.ValidationError("New password can't be same as current one.")

        return super().validate(data)

    def save(self):
        new_password = self.validated_data['new_password']
        user = self.context['request'].user
        user.set_password(new_password)
        user.save()


class PasswordRestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    token = serializers.CharField(required=False)
    new_password = serializers.CharField(required=False)
    confirm_new_password = serializers.CharField(required=False)

    def validate(self, data):
        email = data.get('email')
        token = data.get('token')
        if not token and not email:
            raise serializers.ValidationError("Either token or email is required.")
        if email:
            user = User.objects.filter(email__iexact=email).first()
            self.context['user'] = user
            return super().validate(data)

        new_password = data.get('new_password')
        confirm_new_password = data.get('confirm_new_password')
        if not new_password:
            raise serializers.ValidationError({
                'new_password': "New password is required."
            })
        if not confirm_new_password:
            raise serializers.ValidationError({
                'confirm_new_password': "Confirm new password is required."
            })

        if confirm_new_password != new_password:
            raise serializers.ValidationError("New passwords don't match.")

        token = PasswordResetToken.objects.filter(key=token).last()
        if not token:
            raise serializers.ValidationError({
                'token': "Invalid or expired token."
            })

        self.context['user'] = token.user
        return super().validate(data)

    def save(self):
        email = self.validated_data.get('email')
        user = self.context['user']
        if email:
            if not user:
                return
            reset_token = create_password_reset_key(user)
            send_password_reset_email(user, reset_token)
            return

        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        PasswordResetToken.objects.filter(user=user).delete()
