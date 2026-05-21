from celery import shared_task
from django.utils import timezone

from .models import ScheduledReport
from .services import create_report_history, calculate_next_run


@shared_task(name="reports.tasks.generate_scheduled_report_task")
def generate_scheduled_report_task(report_id):
    report = ScheduledReport.objects.select_related(
        "dashboard",
        "organization",
    ).get(id=report_id)

    history = create_report_history(report)

    report.last_run_at = timezone.now()
    report.next_run_at = calculate_next_run(report)
    report.save(update_fields=["last_run_at", "next_run_at", "updated_at"])

    return {
        "report_id": report.id,
        "history_id": history.id,
        "status": history.status,
    }


@shared_task(name="reports.tasks.process_due_scheduled_reports_task")
def process_due_scheduled_reports_task():
    now = timezone.now()

    reports = ScheduledReport.objects.filter(
        is_active=True,
        next_run_at__lte=now,
    )

    count = 0

    for report in reports:
        generate_scheduled_report_task.delay(report.id)
        count += 1

    return {"queued_reports": count}