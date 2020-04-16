from django.db import IntegrityError
from django.conf import settings as app_settings

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status

from pymongo import MongoClient

from .models import Table
from .serializers import TableSerializer
from .utils import process_data


class TableViewSet(viewsets.ModelViewSet):
    """
    Tables view
    Creates a Table model and dumps the dataset to mongo
    """
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    lookup_field = 'table_uuid'

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(owner=request.user)
        serializer = TableSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        try:
            request_data = request.data
            data = process_data(
                request_data.pop('data'), request_data.get('source')
            )
        except (ValueError, KeyError) as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request_data)

        if serializer.is_valid(raise_exception=True):
            try:
                self.perform_create(serializer)
                mongo_client = MongoClient(app_settings.MONGO_URI)
                connection = mongo_client[request_data.name]
                connection.insert_many(data)

                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            except IntegrityError as e:
                return Response(e, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        # set owner
        user = self.request.user
        serializer.save(owner=user.id)
