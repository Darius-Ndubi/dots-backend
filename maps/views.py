from rest_framework import (viewsets, )

from .models import (Layer, )
from .serializers import (LayerSerializer, )


class LayerViewSet(viewsets.ModelViewSet):
    model = Layer
    queryset = Layer.objects.all()
    serializer_class = LayerSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(last_modified_by=self.request.user)
