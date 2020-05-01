from django.contrib.auth import get_user_model
from django.db.models import OuterRef, Subquery
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView, ListCreateAPIView, ListAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from core import serializers
from core.models import Workspace, Membership
from core.permissions import WorkspacePermissions, WorkspaceUserPermissions

User = get_user_model()


class UserView(RetrieveUpdateAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserRegistrationView(GenericAPIView):
    serializer_class = serializers.UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
        return Response(data, status=status.HTTP_201_CREATED)


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


class WorkspaceUsersView(ListAPIView, UpdateModelMixin, GenericViewSet):
    serializer_class = serializers.WorkspaceUserSerializer
    permission_classes = [IsAuthenticated, WorkspaceUserPermissions]
    queryset = User.objects.filter()

    def get_queryset(self):
        membership = Membership.objects.filter(
            workspace=self.kwargs['workspace_id'], user=OuterRef('id')
        ).values('role')
        return self.queryset.filter(
            membership__workspace=self.kwargs['workspace_id'],
        ).annotate(role=Subquery(membership))

    def perform_update(self, serializer):
        serializer.save()
        new_role = serializer.validated_data.get('role')
        if not new_role:
            return

        workspace_id = self.kwargs['workspace_id']
        user_id = self.kwargs['pk']
        Membership.objects.filter(workspace=workspace_id, user=user_id).update(role=new_role)
