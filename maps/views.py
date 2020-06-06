from rest_framework import (viewsets, permissions, )

from django_filters.rest_framework import (DjangoFilterBackend,)

from .models import (MapLayer, )
from .serializers import (MapLayerSerializer, )


class MapLayerViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    model = MapLayer
    queryset = MapLayer.objects.all()
    serializer_class = MapLayerSerializer

    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('table__table_uuid', 'table__id', 'table__workspace__id',)

    lookup_field = 'layer_uuid'

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


