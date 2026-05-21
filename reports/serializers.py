from rest_framework import serializers
from .models import ScheduledReport, ReportHistory


class ReportHistorySerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    dashboard_name = serializers.CharField(source="dashboard.name", read_only=True)

    class Meta:
        model = ReportHistory
        fields = [
            "id",
            "scheduled_report",
            "dashboard",
            "dashboard_name",
            "report_name",
            "report_format",
            "file_url",
            "status",
            "error_message",
            "generated_at",
        ]

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        if obj.file:
            return obj.file.url
        return None


class ScheduledReportSerializer(serializers.ModelSerializer):
    dashboard_name = serializers.CharField(source="dashboard.name", read_only=True)

    class Meta:
        model = ScheduledReport
        fields = [
            "id",
            "dashboard",
            "dashboard_name",
            "name",
            "frequency",
            "report_format",
            "recipients",
            "is_active",
            "next_run_at",
            "last_run_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["last_run_at", "created_at", "updated_at"]

    def validate_dashboard(self, dashboard):
        request = self.context["request"]
        if dashboard.organization_id != request.user.organization_id:
            raise serializers.ValidationError("Invalid dashboard.")
        return dashboard

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["organization"] = request.user.organization
        validated_data["created_by"] = request.user
        return super().create(validated_data)