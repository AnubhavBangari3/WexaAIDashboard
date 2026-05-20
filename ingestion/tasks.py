from celery import shared_task
from .models import Event
from .services import normalize_event_payload


@shared_task(bind=True, max_retries=3)
def process_event_task(self, event_id):
    try:
        event = Event.objects.get(id=event_id)
        event.normalized_payload = normalize_event_payload(
            event.event_name,
            event.payload,
        )
        event.status = Event.STATUS_PROCESSED
        event.error_message = None
        event.save(update_fields=["normalized_payload", "status", "error_message"])
        return {"event_id": event.id, "status": "processed"}

    except Event.DoesNotExist:
        return {"event_id": event_id, "status": "not_found"}

    except Exception as exc:
        try:
            event = Event.objects.get(id=event_id)
            event.status = Event.STATUS_FAILED
            event.error_message = str(exc)
            event.save(update_fields=["status", "error_message"])
        except Event.DoesNotExist:
            pass

        raise self.retry(exc=exc, countdown=10)