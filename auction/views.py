from rest_framework import viewsets, permissions
from rest_framework.authentication import TokenAuthentication
from .models import Vehicle, Auction, Bid
from .serializers import VehicleSerializer, AuctionSerializer, BidSerializer

from django.utils.timezone import now
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
import json

from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes

from .models import *
from .serializers import *
from django.shortcuts import render

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status



@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    return render(request, 'index.html')

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    authentication_classes = [TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]  # 🧠 This is crucial for image upload!

    def create(self, request, *args, **kwargs):
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
            # Optionally delete old images first if you want:
            # VehicleImage.objects.filter(vehicle=vehicle).delete()

            for image in request.FILES.getlist('images'):
                VehicleImage.objects.create(vehicle=vehicle, image=image)

        return Response(self.get_serializer(vehicle).data)

class AuctionViewSet(viewsets.ModelViewSet):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
class PlaceBidView(generics.CreateAPIView):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        auction_id = request.data.get("auction")
        bid_amount = request.data.get("bid_amount")
        user = request.user

        try:
            auction = Auction.objects.get(id=auction_id)
            
            # Check if the auction is still running
            if auction.end_time < now():
                return Response({"error": "This auction has ended."}, status=status.HTTP_400_BAD_REQUEST)

            # Check bid amount
            if bid_amount <= auction.highest_bid:
                return Response({"error": "Your bid must be higher than the current highest bid."}, status=status.HTTP_400_BAD_REQUEST)

            if bid_amount < auction.starting_price:
                return Response({"error": "Your bid must be higher than the starting price."}, status=status.HTTP_400_BAD_REQUEST)

            if bid_amount > auction.vehicle.max_price:
                return Response({"error": "Your bid exceeds the vehicle's maximum price."}, status=status.HTTP_400_BAD_REQUEST)

            # Save the bid and update auction
            bid = Bid.objects.create(auction=auction, bidder=user, bid_amount=bid_amount)
            auction.highest_bid = bid_amount
            auction.highest_bidder = user
            auction.save(update_fields=['highest_bid', 'highest_bidder'])

            return Response({"success": "Bid placed successfully!"}, status=status.HTTP_201_CREATED)

        except Auction.DoesNotExist:
            return Response({"error": "Auction not found."}, status=status.HTTP_404_NOT_FOUND)





@login_required  # Ensure only logged-in users can bid
@csrf_exempt  # If testing with Postman or external tools, disable CSRF (remove in production)
def place_bid(request, auction_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse JSON data
            bid_amount = float(data.get('bid_amount'))  # Get bid amount from request body

            auction = get_object_or_404(Auction, id=auction_id)

            # Create bid instance (but don't save yet)
            bid = Bid(auction=auction, bidder=request.user, bid_amount=bid_amount)

            # Validate bid using `clean()`
            bid.full_clean()

            # Save the bid if valid
            bid.save()

            return JsonResponse({'success': True, 'message': 'Bid placed successfully!', 'bid_amount': bid.bid_amount})

        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid bid amount.'}, status=400)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)



# @permission_classes([AllowAny])
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser]) 
@permission_classes([AllowAny])  # Or change to IsAuthenticated if needed
def create_vehicle(request):
    print("📥 Incoming files:", request.FILES)
    serializer = VehicleSerializer(data=request.data)
    if serializer.is_valid():
        vehicle = serializer.save()
        for image in request.FILES.getlist('images'):
            img_instance = VehicleImage.objects.create(vehicle=vehicle, image=image)
            print("✅ Saved:", img_instance.image.path)
        return Response(VehicleSerializer(vehicle).data, status=status.HTTP_201_CREATED)
    print("❌ Errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
