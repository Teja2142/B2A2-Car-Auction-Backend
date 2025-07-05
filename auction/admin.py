from django.contrib import admin
from .models import Auction, Bid
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
