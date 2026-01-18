from django.urls import path
from .views import (
    ListIndexView,
    ListCreateView,
    ListDetailView,
    ListUpdateView,
    ListDeleteView,
    ListItemCreateView,
    ListItemToggleCheckedView,
    ListItemEditView,
    ListItemUpdateView,
    ListItemDeleteView,
    ListItemRowView,
)

app_name = "lists"

urlpatterns = [
    path("", ListIndexView.as_view(), name="list_index"),
    path("new/", ListCreateView.as_view(), name="list_create"),
    path("<uuid:list_id>/", ListDetailView.as_view(), name="list_detail"),

    # List edit/delete
    path("<uuid:list_id>/edit/", ListUpdateView.as_view(), name="list_edit"),
    path("<uuid:list_id>/delete/", ListDeleteView.as_view(), name="list_delete"),

    # Items
    path("<uuid:list_id>/items/create/", ListItemCreateView.as_view(), name="item_create"),
    path("<uuid:list_id>/items/<uuid:item_id>/toggle/", ListItemToggleCheckedView.as_view(), name="item_toggle"),
    path("<uuid:list_id>/items/<uuid:item_id>/row/", ListItemRowView.as_view(), name="item_row"),


    # Item edit/delete (HTMX)
    path("<uuid:list_id>/items/<uuid:item_id>/edit/", ListItemEditView.as_view(), name="item_edit"),
    path("<uuid:list_id>/items/<uuid:item_id>/update/", ListItemUpdateView.as_view(), name="item_update"),
    path("<uuid:list_id>/items/<uuid:item_id>/delete/", ListItemDeleteView.as_view(), name="item_delete"),
]
