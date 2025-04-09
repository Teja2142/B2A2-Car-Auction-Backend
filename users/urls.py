from django.urls import path
from .views import register_user, login_user, request_password_reset, reset_password
from .views import CustomObtainAuthToken

urlpatterns = [
    path('register/', register_user, name='register_user'),
    path('login/', login_user, name='login'),
    path('password-reset/', request_password_reset, name='request_password_reset'),
    path('password-reset/<uuid:token>/', reset_password, name='reset_password'),
    path('login-token/', CustomObtainAuthToken.as_view(), name='custom_token_auth'),
]
