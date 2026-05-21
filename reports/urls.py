from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ScheduledReportViewSet, ReportHistoryViewSet

router = DefaultRouter()
router.register("scheduled", ScheduledReportViewSet, basename="scheduled-report")
router.register("history", ReportHistoryViewSet, basename="report-history")

urlpatterns = [
    path("", include(router.urls)),
]