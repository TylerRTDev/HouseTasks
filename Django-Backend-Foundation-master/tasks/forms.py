from django import forms
from django.contrib.auth import get_user_model

from workspaces.models import WorkspaceMembership
from .models import Task

User = get_user_model()


class TaskForm(forms.ModelForm):
    assignees = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        help_text="Assign to one or more workspace members.",
    )

    class Meta:
        model = Task
        fields = ["title", "description", "due_date", "assignees"]

    def __init__(self, *args, workspace, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["due_date"].required = False

        member_ids = WorkspaceMembership.objects.filter(workspace=workspace).values_list("user_id", flat=True)
        self.fields["assignees"].queryset = User.objects.filter(id__in=member_ids).order_by("username")
