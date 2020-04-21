from dots.router import OptionalSlashRouter
from .views import TableViewSet

router = OptionalSlashRouter()

router.register('tables', TableViewSet)

urlpatterns = router.urls
