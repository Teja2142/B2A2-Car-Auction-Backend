from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import DealerProfileViewSet, dealer_register, DealerEmailTokenObtainView

router = DefaultRouter()
router.register(r'dealer-profiles', DealerProfileViewSet, basename='dealerprofile')

urlpatterns = [
    path('register/', dealer_register, name='dealer_register'),
    path('login/', DealerEmailTokenObtainView.as_view(), name='dealer_login'),
]
urlpatterns += router.urls
