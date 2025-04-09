from django.db import models
from users.models import User
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

# from django.db import models
# from django.conf import settings
# from django.utils import timezone

# User = settings.AUTH_USER_MODEL

class Vehicle(models.Model):
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    condition = models.CharField(max_length=50)
    max_price = models.DecimalField(max_digits=12, decimal_places=2)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.year})"

class VehicleImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='vehicle_images/')

    def __str__(self):
        return f"Image for {self.vehicle}"

class Auction(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE)
    starting_price = models.DecimalField(max_digits=12, decimal_places=2)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    highest_bid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    highest_bidder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.vehicle} - Auction"

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.bid_amount <= self.auction.highest_bid:
            raise ValidationError("Bid must be higher than the current highest bid.")
        if self.bid_amount < self.auction.starting_price:
            raise ValidationError("Bid must be at least the starting price.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        if self.bid_amount > self.auction.highest_bid:
            self.auction.highest_bid = self.bid_amount
            self.auction.highest_bidder = self.bidder
            self.auction.save(update_fields=['highest_bid', 'highest_bidder'])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.bidder} - {self.bid_amount} on {self.auction}"

