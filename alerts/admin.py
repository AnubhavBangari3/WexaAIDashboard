from django.contrib import admin
from .models import AlertRule, AlertHistory, Notification


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "organization",
        "event_name",
        "metric",
        "operator",
        "threshold",
        "status",
        "created_at",
    ]
    list_filter = ["status", "metric", "operator", "enable_in_app", "enable_email", "enable_webhook"]
    search_fields = ["name", "event_name", "organization__name"]


@admin.register(AlertHistory)
class AlertHistoryAdmin(admin.ModelAdmin):
    list_display = [
        "alert_rule",
        "organization",
        "action",
        "triggered_value",
        "threshold",
        "created_at",
    ]
    list_filter = ["action"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "organization",
        "channel",
        "status",
        "is_read",
        "created_at",
    ]
    list_filter = ["channel", "status", "is_read"]