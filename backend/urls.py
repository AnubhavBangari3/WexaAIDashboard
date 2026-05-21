from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/auth/", include("accounts.urls")),
    path("api/organizations/", include("organizations.urls")),
    path("api/ingestion/", include("ingestion.urls")),
    path("api/dashboards/", include("dashboards.urls")),
    path("api/alerts/", include("alerts.urls")),
    path("api/reports/", include("reports.urls")),
]