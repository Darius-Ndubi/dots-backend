from django.contrib import admin

from .models import User, Membership, Workspace


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_active', 'is_superuser', 'is_staff')
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_filter = ['is_active', 'is_superuser', 'is_staff', 'last_login']


class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'workspace', 'get_workspace_slug', 'is_active', 'role', 'is_default')
    search_fields = ['workspace__slug', 'user__username']
    list_filter = ['workspace__slug', 'role', 'is_active']

    def get_workspace_slug(self, obj):
        return obj.workspace.slug
    get_workspace_slug.short_description = 'Workspace Slug'
    get_workspace_slug.admin_order_field = 'workspace__slug'


class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ['name', 'slug']


admin.site.register(User, UserAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(Workspace, WorkspaceAdmin)
