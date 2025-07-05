from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import re
import uuid
from dealers.models import DealerProfile

class Vehicle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vin = models.CharField(
        max_length=17, unique=True,
        help_text="Example: 1HGCM82633A004352 (17-character Vehicle Identification Number)"
    )
    make = models.CharField(
        max_length=100,
        help_text="Example: Toyota, Ford, BMW, Tesla"
    )
    model = models.CharField(
        max_length=100,
        help_text="Example: Camry, F-150, 3 Series, Model S"
    )
    year = models.PositiveIntegerField(
        help_text="Example: 2022"
    )
    color = models.CharField(
        max_length=50,
        help_text="Example: Red, Blue, Black, White"
    )
    mileage = models.PositiveIntegerField(
        help_text="Example: 25000 (in kilometers or miles)"
    )
    features = models.TextField(
        blank=True,
        help_text="Example: Sunroof, Leather seats, Bluetooth, Backup camera"
    )
    description = models.TextField(
        blank=True,
        help_text="Example: Well-maintained, single owner, accident-free."
    )
    price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="Example: 18500.00"
    )
    starting_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="Example: 15000.00 (minimum bid price)"
    )

    TRANSMISSION_CHOICES = [
        ("automatic", "Automatic"),
        ("manual", "Manual"),
        ("cvt", "CVT"),
        ("semi-automatic", "Semi-Automatic"),
    ]
    FUEL_TYPE_CHOICES = [
        ("petrol", "Petrol"),
        ("diesel", "Diesel"),
        ("electric", "Electric"),
        ("hybrid", "Hybrid"),
        ("cng", "CNG"),
        ("lpg", "LPG"),
        ("other", "Other"),
    ]
    BODY_STYLE_CHOICES = [
        ("sedan", "Sedan"),
        ("suv", "SUV"),
        ("hatchback", "Hatchback"),
        ("coupe", "Coupe"),
        ("convertible", "Convertible"),
        ("wagon", "Wagon"),
        ("van", "Van"),
        ("pickup", "Pickup"),
        ("other", "Other"),
    ]
    STATUS_CHOICES = [
        ("active", "Active"),
        ("sold", "Sold"),
        ("pending", "Pending"),
    ]

    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, blank=True)
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES, blank=True)
    body_style = models.CharField(max_length=20, choices=BODY_STYLE_CHOICES, blank=True)
    registration_number = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    dealer = models.ForeignKey(DealerProfile, related_name="vehicles", on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.year})"

    def clean(self):
        # VIN validation: 17 chars, alphanumeric, no I/O/Q
        if self.vin:
            vin_pattern = r'^[A-HJ-NPR-Z0-9]{17}$'
            if not re.match(vin_pattern, self.vin):
                raise ValidationError({'vin': 'VIN must be 17 characters, alphanumeric, and not contain I, O, or Q.'})
        # Year reasonable range
        if self.year and (self.year < 1886 or self.year > 2100):
            raise ValidationError({'year': 'Year must be between 1886 and 2100.'})
        # Mileage positive
        if self.mileage is not None and self.mileage < 0:
            raise ValidationError({'mileage': 'Mileage must be positive.'})
        # Registration number unique (enforced by DB, but double check)
        if self.registration_number:
            if Vehicle.objects.exclude(pk=self.pk).filter(registration_number__iexact=self.registration_number).exists():
                raise ValidationError({'registration_number': 'Registration number must be unique.'})

class VehicleImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='vehicle_images/')

    def __str__(self):
        return f"Image for {self.vehicle}"
