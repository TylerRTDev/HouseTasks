from django.views.generic import ListView
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.db.models import Prefetch

from core.mixins import WorkspaceContextMixin
from .forms import TaskForm
from .models import Task, TaskAssignment



class TaskListView(WorkspaceContextMixin, ListView):
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"

    def get_queryset(self):
        assignment_qs = TaskAssignment.objects.select_related("user").order_by("user__username")

        return (
            Task.objects.filter(workspace=self.workspace, parent__isnull=True)
            .select_related("workspace", "parent", "created_by")
            .prefetch_related(
                "assignees",
                Prefetch("assignments", queryset=assignment_qs),
                Prefetch("subtasks__assignments", queryset=assignment_qs),
            )
        )

class TaskCreateView(WorkspaceContextMixin, View):
    def get(self, request, workspace_slug: str):
        form = TaskForm(workspace=self.workspace)
        return render(request, "tasks/task_form.html", {"form": form, "workspace": self.workspace})

    def post(self, request, workspace_slug: str):
        form = TaskForm(request.POST, workspace=self.workspace)
        if not form.is_valid():
            return render(request, "tasks/task_form.html", {"form": form, "workspace": self.workspace})

        task = form.save(commit=False)
        task.workspace = self.workspace
        task.created_by = request.user
        task.save()

        assignees = form.cleaned_data["assignees"]
        TaskAssignment.objects.bulk_create(
            [
                TaskAssignment(task=task, user=u, assigned_by=request.user)
                for u in assignees
            ],
            ignore_conflicts=True,
        )

        messages.success(request, "Task created.")
        return redirect("tasks:task_list", workspace_slug=self.workspace.slug)

class TaskToggleCompleteView(WorkspaceContextMixin, View):
    def post(self, request, workspace_slug: str, task_id: str):
        task = get_object_or_404(Task, id=task_id, workspace=self.workspace)

        task.is_complete = not task.is_complete
        task.completed_at = timezone.now() if task.is_complete else None
        task.save(update_fields=["is_complete", "completed_at", "updated_at"])

        # Return just the updated row HTML for HTMX swaps
        return render(request, "tasks/partials/task_row.html", {"task": task, "workspace": self.workspace})

class TaskUpdateView(WorkspaceContextMixin, View):
    def post(self, request, workspace_slug: str, task_id: str):
        task = get_object_or_404(Task, id=task_id, workspace=self.workspace)
        form = TaskForm(request.POST, instance=task, workspace=self.workspace)

        if not form.is_valid():
            return render(
                request,
                "tasks/partials/task_edit_form.html",
                {"form": form, "task": task, "workspace": self.workspace},
            )

        task = form.save()
        task.assignments.all().delete()

        TaskAssignment.objects.bulk_create(
            [
                TaskAssignment(task=task, user=u, assigned_by=request.user)
                for u in form.cleaned_data["assignees"]
            ],
            ignore_conflicts=True,
        )

        return render(
            request,
            "tasks/partials/task_row.html",
            {"task": task, "workspace": self.workspace},
        )

class TaskEditView(WorkspaceContextMixin, View):
    def get(self, request, workspace_slug: str, task_id: str):
        task = get_object_or_404(Task, id=task_id, workspace=self.workspace)
        form = TaskForm(instance=task, workspace=self.workspace)
        return render(
            request,
            "tasks/partials/task_edit_form.html",
            {"form": form, "task": task, "workspace": self.workspace},
        )


class TaskDeleteView(WorkspaceContextMixin, View):
    def delete(self, request, workspace_slug: str, task_id: str):
        task = get_object_or_404(Task, id=task_id, workspace=self.workspace)
        task.delete()
        return HttpResponse("")


class SubtaskFormView(WorkspaceContextMixin, View):
    def get(self, request, workspace_slug: str, task_id: str):
        parent = get_object_or_404(Task, id=task_id, workspace=self.workspace)
        form = TaskForm(workspace=self.workspace)
        return render(
            request,
            "tasks/partials/subtask_form.html",
            {"form": form, "workspace": self.workspace, "parent": parent},
        )

class SubtaskCreateView(WorkspaceContextMixin, View):
    def post(self, request, workspace_slug: str, task_id: str):
        parent = get_object_or_404(Task, id=task_id, workspace=self.workspace)
        form = TaskForm(request.POST, workspace=self.workspace)

        if not form.is_valid():
            return render(
                request,
                "tasks/partials/subtask_form.html",
                {"form": form, "workspace": self.workspace, "parent": parent},
            )

        subtask = form.save(commit=False)
        subtask.workspace = self.workspace
        subtask.created_by = request.user
        subtask.parent = parent
        subtask.save()

        assignees = form.cleaned_data["assignees"]
        TaskAssignment.objects.bulk_create(
            [TaskAssignment(task=subtask, user=u, assigned_by=request.user) for u in assignees],
            ignore_conflicts=True,
        )

        # Return the new subtask row so HTMX can append it
        return render(
            request,
            "tasks/partials/subtask_row.html",
            {"task": subtask, "workspace": self.workspace},
        )


class TaskRowView(WorkspaceContextMixin, View):
    def get(self, request, workspace_slug: str, task_id: str):
        task = get_object_or_404(Task, id=task_id, workspace=self.workspace)

        template = "tasks/partials/task_row.html" if task.parent_id is None else "tasks/partials/subtask_row.html"

        return render(
            request,
            template,
            {"task": task, "workspace": self.workspace},
        )
