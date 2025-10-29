from rest_framework import serializers
from .models import Vehicle, VehicleImage

class VehicleImageSerializer(serializers.ModelSerializer):
    """
    Serializer for vehicle image uploads
    """
    image = serializers.ImageField(
        help_text="Upload vehicle image (JPEG, PNG formats supported)",
        label="Vehicle Image"
    )
    vehicle = serializers.PrimaryKeyRelatedField(
        queryset=Vehicle.objects.all(),
        help_text="Select the vehicle for this image",
        label="Vehicle"
    )
    
    class Meta:
        model = VehicleImage
        fields = ['id', 'image', 'vehicle']
        read_only_fields = ['id']

class VehicleSerializer(serializers.ModelSerializer):
    """
    Serializer for vehicle data with form-friendly field definitions
    """
    images = VehicleImageSerializer(many=True, read_only=True)
    dealer = serializers.PrimaryKeyRelatedField(read_only=True, help_text="Dealer user ID (present only if created by a dealer user)")
    
    vin = serializers.CharField(
        max_length=17,
        help_text="Enter 17-character Vehicle Identification Number",
        label="VIN Number",
        style={'placeholder': '1HGBH41JXMN109186'}
    )
    make = serializers.CharField(
        max_length=50,
        help_text="Enter vehicle make/manufacturer",
        label="Make",
        style={'placeholder': 'Toyota'}
    )
    model = serializers.CharField(
        max_length=50,
        help_text="Enter vehicle model",
        label="Model", 
        style={'placeholder': 'Camry'}
    )
    year = serializers.IntegerField(
        help_text="Enter vehicle year (1886-2100)",
        label="Year",
        min_value=1886,
        max_value=2100,
        style={'placeholder': '2023'}
    )
    color = serializers.CharField(
        max_length=30,
        help_text="Enter vehicle color",
        label="Color",
        style={'placeholder': 'Silver'}
    )
    mileage = serializers.IntegerField(
        min_value=0,
        help_text="Enter vehicle mileage in miles",
        label="Mileage",
        style={'placeholder': '25000'}
    )
    transmission = serializers.CharField(
        max_length=20,
        help_text="Enter transmission type",
        label="Transmission",
        style={'placeholder': 'Automatic'}
    )
    fuel_type = serializers.CharField(
        max_length=20,
        help_text="Enter fuel type",
        label="Fuel Type",
        style={'placeholder': 'Gasoline'}
    )
    body_style = serializers.CharField(
        max_length=30,
        help_text="Enter body style",
        label="Body Style",
        style={'placeholder': 'Sedan'}
    )
    registration_number = serializers.CharField(
        max_length=20,
        help_text="Enter registration/license plate number",
        label="Registration Number",
        style={'placeholder': 'ABC-123'}
    )
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Enter vehicle price",
        label="Price ($)",
        style={'placeholder': '25000.00'}
    )
    starting_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Enter auction starting price",
        label="Starting Price ($)",
        style={'placeholder': '20000.00'}
    )
    features = serializers.CharField(
        required=False,
        help_text="List vehicle features (optional)",
        label="Features",
        style={'placeholder': 'Leather seats, Sunroof, Navigation'}
    )
    description = serializers.CharField(
        required=False,
        help_text="Enter detailed vehicle description (optional)",
        label="Description",
        style={'base_template': 'textarea.html', 'placeholder': 'Detailed description of the vehicle...'}
    )

    class Meta:
        model = Vehicle
        fields = [
            'id', 'vin', 'make', 'model', 'year', 'color', 'mileage', 'features', 'description',
            'transmission', 'fuel_type', 'body_style', 'registration_number', 'images',
            'price', 'status', 'dealer', 'created_at', 'updated_at', 'starting_price'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'dealer']

    def validate_vin(self, value):
        import re
        vin_pattern = r'^[A-HJ-NPR-Z0-9]{17}$'
        if not re.match(vin_pattern, value):
            raise serializers.ValidationError('VIN must be 17 characters, alphanumeric, and not contain I, O, or Q.')
        return value

    def validate_year(self, value):
        if value < 1886 or value > 2100:
            raise serializers.ValidationError('Year must be between 1886 and 2100.')
        return value

    def validate_mileage(self, value):
        if value < 0:
            raise serializers.ValidationError('Mileage must be positive.')
        return value

    def validate_registration_number(self, value):
        if value and Vehicle.objects.filter(registration_number__iexact=value).exists():
            raise serializers.ValidationError('Registration number must be unique.')
        return value

class MultipleVehicleImageUploadSerializer(serializers.Serializer):
    """
    Serializer for uploading multiple vehicle images at once
    """
    vehicle = serializers.PrimaryKeyRelatedField(
        queryset=Vehicle.objects.all(),
        help_text="Select the vehicle for these images",
        label="Vehicle"
    )
    images = serializers.ListField(
        child=serializers.ImageField(),
        allow_empty=False,
        write_only=True,
        help_text="Upload one or more vehicle images (JPEG, PNG formats supported)",
        label="Vehicle Images"
    )

    def create(self, validated_data):
        vehicle = validated_data['vehicle']
        images = validated_data['images']
        image_objs = [VehicleImage.objects.create(vehicle=vehicle, image=img) for img in images]
        return image_objs


class PartialVehicleSerializer(VehicleSerializer):
    """All vehicle fields optional for PATCH operations."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not getattr(field, 'read_only', False):
                field.required = False


class PartialVehicleImageSerializer(VehicleImageSerializer):
    """All vehicle image fields optional for PATCH operations."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not getattr(field, 'read_only', False):
                field.required = False


class PartialMultipleVehicleImageUploadSerializer(MultipleVehicleImageUploadSerializer):
    """Make bulk upload fields optional for PATCH-like flexibility (not typical but for consistency)."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False
