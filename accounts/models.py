from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_OWNER = "owner"
    ROLE_ADMIN = "admin"
    ROLE_ANALYST = "analyst"
    ROLE_VIEWER = "viewer"

    ROLE_CHOICES = [
        (ROLE_OWNER, "Owner"),
        (ROLE_ADMIN, "Admin"),
        (ROLE_ANALYST, "Analyst"),
        (ROLE_VIEWER, "Viewer"),
    ]

    email = models.EmailField(unique=True)

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_VIEWER,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def is_owner_or_admin(self):
        return self.role in [self.ROLE_OWNER, self.ROLE_ADMIN]

    def __str__(self):
        return self.email