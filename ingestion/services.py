from django.utils import timezone


def normalize_event_payload(event_name, payload):
    return {
        "event_name": event_name,
        "payload": payload,
        "normalized_at": timezone.now().isoformat(),
    }