from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from core.permissions import get_workspace_or_404, require_owner
from .forms import AddMemberForm, WorkspaceCreateForm, WorkspaceUpdateForm
from .models import Workspace, WorkspaceMembership


class WorkspaceChooserView(LoginRequiredMixin, View):
    def get(self, request):
        memberships = (
            WorkspaceMembership.objects.select_related("workspace")
            .filter(user=request.user)
            .order_by("workspace__name")
        )
        workspaces = [m.workspace for m in memberships]

        if len(workspaces) == 1:
            return redirect("tasks:task_list", workspace_slug=workspaces[0].slug)

        return render(request, "workspaces/chooser.html", {"workspaces": workspaces})


class WorkspaceCreateView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "workspaces/create.html", {"form": WorkspaceCreateForm()})

    @transaction.atomic
    def post(self, request):
        form = WorkspaceCreateForm(request.POST)
        if not form.is_valid():
            return render(request, "workspaces/create.html", {"form": form})

        workspace = form.save(commit=False)
        workspace.created_by = request.user
        workspace.save()

        WorkspaceMembership.objects.create(
            workspace=workspace,
            user=request.user,
            role=WorkspaceMembership.Role.OWNER,
        )

        return redirect("tasks:task_list", workspace_slug=workspace.slug)


class WorkspaceMembersView(LoginRequiredMixin, View):
    def get(self, request, workspace_slug: str):
        workspace = get_workspace_or_404(user=request.user, slug=workspace_slug)
        require_owner(user=request.user, workspace=workspace)

        memberships = (
            WorkspaceMembership.objects.select_related("user")
            .filter(workspace=workspace)
            .order_by("-role", "user__username")
        )
        return render(
            request,
            "workspaces/members.html",
            {"workspace": workspace, "memberships": memberships, "form": AddMemberForm()},
        )

    def post(self, request, workspace_slug: str):
        workspace = get_workspace_or_404(user=request.user, slug=workspace_slug)
        require_owner(user=request.user, workspace=workspace)

        form = AddMemberForm(request.POST)
        memberships = (
            WorkspaceMembership.objects.select_related("user")
            .filter(workspace=workspace)
            .order_by("-role", "user__username")
        )

        if not form.is_valid():
            return render(
                request,
                "workspaces/members.html",
                {"workspace": workspace, "memberships": memberships, "form": form},
            )

        try:
            user_to_add = form.get_user()
        except Exception as e:
            form.add_error("identifier", str(e))
            return render(
                request,
                "workspaces/members.html",
                {"workspace": workspace, "memberships": memberships, "form": form},
            )

        WorkspaceMembership.objects.get_or_create(
            workspace=workspace,
            user=user_to_add,
            defaults={"role": form.cleaned_data["role"]},
        )

        return redirect("workspaces:members", workspace_slug=workspace.slug)
    

class WorkspaceSettingsView(LoginRequiredMixin, View):
    def get(self, request, workspace_slug: str):
        workspace = get_workspace_or_404(user=request.user, slug=workspace_slug)
        require_owner(user=request.user, workspace=workspace)

        form = WorkspaceUpdateForm(instance=workspace)
        return render(request, "workspaces/settings.html", {"workspace": workspace, "form": form})

    def post(self, request, workspace_slug: str):
        workspace = get_workspace_or_404(user=request.user, slug=workspace_slug)
        require_owner(user=request.user, workspace=workspace)

        form = WorkspaceUpdateForm(request.POST, instance=workspace)
        if not form.is_valid():
            return render(request, "workspaces/settings.html", {"workspace": workspace, "form": form})

        form.save()
        return redirect("tasks:task_list", workspace_slug=workspace.slug)
    

class WorkspaceDeleteView(LoginRequiredMixin, View):
    def post(self, request, workspace_slug: str):
        workspace = get_workspace_or_404(user=request.user, slug=workspace_slug)
        require_owner(user=request.user, workspace=workspace)

        workspace.delete()
        return redirect("workspaces:chooser")

