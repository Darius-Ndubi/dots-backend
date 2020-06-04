from rest_framework import (viewsets, permissions, )

from .models import (Layer, )
from .serializers import (LayerSerializer, )


class LayerViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    model = Layer
    queryset = Layer.objects.all()
    serializer_class = LayerSerializer
    lookup_field = 'layer_uuid'

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(modified_by=self.request.user)

    def get_queryset(self):
        return super(LayerViewSet, self).get_queryset().filter(
            table__workspace__membership__user=self.request.user,
            table__workspace__membership__is_active=True
        )
