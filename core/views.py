from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from core import serializers


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
