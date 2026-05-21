import requests
from decimal import Decimal

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from ingestion.models import Event
from .models import AlertRule, AlertHistory, Notification


def compare_values(value, operator, threshold):
    value = Decimal(str(value))
    threshold = Decimal(str(threshold))

    if operator == "gt":
        return value > threshold
    if operator == "gte":
        return value >= threshold
    if operator == "lt":
        return value < threshold
    if operator == "lte":
        return value <= threshold
    if operator == "eq":
        return value == threshold

    return False


def get_alert_metric_value(alert_rule):
    start_time = timezone.now() - timezone.timedelta(
        minutes=alert_rule.time_window_minutes
    )

    qs = Event.objects.filter(
        organization=alert_rule.organization,
        occurred_at__gte=start_time,
    )

    if alert_rule.event_name:
        qs = qs.filter(event_name=alert_rule.event_name)

    return qs.count()


def create_notification(alert_rule, channel, title, message):
    return Notification.objects.create(
        organization=alert_rule.organization,
        alert_rule=alert_rule,
        channel=channel,
        title=title,
        message=message,
        status=Notification.STATUS_PENDING,
    )


def send_email_notification(notification, email_to):
    try:
        send_mail(
            subject=notification.title,
            message=notification.message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "alerts@wexa.local"),
            recipient_list=[email_to],
            fail_silently=False,
        )

        notification.status = Notification.STATUS_SENT
        notification.sent_at = timezone.now()

    except Exception as exc:
        notification.status = Notification.STATUS_FAILED
        notification.error_message = str(exc)

    notification.save(update_fields=["status", "error_message", "sent_at"])


def send_webhook_notification(notification, webhook_url):
    try:
        payload = {
            "text": notification.title,
            "attachments": [
                {
                    "title": notification.title,
                    "text": notification.message,
                    "color": "danger",
                }
            ],
        }

        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()

        notification.status = Notification.STATUS_SENT
        notification.sent_at = timezone.now()

    except Exception as exc:
        notification.status = Notification.STATUS_FAILED
        notification.error_message = str(exc)

    notification.save(update_fields=["status", "error_message", "sent_at"])


def evaluate_alert_rule(alert_rule):
    now = timezone.now()

    if alert_rule.is_muted_now():
        alert_rule.status = AlertRule.STATUS_MUTED
        alert_rule.last_evaluated_at = now
        alert_rule.save(update_fields=["status", "last_evaluated_at"])

        AlertHistory.objects.create(
            alert_rule=alert_rule,
            organization=alert_rule.organization,
            action=AlertHistory.ACTION_MUTED,
            threshold=alert_rule.threshold,
            message="Alert is muted currently.",
        )

        return {"status": "muted"}

    current_value = get_alert_metric_value(alert_rule)
    is_triggered = compare_values(
        current_value,
        alert_rule.operator,
        alert_rule.threshold,
    )

    old_status = alert_rule.status

    if is_triggered:
        alert_rule.status = AlertRule.STATUS_TRIGGERED
        alert_rule.last_triggered_value = current_value

        message = (
            f"Alert '{alert_rule.name}' triggered. "
            f"Current value: {current_value}, "
            f"Threshold: {alert_rule.operator} {alert_rule.threshold}, "
            f"Window: {alert_rule.time_window_minutes} minutes."
        )

        AlertHistory.objects.create(
            alert_rule=alert_rule,
            organization=alert_rule.organization,
            action=AlertHistory.ACTION_TRIGGERED,
            triggered_value=current_value,
            threshold=alert_rule.threshold,
            message=message,
        )

        if old_status != AlertRule.STATUS_TRIGGERED:
            title = f"Alert Triggered: {alert_rule.name}"

            if alert_rule.enable_in_app:
                notification = create_notification(
                    alert_rule,
                    Notification.CHANNEL_IN_APP,
                    title,
                    message,
                )
                notification.status = Notification.STATUS_SENT
                notification.sent_at = timezone.now()
                notification.save(update_fields=["status", "sent_at"])

            if alert_rule.enable_email and alert_rule.email_to:
                notification = create_notification(
                    alert_rule,
                    Notification.CHANNEL_EMAIL,
                    title,
                    message,
                )
                send_email_notification(notification, alert_rule.email_to)

            if alert_rule.enable_webhook and alert_rule.webhook_url:
                notification = create_notification(
                    alert_rule,
                    Notification.CHANNEL_WEBHOOK,
                    title,
                    message,
                )
                send_webhook_notification(notification, alert_rule.webhook_url)

    else:
        if old_status == AlertRule.STATUS_TRIGGERED:
            AlertHistory.objects.create(
                alert_rule=alert_rule,
                organization=alert_rule.organization,
                action=AlertHistory.ACTION_RESOLVED,
                triggered_value=current_value,
                threshold=alert_rule.threshold,
                message=f"Alert '{alert_rule.name}' resolved. Current value: {current_value}.",
            )

        alert_rule.status = AlertRule.STATUS_ACTIVE

    alert_rule.last_evaluated_at = now
    alert_rule.save(
        update_fields=[
            "status",
            "last_triggered_value",
            "last_evaluated_at",
            "updated_at",
        ]
    )

    return {
        "status": alert_rule.status,
        "value": current_value,
        "threshold": str(alert_rule.threshold),
    }


def evaluate_all_alerts():
    rules = AlertRule.objects.select_related("organization").all()
    results = []

    for rule in rules:
        results.append(
            {
                "alert_id": rule.id,
                "name": rule.name,
                "result": evaluate_alert_rule(rule),
            }
        )

    return results