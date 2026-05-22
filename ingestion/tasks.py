from celery import shared_task
from django.utils import timezone

from .models import Event


@shared_task(bind=True)
def process_event_task(self, event_id):
    try:
        event = Event.objects.get(id=event_id)

        processed_payload = {
            **event.payload,
            "processed": True,
            "processed_at": timezone.now().isoformat(),
        }

        event.payload = processed_payload
        event.status = Event.STATUS_PROCESSED
        event.error_message = ""

        event.save(
            update_fields=[
                "payload",
                "status",
                "error_message",
            ]
        )

        return {
            "status": "processed",
            "event_id": event.id,
        }

    except Exception as exc:
        try:
            event = Event.objects.get(id=event_id)
            event.status = Event.STATUS_FAILED
            event.error_message = str(exc)

            event.save(
                update_fields=[
                    "status",
                    "error_message",
                ]
            )

        except Exception:
            pass

        return {
            "status": "failed",
            "reason": str(exc),
            "event_id": event_id,
        }