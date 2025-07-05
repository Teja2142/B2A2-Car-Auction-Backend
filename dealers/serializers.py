from rest_framework import serializers
from .models import DealerProfile

class DealerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DealerProfile
        fields = [
            'id', 'company_name', 'address', 'city', 'state', 'country', 'phone', 'logo',
            'email', 'website', 'created_at', 'updated_at', 'is_approved'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_approved']
