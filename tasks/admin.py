from django.contrib import admin
from tasks.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "status", "active", "created_at", "updated_at", "expires_at")
    list_filter = ("status", "active", "created_at", "updated_at", "expires_at")
    search_fields = ("title", "description", "owner__email", "owner__username")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            "fields": ("owner", "title", "description", "status", "active", "expires_at")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )
