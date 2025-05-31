import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    mobile = models.CharField(max_length=15, unique=True)
    reset_token = models.UUIDField(blank=True, null=True, unique=True)

    def __str__(self):
        return self.username

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        from django.utils.timezone import now
        return (now() - self.created_at).total_seconds() < 3600  # 1 hour expiry
