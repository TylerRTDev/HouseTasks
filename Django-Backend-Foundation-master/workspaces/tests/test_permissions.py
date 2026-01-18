from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from workspaces.models import Workspace, WorkspaceMembership

User = get_user_model()


class WorkspaceAccessTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pass12345")
        self.other = User.objects.create_user(username="other", password="pass12345")

        self.ws = Workspace.objects.create(name="My Space", created_by=self.owner)
        WorkspaceMembership.objects.create(workspace=self.ws, user=self.owner, role=WorkspaceMembership.Role.OWNER)

    def test_non_member_cannot_view_members_page(self):
        self.client.login(username="other", password="pass12345")
        url = reverse("workspaces:members", kwargs={"workspace_slug": self.ws.slug})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_owner_can_view_members_page(self):
        self.client.login(username="owner", password="pass12345")
        url = reverse("workspaces:members", kwargs={"workspace_slug": self.ws.slug})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
