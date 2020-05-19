from django.db import IntegrityError

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .models import Table
from .serializers import (TableSerializer, TableDetailSerializer)
from .utils import (
    process_data, connect_to_mongo, generate_geojson_data,
    get_data_source_forms,
)


class TableViewSet(viewsets.ModelViewSet):
    """
    Tables view
    Creates a Table model and dumps the dataset to mongo
    """
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    lookup_field = 'table_uuid'

    def create(self, request, *args, **kwargs):
        try:
            request_data = request.data
            data = process_data(
                request_data.pop('data'), request_data.get('source')
            )
        except (ValueError, KeyError) as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(
            data=request_data, context={'request': self.request}
        )

        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)

            # generate mongoData
            mongo_data = {
                'data': data,
                'table_uuid': str(serializer.data.get('table_uuid'))
            }
            mongo_client = connect_to_mongo()
            connection = mongo_client[request_data.get('name').replace(' ', '_')]
            connection.insert_one(mongo_data)

            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        except IntegrityError as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action == 'retrieve':
            return TableDetailSerializer
        return TableSerializer


class TableGeoJsonView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        table_uuid = kwargs.get('table_uuid', None)
        if table_uuid is None:
            return Response(
                dict(error='Table UUID is required'),
                status=status.HTTP_400_BAD_REQUES
            )
        try:
            table = Table.objects.get(table_uuid=table_uuid)
            geo_json_data = generate_geojson_data(table)

            return Response(
                dict(data=geo_json_data),
                status=status.HTTP_200_OK
            )
        except Table.DoesNotExist:
            return Response(
                dict(error='Table with the does not exist'),
                status=status.HTTP_400_BAD_REQUES
            )


class ThirdPartyImportView(APIView):
    """
    Get 3rd party forms based on source
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        source = request.GET.get('source', None)
        if source is None:
            return Response(
                dict(error='Please pass data source'),
                status=status.HTTP_400_BAD_REQUEST
            )

        source_forms = get_data_source_forms(source)
        return Response(source_forms, status=status.HTTP_200_OK)




