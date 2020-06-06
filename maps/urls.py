from rest_framework import routers
from .views import (MapLayerViewSet,)

router = routers.SimpleRouter()

router.register('maplayer', MapLayerViewSet)
urlpatterns = router.urls
