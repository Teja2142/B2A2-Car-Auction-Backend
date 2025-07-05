from rest_framework import viewsets, permissions, status, generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes, parser_classes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.timezone import now

from .models import Auction, Bid
from .serializers import AuctionSerializer, BidSerializer

# Home page (public)
@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    from django.shortcuts import render
    return render(request, 'index.html')

# Auction ViewSet
class AuctionViewSet(viewsets.ModelViewSet):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'  # Use UUID for lookup
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['vehicle', 'start_time', 'end_time', 'highest_bidder']
    search_fields = ['vehicle__make', 'vehicle__model', 'highest_bidder__email']
    ordering_fields = ['start_time', 'end_time', 'starting_price', 'highest_bid']
    ordering = ['-start_time']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @swagger_auto_schema(
        operation_description="Create a new auction.",
        request_body=AuctionSerializer,
        responses={201: AuctionSerializer, 400: 'Validation error'},
        manual_parameters=[],
        tags=['auction']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update an auction (partial or full).",
        request_body=AuctionSerializer,
        responses={200: AuctionSerializer, 400: 'Validation error'},
        manual_parameters=[],
        tags=['auction']
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['auction'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['auction'],
        operation_description="List all auctions. Supports search, ordering, and filtering.",
        manual_parameters=[
            openapi.Parameter(
                'search', openapi.IN_QUERY, description="Search by vehicle make, model, or highest bidder email.", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'ordering', openapi.IN_QUERY, description="Order by start_time, end_time, starting_price, or highest_bid. Example: ordering=-start_time",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'vehicle', openapi.IN_QUERY, description="Filter by vehicle ID.", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'start_time', openapi.IN_QUERY, description="Filter by auction start time (YYYY-MM-DD).", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'end_time', openapi.IN_QUERY, description="Filter by auction end time (YYYY-MM-DD).", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'highest_bidder', openapi.IN_QUERY, description="Filter by highest bidder user ID.", type=openapi.TYPE_STRING
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['auction'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['auction'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(tags=['auction'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

# Bid ViewSet
class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'  # Use UUID for lookup
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['auction', 'bidder']
    search_fields = ['auction__vehicle__make', 'auction__vehicle__model', 'bidder__email']
    ordering_fields = ['timestamp', 'bid_amount']
    ordering = ['-timestamp']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @swagger_auto_schema(
        operation_description="Create a new bid.",
        request_body=BidSerializer,
        responses={201: BidSerializer, 400: 'Validation error'},
        manual_parameters=[],
        tags=['auction']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a bid (partial or full).",
        request_body=BidSerializer,
        responses={200: BidSerializer, 400: 'Validation error'},
        manual_parameters=[],
        tags=['auction']
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['auction'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['auction'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(tags=['auction'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(bidder=self.request.user)

    @swagger_auto_schema(tags=['auction'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['auction'],
        operation_description="List all bids. Supports search, ordering, and filtering.",
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search by auction vehicle make/model or bidder email.", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Order by timestamp or bid_amount. Example: ordering=-timestamp", type=openapi.TYPE_STRING),
            openapi.Parameter('auction', openapi.IN_QUERY, description="Filter by auction ID.", type=openapi.TYPE_STRING),
            openapi.Parameter('bidder', openapi.IN_QUERY, description="Filter by bidder user ID.", type=openapi.TYPE_STRING),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

# Place Bid API (DRF generic view)
class PlaceBidView(generics.CreateAPIView):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'  # Use UUID for lookup

    @swagger_auto_schema(
        operation_description="Place a bid on an auction.",
        request_body=BidSerializer,
        responses={201: openapi.Response('Bid placed successfully', BidSerializer), 400: 'Validation error'},
        manual_parameters=[],
        tags=['auction']
    )
    def post(self, request, *args, **kwargs):
        auction_id = request.data.get("auction")
        bid_amount = request.data.get("bid_amount")
        user = request.user

        try:
            auction = Auction.objects.get(id=auction_id)
        except Auction.DoesNotExist:
            return Response({"error": "Auction not found."}, status=status.HTTP_404_NOT_FOUND)

        if auction.end_time < now():
            return Response({"error": "This auction has ended."}, status=status.HTTP_400_BAD_REQUEST)
        if float(bid_amount) <= float(auction.highest_bid):
            return Response({"error": "Your bid must be higher than the current highest bid."}, status=status.HTTP_400_BAD_REQUEST)
        if float(bid_amount) < float(auction.starting_price):
            return Response({"error": "Your bid must be higher than the starting price."}, status=status.HTTP_400_BAD_REQUEST)

        bid = Bid.objects.create(auction=auction, bidder=user, bid_amount=bid_amount)
        auction.highest_bid = bid_amount
        auction.highest_bidder = user
        auction.save(update_fields=['highest_bid', 'highest_bidder'])

        return Response({"success": "Bid placed successfully!"}, status=status.HTTP_201_CREATED)
