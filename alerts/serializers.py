from rest_framework import serializers
from .models import AlertRule, AlertHistory, Notification


class AlertRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertRule
        fields = [
            "id",
            "name",
            "event_name",
            "metric",
            "operator",
            "threshold",
            "time_window_minutes",
            "enable_in_app",
            "enable_email",
            "email_to",
            "enable_webhook",
            "webhook_url",
            "status",
            "muted_until",
            "last_triggered_value",
            "last_evaluated_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "last_triggered_value",
            "last_evaluated_at",
            "created_at",
            "updated_at",
        ]


class AlertHistorySerializer(serializers.ModelSerializer):
    alert_name = serializers.CharField(source="alert_rule.name", read_only=True)

    class Meta:
        model = AlertHistory
        fields = [
            "id",
            "alert_rule",
            "alert_name",
            "action",
            "triggered_value",
            "threshold",
            "message",
            "created_at",
        ]


class NotificationSerializer(serializers.ModelSerializer):
    alert_name = serializers.CharField(source="alert_rule.name", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "alert_rule",
            "alert_name",
            "channel",
            "title",
            "message",
            "status",
            "error_message",
            "is_read",
            "created_at",
            "sent_at",
        ]