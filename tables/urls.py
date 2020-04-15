from rest_framework import routers

from .views import TableViewSet

router = routers.SimpleRouter()

router.register('tables', TableViewSet)

urlpatterns = router.urls
