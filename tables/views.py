from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status

from .models import Table
from .serializers import TableSerializer
from .utils import process_data


class TableViewSet(viewsets.ModelViewSet):
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
            data = process_data(
                request.data.get('data'), request.data.get('source')
            )
        except (ValueError, KeyError) as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)


