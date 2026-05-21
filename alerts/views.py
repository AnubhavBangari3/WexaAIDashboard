from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import AlertRule, AlertHistory, Notification
from .serializers import (
    AlertRuleSerializer,
    AlertHistorySerializer,
    NotificationSerializer,
)
from .services import evaluate_alert_rule, evaluate_all_alerts


class AlertRuleViewSet(viewsets.ModelViewSet):
    serializer_class = AlertRuleSerializer

    def get_queryset(self):
        return AlertRule.objects.filter(
            organization=self.request.user.organization
        )

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
        )

    @action(detail=True, methods=["post"])
    def evaluate(self, request, pk=None):
        alert = self.get_object()
        result = evaluate_alert_rule(alert)
        return Response(result)

    @action(detail=False, methods=["post"], url_path="evaluate-all")
    def evaluate_all(self, request):
        result = evaluate_all_alerts()
        return Response(result)

    @action(detail=True, methods=["post"])
    def mute(self, request, pk=None):
        alert = self.get_object()
        minutes = int(request.data.get("minutes", 60))

        alert.status = AlertRule.STATUS_MUTED
        alert.muted_until = timezone.now() + timezone.timedelta(minutes=minutes)
        alert.save(update_fields=["status", "muted_until", "updated_at"])

        AlertHistory.objects.create(
            alert_rule=alert,
            organization=request.user.organization,
            action=AlertHistory.ACTION_MUTED,
            threshold=alert.threshold,
            message=f"Alert muted for {minutes} minutes.",
        )

        return Response(AlertRuleSerializer(alert).data)

    @action(detail=True, methods=["post"])
    def unmute(self, request, pk=None):
        alert = self.get_object()
        alert.status = AlertRule.STATUS_ACTIVE
        alert.muted_until = None
        alert.save(update_fields=["status", "muted_until", "updated_at"])
        return Response(AlertRuleSerializer(alert).data)


class AlertHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AlertHistorySerializer

    def get_queryset(self):
        return AlertHistory.objects.filter(
            organization=self.request.user.organization
        ).select_related("alert_rule")


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(
            organization=self.request.user.organization
        ).select_related("alert_rule")

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=["is_read"])
        return Response(NotificationSerializer(notification).data)