from rest_framework import serializers
from .models import Auction, Bid
from vehicles.models import Vehicle
from django.utils.timezone import now  

class AuctionSerializer(serializers.ModelSerializer):
    """
    Serializer for auction creation and management
    """
    vehicle = serializers.PrimaryKeyRelatedField(
        queryset=Vehicle.objects.all(),
        help_text="Select the vehicle for this auction",
        label="Vehicle"
    )
    starting_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Enter the starting bid price",
        label="Starting Price ($)",
        style={'placeholder': '15000.00'}
    )
    reserve_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text="Enter reserve price (minimum selling price) - optional",
        label="Reserve Price ($)",
        style={'placeholder': '20000.00'}
    )
    start_time = serializers.DateTimeField(
        help_text="Enter auction start date and time",
        label="Start Time",
        format="%Y-%m-%d %H:%M:%S"
    )
    end_time = serializers.DateTimeField(
        help_text="Enter auction end date and time",
        label="End Time", 
        format="%Y-%m-%d %H:%M:%S"
    )
    title = serializers.CharField(
        max_length=255,
        help_text="Enter a descriptive title for the auction",
        label="Auction Title",
        style={'placeholder': '2023 Toyota Camry - Low Mileage'}
    )
    description = serializers.CharField(
        required=False,
        help_text="Enter detailed auction description (optional)",
        label="Description",
        style={'base_template': 'textarea.html', 'placeholder': 'Detailed description of the auction...'}
    )
    
    class Meta:
        model = Auction
        fields = '__all__'

class BidSerializer(serializers.ModelSerializer):
    """
    Serializer for bid placement and management
    """
    auction = serializers.PrimaryKeyRelatedField(
        queryset=Auction.objects.all(),
        help_text="Select the auction to bid on",
        label="Auction"
    )
    bid_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Enter your bid amount (must be higher than current highest bid)",
        label="Bid Amount ($)",
        style={'placeholder': '25000.00'}
    )
    bidder = serializers.PrimaryKeyRelatedField(
        read_only=True,
        help_text="Bidder information (auto-filled from logged-in user)",
        label="Bidder"
    )
    
    class Meta:
        model = Bid
        fields = '__all__'


class PartialAuctionSerializer(AuctionSerializer):
    """All auction fields optional for PATCH operations."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not getattr(field, 'read_only', False):
                field.required = False


class PartialBidSerializer(BidSerializer):
    """All bid fields optional for PATCH operations (except read-only)."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not getattr(field, 'read_only', False):
                field.required = False
