from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    register_user,
    login_user,
    request_password_reset,
    reset_password,
    UserEmailTokenObtainView,
    SwaggerTokenRefreshView,
    UserViewSet,
    UserProfileView,
)

router = DefaultRouter()
router.register(r'accounts', UserViewSet, basename='user')

urlpatterns = [
    path('register/', register_user, name='register_user'),
    path('login/', login_user, name='login'),
    path('password-reset/', request_password_reset, name='request_password_reset'),
    path('password-reset/<uuid:token>/', reset_password, name='reset_password'),
    path('jwt/token/', UserEmailTokenObtainView.as_view(), name='token_obtain_pair'),
    path('jwt/refresh/', SwaggerTokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('', include(router.urls)),
]
