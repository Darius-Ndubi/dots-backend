from rest_framework.permissions import BasePermission, SAFE_METHODS

from core.models import Membership


class WorkspacePermissions(BasePermission):
    def has_object_permission(self, request, view, ws):
        # Everyone create a new workspace
        if request.method is 'POST':
            return True

        # Everyone can get list of workspaces they are in
        if request.method in SAFE_METHODS:
            return True

        # Only Owner and Admins can update the workspace info
        return ws.membership.filter(
            user=request.user,
            role__in=[Membership.OWNER, Membership.ADMIN]
        )
