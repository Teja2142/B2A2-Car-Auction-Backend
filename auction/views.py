from rest_framework import viewsets, permissions, status, generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes, parser_classes

from .models import Vehicle, Auction, Bid, VehicleImage
from .serializers import VehicleSerializer, AuctionSerializer, BidSerializer, VehicleImageSerializer
from django.utils.timezone import now

# Home page (public)
@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    from django.shortcuts import render
    return render(request, 'index.html')

# Vehicle ViewSet
class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  # Only authenticated users can create/update/delete
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        # Allow anyone to list/retrieve, restrict create/update/delete
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        required_fields = ['make', 'model', 'year', 'condition', 'max_price']
        for field in required_fields:
            if not request.data.get(field):
                return Response(
                    {"error": f"'{field}' is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        make = request.data.get('make')
        model = request.data.get('model')
        condition = request.data.get('condition')

        try:
            year = int(request.data.get('year'))
        except (TypeError, ValueError):
            return Response({"error": "Year must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            max_price = float(request.data.get('max_price'))
        except (TypeError, ValueError):
            return Response({"error": "Max price must be a number."}, status=status.HTTP_400_BAD_REQUEST)

        if not request.FILES.getlist('images'):
            return Response({"error": "At least one image is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Duplicate check (case-insensitive)
        if Vehicle.objects.filter(
            make__iexact=make,
            model__iexact=model,
            year=year,
            condition__iexact=condition,
            max_price=max_price
        ).exists():
            return Response(
                {"error": "A vehicle with the same details already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vehicle = serializer.save()
        for image in request.FILES.getlist('images'):
            VehicleImage.objects.create(vehicle=vehicle, image=image)
        return Response(self.get_serializer(vehicle).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        vehicle = serializer.save()
        if 'images' in request.FILES:
            for image in request.FILES.getlist('images'):
                VehicleImage.objects.create(vehicle=vehicle, image=image)
        return Response(self.get_serializer(vehicle).data)

# Auction ViewSet
class AuctionViewSet(viewsets.ModelViewSet):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

# Bid ViewSet
class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

# Place Bid API (DRF generic view)
class PlaceBidView(generics.CreateAPIView):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        auction_id = request.data.get("auction")
        bid_amount = request.data.get("bid_amount")
        user = request.user

        try:
            auction = Auction.objects.get(id=auction_id)
            if auction.end_time < now():
                return Response({"error": "This auction has ended."}, status=status.HTTP_400_BAD_REQUEST)
            if float(bid_amount) <= float(auction.highest_bid):
                return Response({"error": "Your bid must be higher than the current highest bid."}, status=status.HTTP_400_BAD_REQUEST)
            if float(bid_amount) < float(auction.starting_price):
                return Response({"error": "Your bid must be higher than the starting price."}, status=status.HTTP_400_BAD_REQUEST)
            if float(bid_amount) > float(auction.vehicle.max_price):
                return Response({"error": "Your bid exceeds the vehicle's maximum price."}, status=status.HTTP_400_BAD_REQUEST)

            bid = Bid.objects.create(auction=auction, bidder=user, bid_amount=bid_amount)
            auction.highest_bid = bid_amount
            auction.highest_bidder = user
            auction.save(update_fields=['highest_bid', 'highest_bidder'])

            return Response({"success": "Bid placed successfully!"}, status=status.HTTP_201_CREATED)
        except Auction.DoesNotExist:
            return Response({"error": "Auction not found."}, status=status.HTTP_404_NOT_FOUND)
