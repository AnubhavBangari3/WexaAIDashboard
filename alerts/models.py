from django.conf import settings
from django.db import models
from django.utils import timezone


class AlertRule(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_TRIGGERED = "triggered"
    STATUS_RESOLVED = "resolved"
    STATUS_MUTED = "muted"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_TRIGGERED, "Triggered"),
        (STATUS_RESOLVED, "Resolved"),
        (STATUS_MUTED, "Muted"),
    ]

    OP_GT = "gt"
    OP_GTE = "gte"
    OP_LT = "lt"
    OP_LTE = "lte"
    OP_EQ = "eq"

    OPERATOR_CHOICES = [
        (OP_GT, ">"),
        (OP_GTE, ">="),
        (OP_LT, "<"),
        (OP_LTE, "<="),
        (OP_EQ, "="),
    ]

    CHANNEL_IN_APP = "in_app"
    CHANNEL_EMAIL = "email"
    CHANNEL_WEBHOOK = "webhook"

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="alert_rules",
    )
    name = models.CharField(max_length=255)
    event_name = models.CharField(max_length=255, blank=True)
    metric = models.CharField(max_length=50, default="count")
    operator = models.CharField(max_length=10, choices=OPERATOR_CHOICES, default=OP_GT)
    threshold = models.DecimalField(max_digits=12, decimal_places=2)
    time_window_minutes = models.PositiveIntegerField(default=10)

    enable_in_app = models.BooleanField(default=True)
    enable_email = models.BooleanField(default=False)
    email_to = models.EmailField(blank=True)

    enable_webhook = models.BooleanField(default=False)
    webhook_url = models.URLField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    muted_until = models.DateTimeField(null=True, blank=True)

    last_triggered_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    last_evaluated_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_alert_rules",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "event_name"]),
        ]

    def is_muted_now(self):
        return self.muted_until and self.muted_until > timezone.now()

    def __str__(self):
        return f"{self.name} - {self.organization.name}"


class AlertHistory(models.Model):
    ACTION_TRIGGERED = "triggered"
    ACTION_RESOLVED = "resolved"
    ACTION_MUTED = "muted"
    ACTION_EVALUATED = "evaluated"

    ACTION_CHOICES = [
        (ACTION_TRIGGERED, "Triggered"),
        (ACTION_RESOLVED, "Resolved"),
        (ACTION_MUTED, "Muted"),
        (ACTION_EVALUATED, "Evaluated"),
    ]

    alert_rule = models.ForeignKey(
        AlertRule,
        on_delete=models.CASCADE,
        related_name="history",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="alert_history",
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    triggered_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    threshold = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Notification(models.Model):
    CHANNEL_IN_APP = "in_app"
    CHANNEL_EMAIL = "email"
    CHANNEL_WEBHOOK = "webhook"

    CHANNEL_CHOICES = [
        (CHANNEL_IN_APP, "In App"),
        (CHANNEL_EMAIL, "Email"),
        (CHANNEL_WEBHOOK, "Webhook"),
    ]

    STATUS_PENDING = "pending"
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SENT, "Sent"),
        (STATUS_FAILED, "Failed"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    alert_rule = models.ForeignKey(
        AlertRule,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    error_message = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]