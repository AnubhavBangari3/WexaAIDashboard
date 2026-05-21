from datetime import timedelta
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from ingestion.models import Event
from .models import Dashboard, SavedQuery, Widget
from .serializers import DashboardSerializer, SavedQuerySerializer, WidgetSerializer


def get_user_organization(user):
    if not user.is_authenticated or not getattr(user, "organization", None):
        return None
    return user.organization


def get_start_time(time_range):
    now = timezone.now()

    if time_range == "24h":
        return now - timedelta(hours=24)

    if time_range == "30d":
        return now - timedelta(days=30)

    return now - timedelta(days=7)


def user_can_write(user):
    return getattr(user, "role", None) in ["owner", "admin", "analyst"]


class DashboardListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        organization = get_user_organization(request.user)
        if not organization:
            return Response({"detail": "User has no organization."}, status=400)

        dashboards = Dashboard.objects.filter(organization=organization)
        return Response(DashboardSerializer(dashboards, many=True).data)

    def post(self, request):
        organization = get_user_organization(request.user)
        if not organization:
            return Response({"detail": "User has no organization."}, status=400)

        if not user_can_write(request.user):
            return Response({"detail": "You do not have permission to create dashboards."}, status=403)

        serializer = DashboardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dashboard = serializer.save(
            organization=organization,
            created_by=request.user,
        )

        return Response(DashboardSerializer(dashboard).data, status=201)


class DashboardDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, pk):
        organization = get_user_organization(request.user)
        return get_object_or_404(Dashboard, pk=pk, organization=organization)

    def get(self, request, pk):
        dashboard = self.get_object(request, pk)
        return Response(DashboardSerializer(dashboard).data)

    def put(self, request, pk):
        if not user_can_write(request.user):
            return Response({"detail": "You do not have permission to update dashboards."}, status=403)

        dashboard = self.get_object(request, pk)
        serializer = DashboardSerializer(dashboard, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(DashboardSerializer(dashboard).data)

    def delete(self, request, pk):
        if not user_can_write(request.user):
            return Response({"detail": "You do not have permission to delete dashboards."}, status=403)

        dashboard = self.get_object(request, pk)
        dashboard.delete()
        return Response({"detail": "Dashboard deleted successfully."})


class SavedQueryListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        organization = get_user_organization(request.user)
        if not organization:
            return Response({"detail": "User has no organization."}, status=400)

        queries = SavedQuery.objects.filter(organization=organization)
        return Response(SavedQuerySerializer(queries, many=True).data)

    def post(self, request):
        organization = get_user_organization(request.user)
        if not organization:
            return Response({"detail": "User has no organization."}, status=400)

        if not user_can_write(request.user):
            return Response({"detail": "You do not have permission to create queries."}, status=403)

        serializer = SavedQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        query = serializer.save(
            organization=organization,
            created_by=request.user,
        )

        return Response(SavedQuerySerializer(query).data, status=201)


class WidgetListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, dashboard_id):
        organization = get_user_organization(request.user)
        dashboard = get_object_or_404(Dashboard, id=dashboard_id, organization=organization)

        widgets = Widget.objects.filter(dashboard=dashboard)
        return Response(WidgetSerializer(widgets, many=True).data)

    def post(self, request, dashboard_id):
        organization = get_user_organization(request.user)
        dashboard = get_object_or_404(Dashboard, id=dashboard_id, organization=organization)

        if not user_can_write(request.user):
            return Response({"detail": "You do not have permission to create widgets."}, status=403)

        serializer = WidgetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        saved_query = serializer.validated_data.get("saved_query")
        if saved_query and saved_query.organization != organization:
            return Response({"detail": "Invalid saved query."}, status=400)

        widget = serializer.save(dashboard=dashboard)

        return Response(WidgetSerializer(widget).data, status=201)


class WidgetDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, pk):
        organization = get_user_organization(request.user)
        return get_object_or_404(Widget, pk=pk, dashboard__organization=organization)

    def put(self, request, pk):
        if not user_can_write(request.user):
            return Response({"detail": "You do not have permission to update widgets."}, status=403)

        widget = self.get_object(request, pk)
        serializer = WidgetSerializer(widget, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        saved_query = serializer.validated_data.get("saved_query")
        if saved_query and saved_query.organization != widget.dashboard.organization:
            return Response({"detail": "Invalid saved query."}, status=400)

        serializer.save()
        return Response(WidgetSerializer(widget).data)

    def delete(self, request, pk):
        if not user_can_write(request.user):
            return Response({"detail": "You do not have permission to delete widgets."}, status=403)

        widget = self.get_object(request, pk)
        widget.delete()
        return Response({"detail": "Widget deleted successfully."})


class WidgetDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, widget_id):
        organization = get_user_organization(request.user)
        widget = get_object_or_404(
            Widget,
            id=widget_id,
            dashboard__organization=organization,
        )

        saved_query = widget.saved_query
        start_time = get_start_time(widget.time_range)

        events = Event.objects.filter(
            organization=organization,
            occurred_at__gte=start_time,
        )

        if saved_query and saved_query.event_name:
            events = events.filter(event_name=saved_query.event_name)

        if widget.widget_type == Widget.TYPE_KPI:
            return Response({
                "widget_id": widget.id,
                "type": "kpi",
                "title": widget.title,
                "value": events.count(),
            })

        if widget.widget_type == Widget.TYPE_PIE:
            data = (
                events.values("event_name")
                .annotate(value=Count("id"))
                .order_by("-value")[:10]
            )
            return Response({
                "widget_id": widget.id,
                "type": "pie",
                "data": [
                    {"name": item["event_name"], "value": item["value"]}
                    for item in data
                ],
            })

        if widget.widget_type == Widget.TYPE_BAR:
            data = (
                events.values("event_name")
                .annotate(value=Count("id"))
                .order_by("-value")[:10]
            )
            return Response({
                "widget_id": widget.id,
                "type": "bar",
                "data": [
                    {"name": item["event_name"], "value": item["value"]}
                    for item in data
                ],
            })

        trunc = TruncHour if widget.time_range == "24h" else TruncDate

        data = (
            events.annotate(bucket=trunc("occurred_at"))
            .values("bucket")
            .annotate(value=Count("id"))
            .order_by("bucket")
        )

        return Response({
            "widget_id": widget.id,
            "type": "line",
            "data": [
                {
                    "name": item["bucket"].strftime("%Y-%m-%d %H:%M"),
                    "value": item["value"],
                }
                for item in data
            ],
        })


class DashboardTemplateCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        organization = get_user_organization(request.user)
        if not organization:
            return Response({"detail": "User has no organization."}, status=400)

        if not user_can_write(request.user):
            return Response({"detail": "You do not have permission to create templates."}, status=403)

        template_type = request.data.get("template_type", "web_analytics")

        dashboard = Dashboard.objects.create(
            organization=organization,
            name="Web Analytics Dashboard" if template_type == "web_analytics" else "Sales Dashboard",
            description="Auto-created dashboard template",
            access_type=Dashboard.ACCESS_TEAM,
            auto_refresh_interval=30,
            template_type=template_type,
            created_by=request.user,
        )

        q1 = SavedQuery.objects.create(
            organization=organization,
            name="All Events",
            event_name="",
            metric="count",
            created_by=request.user,
        )

        Widget.objects.create(
            dashboard=dashboard,
            saved_query=q1,
            title="Total Events",
            widget_type=Widget.TYPE_KPI,
            time_range="7d",
            position_x=0,
            position_y=0,
            width=3,
            height=2,
        )

        Widget.objects.create(
            dashboard=dashboard,
            saved_query=q1,
            title="Events Over Time",
            widget_type=Widget.TYPE_LINE,
            time_range="7d",
            position_x=3,
            position_y=0,
            width=6,
            height=4,
        )

        Widget.objects.create(
            dashboard=dashboard,
            saved_query=q1,
            title="Events By Type",
            widget_type=Widget.TYPE_BAR,
            time_range="7d",
            position_x=0,
            position_y=4,
            width=6,
            height=4,
        )

        Widget.objects.create(
            dashboard=dashboard,
            saved_query=q1,
            title="Event Distribution",
            widget_type=Widget.TYPE_PIE,
            time_range="7d",
            position_x=6,
            position_y=4,
            width=6,
            height=4,
        )

        return Response(DashboardSerializer(dashboard).data, status=201)