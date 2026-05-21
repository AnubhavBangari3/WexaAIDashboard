import csv
from django.core.cache import cache
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from backend.realtime import broadcast_event

from .models import APIKey, Event, CSVUpload
from .serializers import (
    APIKeySerializer,
    BatchEventIngestSerializer,
    CSVUploadSerializer,
    EventIngestSerializer,
    EventResponseSerializer,
)
from .tasks import process_event_task


RATE_LIMIT_WINDOW_SECONDS = 60

AUTH_USER_RATE_LIMIT = 120
API_KEY_RATE_LIMIT = 300
CSV_UPLOAD_RATE_LIMIT = 20


def get_user_organization(user):
    if not user.is_authenticated or not getattr(user, "organization", None):
        return None
    return user.organization


def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def check_rate_limit(key, limit, window_seconds=RATE_LIMIT_WINDOW_SECONDS):
    """
    Redis-backed fixed-window rate limiter.
    Uses Django cache, which is configured to Redis in settings.py.
    """
    current_count = cache.get(key)

    if current_count is None:
        cache.set(key, 1, timeout=window_seconds)
        return True, limit - 1

    if int(current_count) >= limit:
        return False, 0

    try:
        new_count = cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=window_seconds)
        new_count = 1

    remaining = max(limit - int(new_count), 0)
    return True, remaining


def enforce_authenticated_rate_limit(request, organization, action="ingestion"):
    user_id = getattr(request.user, "id", "anonymous")
    org_id = organization.id
    ip = get_client_ip(request)

    key = f"rate_limit:auth:{action}:org:{org_id}:user:{user_id}:ip:{ip}"

    allowed, remaining = check_rate_limit(
        key=key,
        limit=AUTH_USER_RATE_LIMIT,
    )

    if not allowed:
        return Response(
            {
                "detail": "Rate limit exceeded. Please try again later.",
                "limit": AUTH_USER_RATE_LIMIT,
                "window_seconds": RATE_LIMIT_WINDOW_SECONDS,
            },
            status=429,
        )

    return None


def enforce_api_key_rate_limit(request, api_key, action="webhook"):
    ip = get_client_ip(request)

    key = f"rate_limit:api_key:{action}:org:{api_key.organization_id}:key:{api_key.id}:ip:{ip}"

    allowed, remaining = check_rate_limit(
        key=key,
        limit=API_KEY_RATE_LIMIT,
    )

    if not allowed:
        return Response(
            {
                "detail": "API key rate limit exceeded. Please try again later.",
                "limit": API_KEY_RATE_LIMIT,
                "window_seconds": RATE_LIMIT_WINDOW_SECONDS,
            },
            status=429,
        )

    return None


def enforce_csv_rate_limit(request, organization):
    user_id = getattr(request.user, "id", "anonymous")
    org_id = organization.id

    key = f"rate_limit:csv_upload:org:{org_id}:user:{user_id}"

    allowed, remaining = check_rate_limit(
        key=key,
        limit=CSV_UPLOAD_RATE_LIMIT,
    )

    if not allowed:
        return Response(
            {
                "detail": "CSV upload rate limit exceeded. Please try again later.",
                "limit": CSV_UPLOAD_RATE_LIMIT,
                "window_seconds": RATE_LIMIT_WINDOW_SECONDS,
            },
            status=429,
        )

    return None


def broadcast_ingestion_event(event):
    try:
        broadcast_event(
            organization_id=event.organization_id,
            event_type="event.created",
            payload={
                "id": event.id,
                "event_name": event.event_name,
                "payload": event.payload,
                "source_type": event.source_type,
                "occurred_at": event.occurred_at.isoformat() if event.occurred_at else None,
                "created_at": event.created_at.isoformat()
                if hasattr(event, "created_at") and event.created_at
                else None,
            },
        )
    except Exception as exc:
        print("Realtime broadcast failed:", exc)


class APIKeyListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        organization = get_user_organization(request.user)
        if not organization:
            return Response({"detail": "User has no organization."}, status=400)

        keys = APIKey.objects.filter(organization=organization)
        return Response(APIKeySerializer(keys, many=True).data)

    def post(self, request):
        organization = get_user_organization(request.user)
        if not organization:
            return Response({"detail": "User has no organization."}, status=400)

        if request.user.role not in ["owner", "admin"]:
            return Response({"detail": "Only Owner/Admin can create API keys."}, status=403)

        serializer = APIKeySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        api_key = serializer.save(
            organization=organization,
            created_by=request.user,
        )

        return Response(APIKeySerializer(api_key).data, status=201)


class APIKeyRevokeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        organization = get_user_organization(request.user)
        if not organization:
            return Response({"detail": "User has no organization."}, status=400)

        if request.user.role not in ["owner", "admin"]:
            return Response({"detail": "Only Owner/Admin can revoke API keys."}, status=403)

        api_key = get_object_or_404(APIKey, pk=pk, organization=organization)
        api_key.is_active = False
        api_key.revoked_at = timezone.now()
        api_key.save(update_fields=["is_active", "revoked_at"])

        return Response({"detail": "API key revoked successfully."})


class EventIngestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        organization = get_user_organization(request.user)
        if not organization:
            return Response({"detail": "User has no organization."}, status=400)

        rate_limit_response = enforce_authenticated_rate_limit(
            request=request,
            organization=organization,
            action="single_event",
        )
        if rate_limit_response:
            return rate_limit_response

        serializer = EventIngestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        event = Event.objects.create(
            organization=organization,
            event_name=data["event_name"],
            payload=data["payload"],
            source_type=Event.SOURCE_API,
            occurred_at=data.get("occurred_at") or timezone.now(),
        )

        process_event_task.delay(event.id)
        broadcast_ingestion_event(event)

        return Response(EventResponseSerializer(event).data, status=201)


class BatchEventIngestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        organization = get_user_organization(request.user)
        if not organization:
            return Response({"detail": "User has no organization."}, status=400)

        rate_limit_response = enforce_authenticated_rate_limit(
            request=request,
            organization=organization,
            action="batch_event",
        )
        if rate_limit_response:
            return rate_limit_response

        serializer = BatchEventIngestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        created_events = []

        for item in serializer.validated_data["events"]:
            event = Event.objects.create(
                organization=organization,
                event_name=item["event_name"],
                payload=item["payload"],
                source_type=Event.SOURCE_BATCH,
                occurred_at=item.get("occurred_at") or timezone.now(),
            )

            created_events.append(event)
            process_event_task.delay(event.id)
            broadcast_ingestion_event(event)

        return Response(
            {
                "created_count": len(created_events),
                "events": EventResponseSerializer(created_events, many=True).data,
            },
            status=201,
        )


class CSVUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        organization = get_user_organization(request.user)
        if not organization:
            return Response({"detail": "User has no organization."}, status=400)

        rate_limit_response = enforce_csv_rate_limit(
            request=request,
            organization=organization,
        )
        if rate_limit_response:
            return rate_limit_response

        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response({"detail": "CSV file is required."}, status=400)

        upload = CSVUpload.objects.create(
            organization=organization,
            uploaded_by=request.user,
            file=uploaded_file,
        )

        try:
            decoded_file = uploaded_file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded_file)

            total_rows = 0
            successful_rows = 0
            failed_rows = 0
            created_events = []

            for row in reader:
                total_rows += 1

                try:
                    event_name = row.get("event_name") or row.get("name") or "csv_event"

                    event = Event.objects.create(
                        organization=organization,
                        event_name=event_name,
                        payload=dict(row),
                        source_type=Event.SOURCE_CSV,
                        occurred_at=timezone.now(),
                    )

                    created_events.append(event)
                    successful_rows += 1

                    process_event_task.delay(event.id)
                    broadcast_ingestion_event(event)

                except Exception:
                    failed_rows += 1

            upload.total_rows = total_rows
            upload.successful_rows = successful_rows
            upload.failed_rows = failed_rows
            upload.save(update_fields=["total_rows", "successful_rows", "failed_rows"])

            return Response(
                {
                    "message": "CSV uploaded successfully",
                    "upload_id": upload.id,
                    "total_rows": total_rows,
                    "successful_rows": successful_rows,
                    "failed_rows": failed_rows,
                    "created_count": len(created_events),
                },
                status=201,
            )

        except Exception as e:
            return Response(
                {"detail": f"CSV upload failed: {str(e)}"},
                status=400,
            )


class WebhookIngestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        api_key_value = request.headers.get("X-API-Key")

        if not api_key_value:
            return Response({"detail": "X-API-Key header is required."}, status=401)

        api_key = get_object_or_404(APIKey, key=api_key_value, is_active=True)

        rate_limit_response = enforce_api_key_rate_limit(
            request=request,
            api_key=api_key,
            action="webhook_event",
        )
        if rate_limit_response:
            return rate_limit_response

        serializer = EventIngestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        event = Event.objects.create(
            organization=api_key.organization,
            api_key=api_key,
            event_name=data["event_name"],
            payload=data["payload"],
            source_type=Event.SOURCE_WEBHOOK,
            occurred_at=data.get("occurred_at") or timezone.now(),
        )

        process_event_task.delay(event.id)
        broadcast_ingestion_event(event)

        return Response(EventResponseSerializer(event).data, status=201)


class EventListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        organization = get_user_organization(request.user)
        if not organization:
            return Response({"detail": "User has no organization."}, status=400)

        events = Event.objects.filter(organization=organization).order_by("-occurred_at")[:100]
        return Response(EventResponseSerializer(events, many=True).data)
