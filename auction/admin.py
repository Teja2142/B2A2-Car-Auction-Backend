from django.contrib import admin
from .models import Auction, Bid,Vehicle

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'starting_price', 'start_time', 'end_time', 'highest_bid', 'highest_bidder')
    search_fields = ('vehicle__make', 'vehicle__model', 'highest_bidder__email')
    list_filter = ('start_time', 'end_time')

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('id', 'auction', 'bidder', 'bid_amount', 'timestamp')
    search_fields = ('auction__vehicle__make', 'auction__vehicle__model', 'bidder__email')
    list_filter = ('timestamp',)




@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'make', 'model', 'year', 'condition', 'available')
    search_fields = ('make', 'model', 'year')
    list_filter = ('available', 'year')
