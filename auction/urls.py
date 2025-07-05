from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuctionViewSet, BidViewSet, PlaceBidView

router = DefaultRouter()
router.register(r'auctions', AuctionViewSet, basename='auction')
router.register(r'bids', BidViewSet, basename='bid')

urlpatterns = [
    path('', include(router.urls)),
    path('place-bid/', PlaceBidView.as_view(), name='place-bid'),
]


