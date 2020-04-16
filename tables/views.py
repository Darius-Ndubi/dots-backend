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
        queryset = self.get_queryset()
        serializer = TableSerializer(
            queryset, many=True, context={'request': self.request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        try:
            request_data = request.data
            data = process_data(
                request_data.pop('data'), request_data.get('source')
            )
        except (ValueError, KeyError) as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)

        request_data['owner'] = request.user.id
        serializer = self.get_serializer(
            data=request_data, context={'request': self.request}
        )

        if serializer.is_valid(raise_exception=True):
            try:
                self.perform_create(serializer)

                # generate mongoData
                mongo_data = {
                    'data': data,
                    'table_uuid': str(serializer.data.get('table_uuid'))
                }
                mongo_client = MongoClient(app_settings.MONGO_URI)
                db_client = mongo_client[app_settings.MONGO_DB_NAME]
                connection = db_client[request_data.get('name').replace(' ', '_')]
                connection.insert_one(mongo_data)

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
        serializer.save()
