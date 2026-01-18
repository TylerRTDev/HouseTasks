from django.conf import settings
from django.db import models

from core.models import UUIDModel
from workspaces.models import Workspace


class Task(UUIDModel):
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Optional due dates (your requirement)
    due_date = models.DateField(null=True, blank=True)

    is_complete = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="tasks_created",
    )

    # Subtasks: a task can optionally point to a parent task
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="subtasks",
    )

    assignees = models.ManyToManyField(
    settings.AUTH_USER_MODEL,
    through="TaskAssignment",
    through_fields=("task", "user"),
    related_name="tasks_assigned",
    blank=True,
)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["is_complete", "due_date", "created_at"]

    def __str__(self) -> str:
        return self.title


class TaskAssignment(UUIDModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="assignments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="task_assignments")

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="task_assignments_made",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["task", "user"], name="uniq_task_user_assignment")
        ]

    def __str__(self) -> str:
        return f"{self.user} -> {self.task}"
