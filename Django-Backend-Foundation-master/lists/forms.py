from django import forms
from .models import List, ListItem


class ListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ["name", "description"]


class ListItemForm(forms.ModelForm):
    class Meta:
        model = ListItem
        fields = ["text"]
