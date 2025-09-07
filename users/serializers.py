from rest_framework import serializers
from .models import PasswordResetToken, User

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'mobile', 'first_name', 'last_name', 'full_name']
        read_only_fields = ['id']

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
    
class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with the following fields:
    - form_type: Choice field ('customer' or 'dealer')
    - full_name: String field for user's full name
    - email: Email field (must be unique)
    - phone: String field for phone number (up to 15 digits)
    - password: String field (must meet complexity requirements):
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one digit
    - confirm_password: Must match password field
    """
    form_type = serializers.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        source='user_type',
        help_text="Select user type: 'customer' or 'dealer'"
    )
    full_name = serializers.CharField(
        write_only=True,
        help_text="User's full name (e.g., 'John Doe')"
    )
    email = serializers.EmailField(
        help_text="Valid email address (must be unique)"
    )
    phone = serializers.CharField(
        source='mobile',
        max_length=15,
        help_text="Phone number up to 15 digits"
    )
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Password must be at least 8 characters long, contain one uppercase letter and one digit"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Must match the password field"
    )
    
    class Meta:
        model = User
        fields = [
            'form_type', 'full_name', 'email', 'phone', 'password', 'confirm_password',
            'country', 'dob', 'state', 'address', 'zip_code', 'gender',
            'language', 'currency', 'id_file', 'profile_pic'
        ]
        extra_kwargs = {
            'dob': {'required': False},
            'state': {'required': False},
            'address': {'required': False},
            'zip_code': {'required': False},
            'gender': {'required': False},
            'language': {'required': False},
            'currency': {'required': False},
            'id_file': {'required': False},
            'profile_pic': {'required': False},
            'country': {'required': False},
        }

    def validate_password(self, value):
        """
        Validate password complexity requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one digit
        """
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one digit."
            )
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )
        return value

    def validate_email(self, value):
        """Validate email uniqueness."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def validate_phone(self, value):
        """Validate phone number uniqueness and length."""
        # Remove any non-digit characters for validation
        cleaned_number = ''.join(filter(str.isdigit, value))
        if len(cleaned_number) > 15:
            raise serializers.ValidationError("Phone number cannot exceed 15 digits")
        
        if User.objects.filter(mobile=value).exists():
            raise serializers.ValidationError("Phone number already registered")
        return value

    # Note: File validation is temporarily disabled
    # Will be re-enabled when document requirements are implemented

    def validate(self, data):
        """Validate form data."""
        # Validate password match
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})

        # Note: Type-specific field validation is temporarily disabled
        # Required fields for each type will be enforced later
        return data

    def create(self, validated_data):
        """Create new user instance."""
        # Remove confirmation fields
        validated_data.pop('confirm_password', None)
        
        # Process full name
        full_name = validated_data.pop('full_name', '')
        name_parts = full_name.split(maxsplit=1)
        validated_data['first_name'] = name_parts[0]
        validated_data['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
        
        # Set username as email
        validated_data['username'] = validated_data['email']
        
        # Create user instance with password
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        return user
    
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text='New password (must meet complexity requirements)'
    )
    confirmPassword = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text='Must match the password field'
    )

    def validate_password(self, value):
        """Validate password complexity."""
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one digit."
            )
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )
        return value

    def validate(self, data):
        """Validate that passwords match."""
        if data.get('password') != data.get('confirmPassword'):
            raise serializers.ValidationError({
                "confirmPassword": "Passwords do not match"
            })
        return data

