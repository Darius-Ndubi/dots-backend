from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import User, Membership, Workspace


class UserAdmin(SimpleHistoryAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_active', 'is_superuser', 'is_staff')
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_filter = ['is_active', 'is_superuser', 'is_staff', 'last_login']


class MembershipAdmin(SimpleHistoryAdmin):
    list_display = ('user', 'workspace', 'get_workspace_name', 'is_active', 'role', 'is_default')
    search_fields = ['workspace__name', 'user__username']
    list_filter = ['workspace__name', 'role', 'is_active']

    def get_workspace_name(self, obj):
        return obj.workspace.name
    get_workspace_name.short_description = 'Workspace Name'
    get_workspace_name.admin_order_field = 'workspace__name'


class WorkspaceAdmin(SimpleHistoryAdmin):
    list_display = ('display_name', 'name')
    search_fields = ['display_name', 'name']


admin.site.register(User, UserAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(Workspace, WorkspaceAdmin)
