from django.http import FileResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ScheduledReport, ReportHistory
from .serializers import ScheduledReportSerializer, ReportHistorySerializer
from .tasks import generate_scheduled_report_task


class ScheduledReportViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduledReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ScheduledReport.objects.filter(
            organization=self.request.user.organization
        ).select_related("dashboard", "organization", "created_by")

    @action(detail=True, methods=["post"])
    def run_now(self, request, pk=None):
        report = self.get_object()
        generate_scheduled_report_task.delay(report.id)

        return Response(
            {"message": "Report generation started."},
            status=status.HTTP_202_ACCEPTED,
        )


class ReportHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReportHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReportHistory.objects.filter(
            organization=self.request.user.organization
        ).select_related("dashboard", "scheduled_report", "organization")

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        history = self.get_object()

        if not history.file:
            return Response(
                {"detail": "Report file not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return FileResponse(
            history.file.open("rb"),
            as_attachment=True,
            filename=history.file.name.split("/")[-1],
        )