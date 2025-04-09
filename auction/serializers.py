from rest_framework import serializers
from .models import Vehicle, VehicleImage, Auction, Bid

class VehicleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImage
        fields = ['id', 'image'] 

class VehicleSerializer(serializers.ModelSerializer):
    images = VehicleImageSerializer(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = ['id', 'make', 'model', 'year', 'condition', 'max_price', 'available', 'images']


class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = '__all__'

class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ['auction', 'bid_amount']
