from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def _send_to_org(organization_id, handler_type, payload):
    if not organization_id:
        return

    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    async_to_sync(channel_layer.group_send)(
        f"org_{organization_id}",
        {
            "type": handler_type,
            "payload": payload,
        },
    )


def broadcast_event(organization_id, event_type, payload):
    """
    Generic realtime event broadcaster.
    Use this from ingestion/views.py or ingestion/tasks.py.
    """

    _send_to_org(
        organization_id=organization_id,
        handler_type="live_event",
        payload={
            "type": event_type,
            "event": payload,
        },
    )

    _send_to_org(
        organization_id=organization_id,
        handler_type="dashboard_refresh",
        payload={
            "type": "dashboard_refresh",
            "reason": event_type,
            "event": payload,
        },
    )


def serialize_event(event):
    return {
        "id": event.id,
        "event_name": getattr(event, "event_name", ""),
        "source_type": getattr(event, "source_type", ""),
        "payload": getattr(event, "payload", {}),
        "normalized_payload": getattr(event, "normalized_payload", {}),
        "status": getattr(event, "status", None),
        "error_message": getattr(event, "error_message", ""),
        "occurred_at": event.occurred_at.isoformat()
        if getattr(event, "occurred_at", None)
        else None,
        "received_at": event.received_at.isoformat()
        if getattr(event, "received_at", None)
        else None,
    }


def broadcast_event_created(event):
    broadcast_event(
        organization_id=event.organization_id,
        event_type="event.created",
        payload=serialize_event(event),
    )


def broadcast_event_processed(event):
    broadcast_event(
        organization_id=event.organization_id,
        event_type="event.processed",
        payload=serialize_event(event),
    )


def broadcast_alert(notification):
    alert_rule = getattr(notification, "alert_rule", None)

    _send_to_org(
        organization_id=notification.organization_id,
        handler_type="live_alert",
        payload={
            "type": "alert.triggered",
            "notification": {
                "id": notification.id,
                "title": getattr(notification, "title", "Alert Triggered"),
                "message": getattr(notification, "message", ""),
                "is_read": getattr(notification, "is_read", False),
                "created_at": notification.created_at.isoformat()
                if getattr(notification, "created_at", None)
                else None,
                "alert_rule": alert_rule.name if alert_rule else None,
            },
        },
    )