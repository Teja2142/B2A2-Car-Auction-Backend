from rest_framework import serializers
from .models import PasswordResetToken, User

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile display and updates
    """
    full_name = serializers.SerializerMethodField(
        help_text="User's full name (auto-generated from first and last name)",
        read_only=True
    )
    username = serializers.CharField(
        help_text="Username (typically same as email)",
        label="Username",
        read_only=True
    )
    email = serializers.EmailField(
        help_text="User's email address",
        label="Email Address",
        style={'placeholder': 'user@example.com'}
    )
    mobile = serializers.CharField(
        help_text="User's mobile/phone number",
        label="Mobile Number",
        style={'placeholder': '+1234567890'},
        max_length=15
    )
    first_name = serializers.CharField(
        help_text="User's first name",
        label="First Name",
        style={'placeholder': 'John'},
        max_length=30
    )
    last_name = serializers.CharField(
        help_text="User's last name",
        label="Last Name", 
        style={'placeholder': 'Doe'},
        max_length=30
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'mobile', 'first_name', 'last_name', 'full_name']
        read_only_fields = ['id', 'username']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting password reset
    """
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
        help_text="Select user type: 'customer' or 'dealer'",
        label="User Type",
        style={'base_template': 'select.html'}
    )
    full_name = serializers.CharField(
        write_only=True,
        help_text="User's full name (e.g., 'John Doe')",
        label="Full Name",
        style={'placeholder': 'John Doe'},
        max_length=100
    )
    email = serializers.EmailField(
        help_text="Valid email address (must be unique)",
        label="Email Address",
        style={'placeholder': 'user@example.com'}
    )
    phone = serializers.CharField(
        source='mobile',
        max_length=15,
        help_text="Phone number up to 15 digits",
        label="Phone Number",
        style={'placeholder': '+1234567890'}
    )
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Password must be at least 8 characters long, contain one uppercase letter and one digit",
        label="Password",
        min_length=8,
        max_length=128
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Must match the password field",
        label="Confirm Password",
        min_length=8,
        max_length=128
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

class AdminUserCreateSerializer(RegisterSerializer):
    """Serializer for admin-created users allowing assignment of staff/superuser flags.

    Only staff users can set is_staff. Only superusers can set is_superuser.
    Inherits all registration fields plus two optional booleans.
    """
    is_staff = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Grant Django admin (staff) access to the new user",
        label="Is Staff"
    )
    is_superuser = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Grant superuser privileges (all permissions) - only superusers can set this",
        label="Is Superuser"
    )

    class Meta(RegisterSerializer.Meta):
        fields = RegisterSerializer.Meta.fields + ['is_staff', 'is_superuser']

    def validate(self, data):
        data = super().validate(data)
        request = self.context.get('request')
        # Enforce privilege escalation rules
        if data.get('is_superuser'):
            if not request or not request.user.is_superuser:
                raise serializers.ValidationError({
                    'is_superuser': 'Only an existing superuser can create another superuser.'
                })
        if data.get('is_staff') and (not request or not request.user.is_staff):
            raise serializers.ValidationError({
                'is_staff': 'Only staff can assign staff status.'
            })
        return data

    def create(self, validated_data):
        # Extract admin flags before base create
        is_staff = validated_data.pop('is_staff', False)
        is_superuser = validated_data.pop('is_superuser', False)
        user = super().create(validated_data)
        # Apply flags (if any)
        update_fields = []
        if is_staff:
            user.is_staff = True
            update_fields.append('is_staff')
        if is_superuser:
            user.is_superuser = True
            update_fields.append('is_superuser')
        if update_fields:
            user.save(update_fields=update_fields)
        return user
    
    
class LoginSerializer(serializers.Serializer):
    """
    Serializer for user authentication
    """
    email = serializers.EmailField(
        help_text="Enter your registered email address"
    )
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Enter your password"
    )

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


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for user profile updates with form-friendly fields
    """
    first_name = serializers.CharField(
        max_length=30,
        help_text="Enter your first name",
        label="First Name",
        style={'placeholder': 'John'}
    )
    last_name = serializers.CharField(
        max_length=30,
        help_text="Enter your last name", 
        label="Last Name",
        style={'placeholder': 'Doe'}
    )
    email = serializers.EmailField(
        help_text="Enter your email address",
        label="Email Address",
        style={'placeholder': 'user@example.com'}
    )
    mobile = serializers.CharField(
        max_length=15,
        help_text="Enter your mobile/phone number",
        label="Mobile Number",
        style={'placeholder': '+1234567890'}
    )
    country = serializers.CharField(
        max_length=50,
        required=False,
        help_text="Enter your country (optional)",
        label="Country",
        style={'placeholder': 'United States'}
    )
    state = serializers.CharField(
        max_length=50,
        required=False,
        help_text="Enter your state/province (optional)",
        label="State/Province",
        style={'placeholder': 'California'}
    )
    address = serializers.CharField(
        max_length=200,
        required=False,
        help_text="Enter your address (optional)",
        label="Address",
        style={'placeholder': '123 Main Street, City'}
    )
    zip_code = serializers.CharField(
        max_length=10,
        required=False,
        help_text="Enter your zip/postal code (optional)",
        label="Zip Code",
        style={'placeholder': '12345'}
    )
    dob = serializers.DateField(
        required=False,
        help_text="Enter your date of birth (optional)",
        label="Date of Birth",
        format="%Y-%m-%d"
    )
    gender = serializers.ChoiceField(
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        required=False,
        help_text="Select your gender (optional)",
        label="Gender"
    )
    language = serializers.CharField(
        max_length=50,
        required=False,
        help_text="Enter your preferred language (optional)",
        label="Language",
        style={'placeholder': 'English'}
    )
    currency = serializers.CharField(
        max_length=10,
        required=False,
        help_text="Enter your preferred currency (optional)",
        label="Currency",
        style={'placeholder': 'USD'}
    )
    profile_pic = serializers.ImageField(
        required=False,
        help_text="Upload your profile picture (optional, max 2MB)",
        label="Profile Picture"
    )
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'mobile', 'country', 'state',
            'address', 'zip_code', 'dob', 'gender', 'language', 'currency',
            'profile_pic'
        ]

    def validate_email(self, value):
        if value:
            normalized = value.strip().lower()
            qs = User.objects.filter(email=normalized)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError('Email already in use.')
            return normalized
        return value

    def validate_mobile(self, value):
        if value:
            qs = User.objects.filter(mobile=value)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError('Mobile number already in use.')
        return value

class PartialUserProfileUpdateSerializer(UserProfileUpdateSerializer):
    """Serializer for PATCH operations where all fields should be optional.

    Inherits field definitions (labels/help_text) but sets required=False on each.
    """
    first_name = serializers.CharField(required=False, max_length=30)
    last_name = serializers.CharField(required=False, max_length=30)
    email = serializers.EmailField(required=False)
    mobile = serializers.CharField(required=False, max_length=15)
    country = serializers.CharField(required=False, max_length=50)
    state = serializers.CharField(required=False, max_length=50)
    address = serializers.CharField(required=False, max_length=200)
    zip_code = serializers.CharField(required=False, max_length=10)
    dob = serializers.DateField(required=False, format="%Y-%m-%d")
    gender = serializers.ChoiceField(required=False, choices=[('male','Male'),('female','Female'),('other','Other')])
    language = serializers.CharField(required=False, max_length=50)
    currency = serializers.CharField(required=False, max_length=10)
    profile_pic = serializers.ImageField(required=False)

    class Meta(UserProfileUpdateSerializer.Meta):
        fields = UserProfileUpdateSerializer.Meta.fields

