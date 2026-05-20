from rest_framework import serializers
from .models import APIKey, Event, CSVUpload


class EventIngestSerializer(serializers.Serializer):
    event_name = serializers.CharField(max_length=255)
    payload = serializers.JSONField()
    occurred_at = serializers.DateTimeField(required=False)

    def validate_payload(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Payload must be a JSON object.")
        return value


class BatchEventIngestSerializer(serializers.Serializer):
    events = EventIngestSerializer(many=True)

    def validate_events(self, value):
        if not value:
            raise serializers.ValidationError("Events list cannot be empty.")
        if len(value) > 500:
            raise serializers.ValidationError("Maximum 500 events allowed in one batch.")
        return value


class EventResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "event_name",
            "source_type",
            "payload",
            "normalized_payload",
            "status",
            "error_message",
            "occurred_at",
            "received_at",
        ]


class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ["id", "name", "key", "is_active", "created_at", "revoked_at"]
        read_only_fields = ["key", "created_at", "revoked_at"]


class CSVUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CSVUpload
        fields = [
            "id",
            "file",
            "total_rows",
            "successful_rows",
            "failed_rows",
            "created_at",
        ]
        read_only_fields = ["total_rows", "successful_rows", "failed_rows", "created_at"]