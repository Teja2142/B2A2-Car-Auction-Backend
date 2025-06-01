from rest_framework import serializers
from .models import PasswordResetToken, User

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'mobile', 'first_name', 'last_name', 'full_name']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def create(self, validated_data):
        user = User.objects.get(email=validated_data['email'])
        token = PasswordResetToken.objects.create(user=user)

        # Send password reset email
        # reset_link = f"http://127.0.0.1:3000/reset-password/{token.token}"
        # send_mail(
        #     "Password Reset Request",
        #     f"Click the link below to reset your password:\n{reset_link}",
        #     "no-reply@yourdomain.com",
        #     [user.email],
        # )
        return token
    
    
    
    
    
    
