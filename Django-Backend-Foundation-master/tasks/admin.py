from django.contrib import admin
from .models import Task, TaskAssignment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "workspace", "is_complete", "due_date", "parent", "created_at")
    list_filter = ("workspace", "is_complete")
    search_fields = ("title", "description")
    autocomplete_fields = ("workspace", "created_by", "parent")


@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ("task", "user", "assigned_by", "assigned_at")
    search_fields = ("task__title", "user__username", "user__email")
