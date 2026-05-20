from django.urls import path
from .views import (
    APIKeyListCreateView,
    APIKeyRevokeView,
    BatchEventIngestView,
    CSVUploadView,
    EventIngestView,
    EventListView,
    WebhookIngestView,
)

urlpatterns = [
    path("events/", EventListView.as_view(), name="event-list"),
    path("events/ingest/", EventIngestView.as_view(), name="event-ingest"),
    path("events/batch/", BatchEventIngestView.as_view(), name="event-batch-ingest"),
    path("events/csv-upload/", CSVUploadView.as_view(), name="csv-upload"),
    path("webhook/", WebhookIngestView.as_view(), name="webhook-ingest"),

    path("api-keys/", APIKeyListCreateView.as_view(), name="api-key-list-create"),
    path("api-keys/<int:pk>/revoke/", APIKeyRevokeView.as_view(), name="api-key-revoke"),
]