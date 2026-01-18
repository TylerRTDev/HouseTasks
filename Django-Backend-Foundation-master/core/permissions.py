from typing import Optional
from django.contrib.auth import get_user_model
from django.http import Http404

from workspaces.models import Workspace, WorkspaceMembership

User = get_user_model()


def user_is_workspace_member(*, user: User, workspace: Workspace) -> bool:
    if not user.is_authenticated:
        return False
    return WorkspaceMembership.objects.filter(workspace=workspace, user=user).exists()


def get_workspace_or_404(*, user: User, slug: str) -> Workspace:
    try:
        workspace = Workspace.objects.get(slug=slug)
    except Workspace.DoesNotExist as exc:
        raise Http404("Workspace not found") from exc

    if not user_is_workspace_member(user=user, workspace=workspace):
        # 404 prevents leaking that the workspace exists
        raise Http404("Workspace not found")

    return workspace


def require_owner(*, user: User, workspace: Workspace) -> None:
    is_owner = WorkspaceMembership.objects.filter(
        workspace=workspace,
        user=user,
        role=WorkspaceMembership.Role.OWNER,
    ).exists()
    if not is_owner:
        raise Http404("Workspace not found")
