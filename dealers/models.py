from django.db import models
import uuid
from django.conf import settings
from django.utils import timezone

class DealerProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dealer_profile')
    company_name = models.CharField(
        max_length=255,
        help_text="Example: Sunrise Auto Group, Elite Motors, City Cars"
    )
    address = models.CharField(
        max_length=255,
        help_text="Example: 123 Main St, Downtown, Suite 400"
    )
    city = models.CharField(
        max_length=100,
        help_text="Example: Hyderabad, Mumbai, New York"
    )
    state = models.CharField(
        max_length=100,
        help_text="Example: Telangana, California, Maharashtra"
    )
    country = models.CharField(
        max_length=100,
        help_text="Example: India, USA, Canada"
    )
    phone = models.CharField(
        max_length=20,
        help_text="Example: +91-9876543210, (555) 123-4567"
    )
    logo = models.ImageField(
        upload_to='dealer_logos/', null=True, blank=True,
        help_text="Upload company logo (PNG/JPG)"
    )
    email = models.EmailField(
        max_length=255, blank=True,
        help_text="Example: info@sunriseauto.com"
    )
    website = models.URLField(
        max_length=255, blank=True,
        help_text="Example: https://www.sunriseauto.com"
    )
    created_at = models.DateTimeField(default=timezone.now, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_approved = models.BooleanField(default=False)
    # Add more fields as needed

    def __str__(self):
        return self.company_name
