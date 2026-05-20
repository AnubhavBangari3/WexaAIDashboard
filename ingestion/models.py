import secrets
from django.db import models
from django.conf import settings


class APIKey(models.Model):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="api_keys",
    )
    name = models.CharField(max_length=100, default="Default API Key")
    key = models.CharField(max_length=128, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_api_keys",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    @staticmethod
    def generate_key():
        return f"wexa_{secrets.token_urlsafe(32)}"

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.organization.name}"


class Event(models.Model):
    SOURCE_API = "api"
    SOURCE_BATCH = "batch"
    SOURCE_CSV = "csv"
    SOURCE_WEBHOOK = "webhook"

    SOURCE_CHOICES = [
        (SOURCE_API, "API"),
        (SOURCE_BATCH, "Batch"),
        (SOURCE_CSV, "CSV"),
        (SOURCE_WEBHOOK, "Webhook"),
    ]

    STATUS_PENDING = "pending"
    STATUS_PROCESSED = "processed"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSED, "Processed"),
        (STATUS_FAILED, "Failed"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="events",
    )
    api_key = models.ForeignKey(
        APIKey,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    event_name = models.CharField(max_length=255, db_index=True)
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES, default=SOURCE_API)
    payload = models.JSONField(default=dict)
    normalized_payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    error_message = models.TextField(blank=True, null=True)
    occurred_at = models.DateTimeField(db_index=True)
    received_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-occurred_at"]
        indexes = [
            models.Index(fields=["organization", "event_name"]),
            models.Index(fields=["organization", "occurred_at"]),
            models.Index(fields=["source_type", "status"]),
        ]

    def __str__(self):
        return f"{self.event_name} - {self.organization.name}"


class CSVUpload(models.Model):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="csv_uploads",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    file = models.FileField(upload_to="csv_uploads/")
    total_rows = models.PositiveIntegerField(default=0)
    successful_rows = models.PositiveIntegerField(default=0)
    failed_rows = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"CSV Upload {self.id} - {self.organization.name}"