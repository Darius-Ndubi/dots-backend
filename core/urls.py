from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from dots.router import OptionalSlashRouter
from . import views


api_router = OptionalSlashRouter()
api_router.register('workspace', views.WorkspaceView)


urlpatterns = [
    path('', include(api_router.urls)),
    path('user', views.UserView.as_view()),
    path('user/register', views.UserRegistrationView.as_view()),
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]
