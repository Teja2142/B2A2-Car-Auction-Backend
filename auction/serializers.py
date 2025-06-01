from rest_framework import serializers
from .models import Vehicle, VehicleImage, Auction, Bid
from users.serializers import UserSerializer  # Import UserSerializer
from django.utils.timezone import now  # Import now for time comparison

class VehicleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImage
        fields = ['id', 'image']
        read_only_fields = ['id']  # Image ID is read-only

class VehicleSerializer(serializers.ModelSerializer):
    images = VehicleImageSerializer(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = ['id', 'make', 'model', 'year', 'condition', 'max_price', 'available', 'images']
        read_only_fields = ['id']  # Vehicle ID is read-only

class AuctionSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only=True)  # Nested Vehicle
    highest_bidder = UserSerializer(read_only=True)  # Nested User (if you have a UserSerializer)
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Auction
        fields = ['id', 'vehicle', 'starting_price', 'start_time', 'end_time', 'highest_bid', 'highest_bidder', 'status']
        read_only_fields = ['id', 'highest_bid', 'highest_bidder', 'status']  # Auction ID, bid info, and status are read-only

    def get_status(self, obj):
        if obj.end_time < now():
            return "completed"
        else:
            return "active"

class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ['id', 'auction', 'bid_amount']
        read_only_fields = ['id']  # Bid ID is read-only

    def validate_bid_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Bid amount must be positive.")
        return value
