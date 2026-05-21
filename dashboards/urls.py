from django.urls import path
from .views import (
    DashboardDetailView,
    DashboardListCreateView,
    DashboardTemplateCreateView,
    SavedQueryListCreateView,
    WidgetDataView,
    WidgetDetailView,
    WidgetListCreateView,
)

urlpatterns = [
    path("", DashboardListCreateView.as_view(), name="dashboard-list-create"),
    path("<int:pk>/", DashboardDetailView.as_view(), name="dashboard-detail"),

    path("saved-queries/", SavedQueryListCreateView.as_view(), name="saved-query-list-create"),

    path("<int:dashboard_id>/widgets/", WidgetListCreateView.as_view(), name="widget-list-create"),
    path("widgets/<int:pk>/", WidgetDetailView.as_view(), name="widget-detail"),
    path("widgets/<int:widget_id>/data/", WidgetDataView.as_view(), name="widget-data"),

    path("templates/create/", DashboardTemplateCreateView.as_view(), name="dashboard-template-create"),
]