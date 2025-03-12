from django.db import models
from users.models import User

class Vehicle(models.Model):
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    condition = models.CharField(max_length=100)
    body_style = models.CharField(max_length=100)
    max_price = models.FloatField()
    mileage = models.IntegerField()
    available = models.BooleanField(default=True)

class Auction(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    starting_price = models.FloatField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    highest_bid = models.FloatField(default=0.0)
    highest_bidder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
