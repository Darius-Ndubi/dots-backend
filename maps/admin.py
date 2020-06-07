from django.contrib import admin

from .models import MapLayer


@admin.register(MapLayer)
class LayerAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'table', 'layer_type', 'created_by'
    )
    list_filter = ('table', 'created_by', 'layer_type',)

