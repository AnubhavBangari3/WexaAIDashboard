from django.db import models
from django.conf import settings


class Dashboard(models.Model):
    ACCESS_TEAM = "team"
    ACCESS_PUBLIC = "public"

    ACCESS_CHOICES = [
        (ACCESS_TEAM, "Team Only"),
        (ACCESS_PUBLIC, "Public Read Only"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="dashboards",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    access_type = models.CharField(
        max_length=20,
        choices=ACCESS_CHOICES,
        default=ACCESS_TEAM,
    )
    auto_refresh_interval = models.PositiveIntegerField(default=30)
    is_template = models.BooleanField(default=False)
    template_type = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_dashboards",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["organization", "access_type"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.organization.name}"


class SavedQuery(models.Model):
    METRIC_COUNT = "count"
    METRIC_UNIQUE_USERS = "unique_users"
    METRIC_TOTAL_VALUE = "total_value"

    METRIC_CHOICES = [
        (METRIC_COUNT, "Event Count"),
        (METRIC_UNIQUE_USERS, "Unique Users"),
        (METRIC_TOTAL_VALUE, "Total Value"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="saved_queries",
    )
    name = models.CharField(max_length=255)
    event_name = models.CharField(max_length=255, blank=True)
    metric = models.CharField(max_length=50, choices=METRIC_CHOICES, default=METRIC_COUNT)
    group_by = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Widget(models.Model):
    TYPE_LINE = "line"
    TYPE_BAR = "bar"
    TYPE_PIE = "pie"
    TYPE_KPI = "kpi"
    TYPE_TABLE = "table"

    WIDGET_CHOICES = [
        (TYPE_LINE, "Line Chart"),
        (TYPE_BAR, "Bar Chart"),
        (TYPE_PIE, "Pie Chart"),
        (TYPE_KPI, "KPI Card"),
        (TYPE_TABLE, "Table"),
    ]

    RANGE_24H = "24h"
    RANGE_7D = "7d"
    RANGE_30D = "30d"

    RANGE_CHOICES = [
        (RANGE_24H, "Last 24 Hours"),
        (RANGE_7D, "Last 7 Days"),
        (RANGE_30D, "Last 30 Days"),
    ]

    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        related_name="widgets",
    )
    saved_query = models.ForeignKey(
        SavedQuery,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="widgets",
    )
    title = models.CharField(max_length=255)
    widget_type = models.CharField(max_length=20, choices=WIDGET_CHOICES)
    time_range = models.CharField(max_length=10, choices=RANGE_CHOICES, default=RANGE_7D)
    position_x = models.PositiveIntegerField(default=0)
    position_y = models.PositiveIntegerField(default=0)
    width = models.PositiveIntegerField(default=6)
    height = models.PositiveIntegerField(default=4)
    config = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position_y", "position_x"]

    def __str__(self):
        return self.title