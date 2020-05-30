from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView, ListCreateAPIView, ListAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt import views as jwt_views


from core import serializers
from core.models import Workspace, Membership
from core.permissions import WorkspacePermissions, WorkspaceUserPermissions


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

