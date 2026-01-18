from django import forms
from django.contrib.auth import get_user_model

from .models import Workspace, WorkspaceMembership

User = get_user_model()


class WorkspaceCreateForm(forms.ModelForm):
    class Meta:
        model = Workspace
        fields = ["name"]

class WorkspaceUpdateForm(forms.ModelForm):
    class Meta:
        model = Workspace
        fields = ["name"]


class AddMemberForm(forms.Form):
    identifier = forms.CharField(
        label="Username or email",
        max_length=150,
        help_text="Add an existing user to this workspace.",
    )
    role = forms.ChoiceField(choices=WorkspaceMembership.Role.choices, initial=WorkspaceMembership.Role.MEMBER)

    def clean_identifier(self):
        ident = self.cleaned_data["identifier"].strip()
        if not ident:
            raise forms.ValidationError("Enter a username or email.")
        return ident

    def get_user(self) -> User:
        ident = self.cleaned_data["identifier"]
        qs = User.objects.all()
        user = qs.filter(username__iexact=ident).first() or qs.filter(email__iexact=ident).first()
        if not user:
            raise forms.ValidationError("No user found with that username/email.")
        return user
