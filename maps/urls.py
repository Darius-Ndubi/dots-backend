from rest_framework import routers
from .views import (LayerViewSet,)

router = routers.SimpleRouter()

router.register('layer', LayerViewSet)
urlpatterns = router.urls
