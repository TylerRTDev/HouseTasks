from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView

from core.mixins import WorkspaceContextMixin
from .forms import ListForm, ListItemForm
from .models import List, ListItem


class ListIndexView(WorkspaceContextMixin, ListView):
    template_name = "lists/list_index.html"
    context_object_name = "lists"

    def get_queryset(self):
        return List.objects.filter(workspace=self.workspace).select_related("workspace", "created_by")


class ListCreateView(WorkspaceContextMixin, View):
    def get(self, request, workspace_slug: str):
        form = ListForm()
        return render(request, "lists/list_form.html", {"form": form, "workspace": self.workspace})

    def post(self, request, workspace_slug: str):
        form = ListForm(request.POST)
        if not form.is_valid():
            return render(request, "lists/list_form.html", {"form": form, "workspace": self.workspace})

        lst = form.save(commit=False)
        lst.workspace = self.workspace
        lst.created_by = request.user
        lst.save()

        return redirect("lists:list_detail", workspace_slug=self.workspace.slug, list_id=lst.id)


class ListUpdateView(WorkspaceContextMixin, View):
    def get(self, request, workspace_slug: str, list_id: str):
        lst = get_object_or_404(List, id=list_id, workspace=self.workspace)
        form = ListForm(instance=lst)
        return render(request, "lists/list_form.html", {"form": form, "workspace": self.workspace, "list": lst})

    def post(self, request, workspace_slug: str, list_id: str):
        lst = get_object_or_404(List, id=list_id, workspace=self.workspace)
        form = ListForm(request.POST, instance=lst)
        if not form.is_valid():
            return render(request, "lists/list_form.html", {"form": form, "workspace": self.workspace, "list": lst})

        form.save()
        return redirect("lists:list_detail", workspace_slug=self.workspace.slug, list_id=lst.id)


class ListDeleteView(WorkspaceContextMixin, View):
    def post(self, request, workspace_slug: str, list_id: str):
        lst = get_object_or_404(List, id=list_id, workspace=self.workspace)
        lst.delete()
        return redirect("lists:list_index", workspace_slug=self.workspace.slug)


class ListDetailView(WorkspaceContextMixin, View):
    def get(self, request, workspace_slug: str, list_id: str):
        lst = get_object_or_404(List, id=list_id, workspace=self.workspace)
        items = lst.items.select_related("checked_by").all()
        return render(
            request,
            "lists/list_detail.html",
            {
                "workspace": self.workspace,
                "list": lst,
                "items": items,
                "item_form": ListItemForm(),
            },
        )


class ListItemCreateView(WorkspaceContextMixin, View):
    def post(self, request, workspace_slug: str, list_id: str):
        lst = get_object_or_404(List, id=list_id, workspace=self.workspace)
        form = ListItemForm(request.POST)

        if not form.is_valid():
            # Re-render the whole list detail page for now (simple MVP)
            items = lst.items.select_related("checked_by").all()
            return render(
                request,
                "lists/list_detail.html",
                {
                    "workspace": self.workspace,
                    "list": lst,
                    "items": items,
                    "item_form": form,
                },
            )

        item = form.save(commit=False)
        item.list = lst
        item.save()

        # HTMX: return only the new row so it can be appended
        return render(
            request,
            "lists/partials/item_row.html",
            {"workspace": self.workspace, "list": lst, "item": item},
        )


class ListItemToggleCheckedView(WorkspaceContextMixin, View):
    def post(self, request, workspace_slug: str, list_id: str, item_id: str):
        lst = get_object_or_404(List, id=list_id, workspace=self.workspace)
        item = get_object_or_404(ListItem, id=item_id, list=lst)

        item.is_checked = not item.is_checked
        if item.is_checked:
            item.checked_by = request.user
            item.checked_at = timezone.now()
        else:
            item.checked_by = None
            item.checked_at = None

        item.save(update_fields=["is_checked", "checked_by", "checked_at", "updated_at"])

        return render(
            request,
            "lists/partials/item_row.html",
            {"workspace": self.workspace, "list": lst, "item": item},
        )


class ListItemEditView(WorkspaceContextMixin, View):
    def get(self, request, workspace_slug: str, list_id: str, item_id: str):
        lst = get_object_or_404(List, id=list_id, workspace=self.workspace)
        item = get_object_or_404(ListItem, id=item_id, list=lst)
        form = ListItemForm(instance=item)
        return render(
            request,
            "lists/partials/item_edit_form.html",
            {"workspace": self.workspace, "list": lst, "item": item, "form": form},
        )


class ListItemUpdateView(WorkspaceContextMixin, View):
    def post(self, request, workspace_slug: str, list_id: str, item_id: str):
        lst = get_object_or_404(List, id=list_id, workspace=self.workspace)
        item = get_object_or_404(ListItem, id=item_id, list=lst)
        form = ListItemForm(request.POST, instance=item)

        if not form.is_valid():
            return render(
                request,
                "lists/partials/item_edit_form.html",
                {"workspace": self.workspace, "list": lst, "item": item, "form": form},
            )

        item = form.save()
        return render(
            request,
            "lists/partials/item_row.html",
            {"workspace": self.workspace, "list": lst, "item": item},
        )


class ListItemDeleteView(WorkspaceContextMixin, View):
    def post(self, request, workspace_slug: str, list_id: str, item_id: str):
        lst = get_object_or_404(List, id=list_id, workspace=self.workspace)
        item = get_object_or_404(ListItem, id=item_id, list=lst)
        item.delete()
        return HttpResponse("")


class ListItemRowView(WorkspaceContextMixin, View):
    def get(self, request, workspace_slug: str, list_id: str, item_id: str):
        lst = get_object_or_404(List, id=list_id, workspace=self.workspace)
        item = get_object_or_404(ListItem, id=item_id, list=lst)

        return render(
            request,
            "lists/partials/item_row.html",
            {"workspace": self.workspace, "list": lst, "item": item},
        )


