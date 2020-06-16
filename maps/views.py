from rest_framework import (viewsets, permissions, )

from django_filters.rest_framework import (DjangoFilterBackend, )

from .models import (MapLayer, )
from .serializers import (MapLayerSerializer, MapLayerDetailSerializer)
from .utils import (generate_geojson_point_data,)


class MapLayerViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    model = MapLayer
    queryset = MapLayer.objects.all()
    serializer_class = MapLayerSerializer

    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('table__table_uuid', 'table__id', 'table__workspace__id',)

    lookup_field = 'layer_uuid'

    def perform_create(self, serializer):
        layer: MapLayer = serializer.save(created_by=self.request.user)
        # generate geojson data and save to Mongo
        if layer.layer_type == 'point':
            generate_geojson_point_data(layer)

    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action == 'retrieve':
            return MapLayerDetailSerializer
        return MapLayerSerializer
