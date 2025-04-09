from django.contrib import admin
from .models import Auction, Bid, Vehicle
from django.utils.html import format_html

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_vehicle_name', 'starting_price', 'start_time', 'end_time', 'highest_bid', 'highest_bidder')
    search_fields = ('vehicle__make', 'vehicle__model', 'highest_bidder__email')
    list_filter = ('start_time', 'end_time')

    def get_vehicle_name(self, obj):
        return f"{obj.vehicle.make} {obj.vehicle.model} ({obj.vehicle.year})"  # Properly format the vehicle name
    
    get_vehicle_name.short_description = "Vehicle"

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_auction_vehicle', 'bidder', 'bid_amount', 'timestamp')
    search_fields = ('auction__vehicle__make', 'auction__vehicle__model', 'bidder__email')
    list_filter = ('timestamp',)

    def get_auction_vehicle(self, obj):
        return f"{obj.auction.vehicle.make} {obj.auction.vehicle.model} ({obj.auction.vehicle.year})"

    get_auction_vehicle.short_description = "Vehicle"

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'make', 'model', 'year', 'condition', 'max_price', 'available', 'image_count', 'image_preview')
    search_fields = ('make', 'model', 'year')
    list_filter = ('available', 'year')

    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Image Count'

    def image_preview(self, obj):
        images = obj.images.all()[:1]  # Show only first image as preview
        if images:
            return format_html('<img src="{}" width="100" />', images[0].image.url)
        return "-"
    image_preview.short_description = 'Thumbnail'
