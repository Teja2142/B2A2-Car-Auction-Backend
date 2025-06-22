from rest_framework import serializers
from .models import Vehicle, VehicleImage, Auction, Bid
from users.serializers import UserSerializer  
from django.utils.timezone import now  

class VehicleImageSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    class Meta:
        model = VehicleImage
        fields = ['id', 'image']
        read_only_fields = ['id']  

class VehicleSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    images = VehicleImageSerializer(many=True, read_only=True)
    class Meta:
        model = Vehicle
        fields = ['id', 'make', 'model', 'year', 'condition', 'max_price', 'available', 'images']
        read_only_fields = ['id']  # Vehicle ID is read-only

class AuctionSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    # Accept vehicle UUID on write, show nested vehicle on read
    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all(), write_only=True)
    vehicle_details = VehicleSerializer(source='vehicle', read_only=True)
    highest_bidder = UserSerializer(read_only=True)  # Nested User (if you have a UserSerializer)
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Auction
        fields = ['id', 'vehicle', 'vehicle_details', 'starting_price', 'start_time', 'end_time', 'highest_bid', 'highest_bidder', 'status']
        read_only_fields = ['id', 'highest_bid', 'highest_bidder', 'status']  # Auction ID, bid info, and status are read-only

    def get_status(self, obj):
        if obj.end_time < now():
            return "completed"
        else:
            return "active"

class BidSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    class Meta:
        model = Bid
        fields = ['id', 'auction', 'bid_amount']
        read_only_fields = ['id']  # Bid ID is read-only

    def validate(self, data):
        # Ensure auction is present for validation
        auction = data.get('auction')
        bid_amount = data.get('bid_amount')
        if auction and bid_amount is not None:
            if float(bid_amount) <= float(auction.highest_bid):
                raise serializers.ValidationError({"bid_amount": "Bid must be higher than the current highest bid."})
            if float(bid_amount) < float(auction.starting_price):
                raise serializers.ValidationError({"bid_amount": "Bid must be at least the starting price."})
        return data

    def validate_bid_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Bid amount must be positive.")
        return value
