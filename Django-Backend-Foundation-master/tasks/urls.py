from django.urls import path
from django.http import HttpResponse
from .views import (
    TaskListView,
    TaskCreateView,
    TaskToggleCompleteView,
    SubtaskFormView,
    SubtaskCreateView,
    TaskEditView,
    TaskUpdateView,
    TaskDeleteView,
    TaskRowView,
)

app_name = "tasks"

urlpatterns = [
    path("", TaskListView.as_view(), name="task_list"),
    path("new/", TaskCreateView.as_view(), name="task_create"),
    path("<uuid:task_id>/toggle-complete/", TaskToggleCompleteView.as_view(), name="task_toggle_complete"),
    path("<uuid:task_id>/edit/", TaskEditView.as_view(), name="task_edit"),
    path("<uuid:task_id>/update/", TaskUpdateView.as_view(), name="task_update"),
    path("<uuid:task_id>/delete/", TaskDeleteView.as_view(), name="task_delete"),
    path("<uuid:task_id>/row/", TaskRowView.as_view(), name="task_row"),

    # Subtasks (HTMX)
    path("<uuid:task_id>/subtasks/new/", SubtaskFormView.as_view(), name="subtask_form"),
    path("<uuid:task_id>/subtasks/create/", SubtaskCreateView.as_view(), name="subtask_create"),
]
