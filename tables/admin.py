from django.contrib import admin

from .models import (Table,)


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'source', 'create_date', 'update_date'
    )
    list_filter = ('owner', 'source',)
