from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'mobile', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create(**validated_data)



from .models import PasswordResetToken, User
from django.core.mail import send_mail

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
        reset_link = f"http://127.0.0.1:3000/reset-password/{token.token}"
        send_mail(
            "Password Reset Request",
            f"Click the link below to reset your password:\n{reset_link}",
            "no-reply@yourdomain.com",
            [user.email],
        )
        return token
    
    
    
    
    
    
