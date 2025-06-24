from django.db import models
from django.contrib.auth.models import User
import uuid

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)

    def __str__(self):
        return f"Profile of {self.user.username or self.uuid}"
