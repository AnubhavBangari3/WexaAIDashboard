from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlertRuleViewSet, AlertHistoryViewSet, NotificationViewSet

router = DefaultRouter()
router.register("rules", AlertRuleViewSet, basename="alert-rules")
router.register("history", AlertHistoryViewSet, basename="alert-history")
router.register("notifications", NotificationViewSet, basename="notifications")

urlpatterns = [
    path("", include(router.urls)),
]