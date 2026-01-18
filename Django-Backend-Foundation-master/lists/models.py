from django.conf import settings
from django.db import models

from core.models import UUIDModel
from workspaces.models import Workspace


class List(UUIDModel):
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="lists",
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="lists_created",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "created_at"]

    def __str__(self) -> str:
        return self.name


class ListItem(UUIDModel):
    list = models.ForeignKey(
        List,
        on_delete=models.CASCADE,
        related_name="items",
    )
    text = models.CharField(max_length=200)

    is_checked = models.BooleanField(default=False)
    checked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="list_items_checked",
    )
    checked_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return self.text
