import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

from django.core.validators import RegexValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from datetime import date

def validate_future_date(value):
    if value and value > date.today():
        raise ValidationError('Date of birth cannot be in the future.')

def validate_file_size(value):
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 5MB
        raise ValidationError("Maximum file size allowed is 5MB")

def validate_image_size(value):
    filesize = value.size
    if filesize > 2 * 1024 * 1024:  # 2MB
        raise ValidationError("Maximum image size allowed is 2MB")

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('dealer', 'Dealer'),
    )
    
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    )

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    mobile = models.CharField(
        validators=[phone_regex],
        max_length=15,
        unique=True,
        help_text="Phone number must be entered in the format: '+999999999'"
    )
    country = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="User's country of residence"
    )
    dob = models.DateField(
        null=True,
        blank=True,
        validators=[validate_future_date],
        help_text="Date of birth in YYYY-MM-DD format"
    )
    reset_token = models.UUIDField(blank=True, null=True, unique=True)
    
    # Customer specific fields
    state = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )
    
    # Dealer specific fields
    language = models.CharField(max_length=50, blank=True, null=True)
    currency = models.CharField(max_length=10, blank=True, null=True)
    id_file = models.FileField(
        upload_to='dealer_docs/',
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        blank=True,
        null=True,
        help_text="Accepted formats: PDF, JPG, PNG. Max size: 5MB"
    )
    profile_pic = models.ImageField(
        upload_to='profile_pics/',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_image_size
        ],
        blank=True,
        null=True,
        help_text="Accepted formats: JPG, PNG. Max size: 2MB"
    )

    def __str__(self):
        return self.username

class PasswordResetToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        from django.utils.timezone import now
        return (now() - self.created_at).total_seconds() < 3600  # 1 hour expiry
