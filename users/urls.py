from django.urls import path
from .views import register_user, login_user, request_password_reset, reset_password, home

urlpatterns = [
    path('api/register', register_user, name='register_user'),
    path('api/login', login_user, name='login'),
    path('api/password-reset', request_password_reset, name='request_password_reset'),
    path('api/password-reset/<uuid:token>', reset_password, name='reset_password'),
]
