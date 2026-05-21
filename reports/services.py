import os
from io import BytesIO
from datetime import timedelta

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.utils import timezone

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw

from .models import ScheduledReport, ReportHistory


def calculate_next_run(report: ScheduledReport):
    current = report.next_run_at or timezone.now()

    if report.frequency == ScheduledReport.FREQUENCY_DAILY:
        return current + timedelta(days=1)

    if report.frequency == ScheduledReport.FREQUENCY_WEEKLY:
        return current + timedelta(weeks=1)

    if report.frequency == ScheduledReport.FREQUENCY_MONTHLY:
        return current + timedelta(days=30)

    return current + timedelta(days=1)


def generate_dashboard_pdf(report: ScheduledReport):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    dashboard = report.dashboard

    y = height - 60
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, f"Dashboard Report: {dashboard.name}")

    y -= 30
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, y, f"Generated At: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 20
    pdf.drawString(50, y, f"Report Name: {report.name}")
    y -= 20
    pdf.drawString(50, y, f"Frequency: {report.frequency}")

    y -= 40
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Widgets")

    y -= 25
    pdf.setFont("Helvetica", 11)

    widgets = dashboard.widgets.all()

    if not widgets.exists():
        pdf.drawString(50, y, "No widgets found in this dashboard.")
    else:
        for widget in widgets:
            if y < 80:
                pdf.showPage()
                y = height - 60
                pdf.setFont("Helvetica", 11)

            pdf.drawString(50, y, f"- {widget.title}")
            y -= 18
            pdf.drawString(70, y, f"Type: {widget.widget_type} | Time Range: {widget.time_range}")
            y -= 18

            if widget.saved_query:
                pdf.drawString(70, y, f"Saved Query: {widget.saved_query.name}")
                y -= 18

            y -= 10

    pdf.save()
    buffer.seek(0)
    return buffer


def generate_dashboard_png(report: ScheduledReport):
    image = Image.new("RGB", (1000, 700), "white")
    draw = ImageDraw.Draw(image)

    dashboard = report.dashboard

    draw.text((40, 40), f"Dashboard Report: {dashboard.name}", fill="black")
    draw.text((40, 80), f"Generated At: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}", fill="black")
    draw.text((40, 120), f"Report Name: {report.name}", fill="black")
    draw.text((40, 160), f"Frequency: {report.frequency}", fill="black")

    y = 220
    draw.text((40, y), "Widgets:", fill="black")
    y += 40

    widgets = dashboard.widgets.all()

    if not widgets.exists():
        draw.text((40, y), "No widgets found in this dashboard.", fill="black")
    else:
        for widget in widgets:
            draw.text((60, y), f"- {widget.title} | {widget.widget_type} | {widget.time_range}", fill="black")
            y += 35
            if y > 650:
                break

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def create_report_history(report: ScheduledReport):
    history = ReportHistory.objects.create(
        scheduled_report=report,
        organization=report.organization,
        dashboard=report.dashboard,
        report_name=report.name,
        report_format=report.report_format,
        status=ReportHistory.STATUS_PENDING,
    )

    try:
        if report.report_format == ScheduledReport.FORMAT_PNG:
            file_buffer = generate_dashboard_png(report)
            filename = f"report_{report.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}.png"
        else:
            file_buffer = generate_dashboard_pdf(report)
            filename = f"report_{report.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}.pdf"

        history.file.save(filename, ContentFile(file_buffer.read()))
        history.status = ReportHistory.STATUS_SUCCESS
        history.error_message = ""
        history.save()

        send_report_email(report, history)

    except Exception as exc:
        history.status = ReportHistory.STATUS_FAILED
        history.error_message = str(exc)
        history.save()

    return history


def send_report_email(report: ScheduledReport, history: ReportHistory):
    if not report.recipients:
        return

    recipients = [
        email.strip()
        for email in report.recipients.split(",")
        if email.strip()
    ]

    if not recipients:
        return

    subject = f"Scheduled Report: {report.name}"
    body = f"""
Hi,

Your scheduled dashboard report has been generated.

Report: {report.name}
Dashboard: {report.dashboard.name}
Status: {history.status}
Generated At: {history.generated_at}

Regards,
Wexa AI Dashboard
"""

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "reports@wexa.local"),
        to=recipients,
    )

    if history.file:
        email.attach_file(history.file.path)

    email.send(fail_silently=True)