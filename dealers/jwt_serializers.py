from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import DealerProfile

User = get_user_model()

class DealerEmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        fields = ['email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username from input fields so only email and password are required
        self.fields.pop('username', None)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email is None or password is None:
            raise serializers.ValidationError({'detail': 'Email and password are required.'})
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'detail': 'Invalid email or password.'})
        if not user.check_password(password):
            raise serializers.ValidationError({'detail': 'Invalid email or password.'})
        if not user.is_active:
            raise serializers.ValidationError({'detail': 'User account is disabled.'})
        if not hasattr(user, 'dealer_profile'):
            raise serializers.ValidationError({'detail': 'No dealer profile found for this user.'})
        # Only pass username and password to parent
        parent_attrs = {'username': user.username, 'password': password}
        data = super().validate(parent_attrs)
        data['user'] = {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'dealer_profile_id': str(user.dealer_profile.id),
        }
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token
