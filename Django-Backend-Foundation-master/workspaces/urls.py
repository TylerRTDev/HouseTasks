from django.urls import path
from .views import WorkspaceChooserView, WorkspaceCreateView, WorkspaceMembersView, WorkspaceSettingsView, WorkspaceDeleteView

app_name = "workspaces"

urlpatterns = [
    path("", WorkspaceChooserView.as_view(), name="chooser"),
    path("new/", WorkspaceCreateView.as_view(), name="create"),
    path("w/<slug:workspace_slug>/members/", WorkspaceMembersView.as_view(), name="members"),
    path("w/<slug:workspace_slug>/settings/", WorkspaceSettingsView.as_view(), name="settings"),
    path("w/<slug:workspace_slug>/delete/", WorkspaceDeleteView.as_view(), name="delete"),
]
