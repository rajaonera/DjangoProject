from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# -------------------------------
# Utilisateurs
# -------------------------------
class User(AbstractUser):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.username} - {self.email}"

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='smartsaha_users',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='smartsaha_users',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
