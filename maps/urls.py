from rest_framework import routers
from .views import (MapLayerViewSet, AdminBoundaryViewSet,)

router = routers.SimpleRouter()

router.register('maplayer', MapLayerViewSet)
router.register('adminboundary', AdminBoundaryViewSet)
urlpatterns = router.urls
