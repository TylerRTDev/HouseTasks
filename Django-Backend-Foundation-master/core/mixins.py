from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import ContextMixin

from .permissions import get_workspace_or_404


class WorkspaceContextMixin(LoginRequiredMixin, ContextMixin):
    """
    Loads workspace from URL kwarg `workspace_slug`, enforces membership,
    and injects `workspace` into template context.
    """
    workspace = None

    def dispatch(self, request, *args, **kwargs):
        self.workspace = get_workspace_or_404(user=request.user, slug=kwargs["workspace_slug"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["workspace"] = self.workspace
        return ctx
