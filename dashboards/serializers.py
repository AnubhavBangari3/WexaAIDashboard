from rest_framework import serializers
from .models import Dashboard, SavedQuery, Widget


class SavedQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedQuery
        fields = [
            "id",
            "name",
            "event_name",
            "metric",
            "group_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class WidgetSerializer(serializers.ModelSerializer):
    saved_query_detail = SavedQuerySerializer(source="saved_query", read_only=True)

    class Meta:
        model = Widget
        fields = [
            "id",
            "dashboard",
            "saved_query",
            "saved_query_detail",
            "title",
            "widget_type",
            "time_range",
            "position_x",
            "position_y",
            "width",
            "height",
            "config",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "dashboard",
            "created_at",
            "updated_at",
        ]

class DashboardSerializer(serializers.ModelSerializer):
    widgets = WidgetSerializer(many=True, read_only=True)

    class Meta:
        model = Dashboard
        fields = [
            "id",
            "name",
            "description",
            "access_type",
            "auto_refresh_interval",
            "is_template",
            "template_type",
            "widgets",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_template", "template_type", "created_at", "updated_at"]