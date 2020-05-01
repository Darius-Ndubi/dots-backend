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


class WorkspaceUserPermissions(BasePermission):
    def has_permission(self, request, view):
        workspace_id = view.kwargs.get('workspace_id')
        return Membership.objects.filter(
            workspace=workspace_id, is_active=True, user=request.user
        ).exists()

    def has_object_permission(self, request, view, user):
        workspace_id = view.kwargs.get('workspace_id')
        # Can not update your own status
        if user.id == request.user.id:
            return False

        # Only Owner and Admins can update the workspace user
        user_m = user.membership.filter(workspace_id=workspace_id).first()

        admin_m = Membership.objects.filter(
            user=request.user,
            role__in=[Membership.OWNER, Membership.ADMIN],
            is_active=True,
            workspace_id=workspace_id
        ).first()

        # If the user who is performing action is not admin/owner then deny permission
        if not admin_m:
            return False

        # If the user who is performing action has not higher permissions than the
        # resource they are trying to update then deny permissions
        if admin_m.role == Membership.OWNER and user_m.role == Membership.OWNER:
            return False

        if admin_m.role == Membership.ADMIN and user_m.role != Membership.MEMBER:
            return False

        return True
