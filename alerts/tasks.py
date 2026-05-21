from celery import shared_task

from backend.realtime import broadcast_alert

from .models import AlertRule, Notification
from .services import (
    evaluate_all_alerts,
    evaluate_alert_rule,
    send_email_notification,
    send_webhook_notification,
)


def broadcast_new_notifications(before_ids):
    notifications = Notification.objects.exclude(
        id__in=before_ids
    ).select_related(
        "organization",
        "alert_rule",
    )

    for notification in notifications:
        broadcast_alert(notification)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def evaluate_alerts_task(self):
    before_ids = set(
        Notification.objects.values_list(
            "id",
            flat=True,
        )
    )

    result = evaluate_all_alerts()

    broadcast_new_notifications(before_ids)

    return result


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def evaluate_single_alert_task(self, alert_id):
    before_ids = set(
        Notification.objects.values_list(
            "id",
            flat=True,
        )
    )

    alert = AlertRule.objects.get(id=alert_id)
    result = evaluate_alert_rule(alert)

    broadcast_new_notifications(before_ids)

    return result


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_email_notification_task(self, notification_id, email_to):
    result = send_email_notification(
        notification_id=notification_id,
        email_to=email_to,
    )

    notification = Notification.objects.get(id=notification_id)
    broadcast_alert(notification)

    return result


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_webhook_notification_task(self, notification_id, webhook_url):
    result = send_webhook_notification(
        notification_id=notification_id,
        webhook_url=webhook_url,
    )

    notification = Notification.objects.get(id=notification_id)
    broadcast_alert(notification)

    return result