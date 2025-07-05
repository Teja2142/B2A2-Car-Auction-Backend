from rest_framework.routers import DefaultRouter
from .views import VehicleViewSet, VehicleImageViewSet

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'vehicle-images', VehicleImageViewSet, basename='vehicleimage')

urlpatterns = router.urls
