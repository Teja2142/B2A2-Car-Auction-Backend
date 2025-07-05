from rest_framework import serializers
from .models import Vehicle, VehicleImage

class VehicleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImage
        fields = ['id', 'image', 'vehicle']
        read_only_fields = ['id']

class VehicleSerializer(serializers.ModelSerializer):
    images = VehicleImageSerializer(many=True, read_only=True)
    dealer = serializers.PrimaryKeyRelatedField(read_only=True)

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
    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all())
    images = serializers.ListField(
        child=serializers.ImageField(),
        allow_empty=False,
        write_only=True,
        help_text="Upload one or more images."
    )

    def create(self, validated_data):
        vehicle = validated_data['vehicle']
        images = validated_data['images']
        image_objs = [VehicleImage.objects.create(vehicle=vehicle, image=img) for img in images]
        return image_objs
