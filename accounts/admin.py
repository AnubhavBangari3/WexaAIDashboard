from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "role",
        "organization",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "role",
        "organization",
        "is_staff",
        "is_superuser",
        "is_active",
    )
    search_fields = ("username", "email", "organization__name")

    fieldsets = UserAdmin.fieldsets + (
        ("Organization & Role", {"fields": ("organization", "role")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Organization & Role", {"fields": ("organization", "role", "email")}),
    )