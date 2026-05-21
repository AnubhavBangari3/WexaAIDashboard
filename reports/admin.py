from django.contrib import admin
from .models import ScheduledReport, ReportHistory


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "dashboard",
        "organization",
        "frequency",
        "report_format",
        "is_active",
        "next_run_at",
        "last_run_at",
    ]
    list_filter = ["frequency", "report_format", "is_active"]
    search_fields = ["name", "dashboard__name", "organization__name"]


@admin.register(ReportHistory)
class ReportHistoryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "report_name",
        "dashboard",
        "organization",
        "report_format",
        "status",
        "generated_at",
    ]
    list_filter = ["status", "report_format"]
    search_fields = ["report_name", "dashboard__name", "organization__name"]