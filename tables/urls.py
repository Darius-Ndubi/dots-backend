from django.urls import path

from dots.router import OptionalSlashRouter
from .views import (TableViewSet, TableGeoJsonView, ThirdPartyImportView,)

router = OptionalSlashRouter()

router.register('tables', TableViewSet)

urlpatterns = router.urls

urlpatterns += [
    path(
        'tables/geojson/<slug:table_uuid>/',
        TableGeoJsonView.as_view(),
        name='table_map_geojson'
    ),
    path(
        'tables/data/forms/',
        ThirdPartyImportView.as_view(),
        name='get_forms'
    )
]
