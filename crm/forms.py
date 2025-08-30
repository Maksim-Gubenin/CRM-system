from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _


class LoginForm(AuthenticationForm):
    """
    Custom login form that extends Django's AuthenticationForm.

    Provides styled form fields with Bootstrap classes and internationalized
    placeholders for username and password inputs.

    Inherits all validation and authentication logic from AuthenticationForm
    while adding custom UI enhancements.
    """

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("Username")}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": _("Password")}
        )
    )
