from celery import shared_task
from django.utils import timezone

from backend.realtime import broadcast_event

from .models import Event


@shared_task(name="ingestion.tasks.process_event_task")
def process_event_task(event_id):
    try:
        event = Event.objects.get(id=event_id)

        # Example processing logic
        processed_payload = {
            **event.payload,
            "processed": True,
            "processed_at": timezone.now().isoformat(),
        }

        event.payload = processed_payload
        event.save(update_fields=["payload"])

        # REALTIME BROADCAST
        broadcast_event(
            organization_id=event.organization_id,
            event_type="event.processed",
            payload={
                "id": event.id,
                "event_name": event.event_name,
                "payload": event.payload,
                "source_type": event.source_type,
                "occurred_at": event.occurred_at.isoformat()
                if event.occurred_at
                else None,
            },
        )

        return {
            "status": "success",
            "event_id": event.id,
        }

    except Event.DoesNotExist:
        return {
            "status": "failed",
            "reason": "event_not_found",
            "event_id": event_id,
        }

    except Exception as exc:
        return {
            "status": "failed",
            "reason": str(exc),
            "event_id": event_id,
        }