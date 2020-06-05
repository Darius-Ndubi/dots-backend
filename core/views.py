from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView, ListCreateAPIView, ListAPIView, CreateAPIView
from rest_framework.mixins import UpdateModelMixin, CreateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt import views as jwt_views


from core import serializers
from core.models import Workspace, Membership, UserActivation, WorkspaceInvitation
from core.permissions import WorkspacePermissions, WorkspaceUserPermissions, IsGetOrIsAuthenticated, \
    IsWorkspaceAdminOrOwner
from core.util.emails import send_activation_email, send_invitation_email
from core.util.key_generation import create_activation_key

User = get_user_model()


class UserView(RetrieveUpdateAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['register']
))
class UserRegistrationView(GenericAPIView):
    serializer_class = serializers.UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        activation = create_activation_key(user)
        send_activation_email(user, activation)
        return Response({}, status=status.HTTP_201_CREATED)


class WorkspaceView(ListCreateAPIView, UpdateModelMixin, GenericViewSet):
    serializer_class = serializers.WorkspaceSerializer
    permission_classes = [IsAuthenticated, WorkspacePermissions]
    queryset = Workspace.objects.filter()

    def get_queryset(self):
        return self.queryset.filter(
            membership__user=self.request.user,
            membership__is_active=True
        )

    def perform_create(self, serializer):
        ws = serializer.save()
        Membership.objects.filter(user=self.request.user).update(is_default=False)
        Membership(workspace=ws, user=self.request.user,
                   role=Membership.OWNER, is_default=True).save()


@method_decorator(name='list', decorator=swagger_auto_schema(
    tags=['workspace users']
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    tags=['workspace users']
))
class WorkspaceUsersView(ListAPIView, UpdateModelMixin, GenericViewSet):
    serializer_class = serializers.WorkspaceUserSerializer
    permission_classes = [IsAuthenticated, WorkspaceUserPermissions]
    queryset = Membership.objects.filter()

    def get_queryset(self):
        return self.queryset.filter(
            workspace=self.kwargs['workspace_id'],
        ).select_related('user')


class TokenObtainPairView(jwt_views.TokenObtainPairView):
    serializer_class = serializers.TokenObtainPairSerializer


class UserActivationView(APIView):
    def get(self, request, activation_key):
        activation = UserActivation.objects.filter(key=activation_key).first()
        if not activation:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user = activation.user
        user.is_active = True
        user.save()
        activation.delete()
        return Response(status=status.HTTP_201_CREATED)


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['user invitation']
))
@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['user invitation']
))
class UserInvitationView(APIView):
    permission_classes = [IsGetOrIsAuthenticated]

    def get(self, request, invitation_key):
        invitation = WorkspaceInvitation.objects.filter(key=invitation_key).first()
        if not invitation:
            return Response({
                'not_found': 'Invalid invite.'
            }, status=status.HTTP_404_NOT_FOUND)

        registered = User.objects.filter(email__iexact=invitation.email).exists()
        if registered:
            return Response({
                'require_login': 'Please login to accept invite.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # If invite is for new user return invite info to autofill the signup form.
        return Response({
            'no_user_found': 'No user found.',
            'email': invitation.email,
            'first_name': invitation.first_name,
            'last_name': invitation.last_name,
        }, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, invitation_key):
        invitation = WorkspaceInvitation.objects.filter(key=invitation_key).first()
        if not invitation:
            return Response({
                'not_found': 'Invalid invite.'
            }, status=status.HTTP_404_NOT_FOUND)

        if request.user.email.lower() != invitation.email.lower():
            return Response({
                'wrong_user': 'Please login/register with the email on which invite was sent.'
            }, status=status.HTTP_400_BAD_REQUEST)

        Membership.objects.filter(user=request.user).update(is_default=False)
        Membership.objects.create(
            is_default=True,
            workspace=invitation.workspace,
            user=request.user
        )
        invitation.delete()
        return Response(status=status.HTTP_200_OK)


class WorkspaceInvitationView(ListAPIView, CreateModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = serializers.WorkspaceInvitationReadSerializer
    permission_classes = [IsAuthenticated, IsWorkspaceAdminOrOwner]
    queryset = WorkspaceInvitation.objects.filter()

    def get_queryset(self):
        return self.queryset.filter(
            workspace=self.kwargs['workspace_id'],
        )

    def create(self, request, *args, **kwargs):
        request.data['workspace'] = self.kwargs['workspace_id']
        serializer = serializers.WorkspaceInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invitation = serializer.save()
        send_invitation_email(invitation)
        return Response({}, status=status.HTTP_201_CREATED)
