from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from dots.router import OptionalSlashRouter
from . import views

api_router = OptionalSlashRouter()
api_router.register('workspace', views.WorkspaceView)


urlpatterns = [
    path('', include(api_router.urls)),
    path('user', views.UserView.as_view()),
    path('user/register', views.UserRegistrationView.as_view()),
    path('user/invite/<slug:invitation_key>', views.UserInvitationView.as_view()),
    path('user/update_password', views.PasswordUpdateView.as_view()),
    path('user/reset_password', views.PasswordResetView.as_view()),
    path('activate/<slug:activation_key>', views.UserActivationView.as_view()),
    path('workspace/<int:workspace_id>/invite', views.WorkspaceInvitationView.as_view({
        'get': 'list', 'post': 'create', 'delete': 'destroy'
    })),
    path('workspace/<int:workspace_id>/users', views.WorkspaceUsersView.as_view({'get': 'list'})),
    path('workspace/<int:workspace_id>/set_default', views.WorkspaceSetDefaultView.as_view()),
    path('workspace/<int:workspace_id>/users/<int:pk>', views.WorkspaceUsersView.as_view({'patch': 'update'})),
    path('token', views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]
