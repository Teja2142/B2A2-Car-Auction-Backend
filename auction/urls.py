from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehicleViewSet, AuctionViewSet, BidViewSet, create_vehicle

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet)
router.register(r'auctions', AuctionViewSet)
router.register(r'bids', BidViewSet)

urlpatterns = [
    path('vehicles/create/', create_vehicle, name="create-vehicle"),
    path('', include(router.urls)),                         # Default ViewSets
]


